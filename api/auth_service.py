"""
Authentication service with Stripe subscription integration for PecanTV.
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status

from models import User
from subscription_models import UserSubscription, SubscriptionPlan
from stripe_client import stripe_client
import schemas

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    """Authentication service with subscription integration."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    @staticmethod
    def get_user_subscription_status(db: Session, user_id: int) -> Dict[str, Any]:
        """Get user's subscription status and details."""
        # Get active subscription
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status.in_(["active", "trialing"])
        ).first()
        
        if not subscription:
            return {
                "has_active_subscription": False,
                "subscription_plan": None,
                "subscription_status": None,
                "subscription_expires": None,
                "can_access_premium": False,
                "remaining_free_episodes": 3  # Default free tier limit
            }
        
        # Get plan details
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription.plan_id
        ).first()
        
        # Check if subscription is still valid
        is_active = (
            subscription.status in ["active", "trialing"] and
            subscription.current_period_end and
            subscription.current_period_end > datetime.now(timezone.utc)
        )
        
        return {
            "has_active_subscription": is_active,
            "subscription_plan": plan.name if plan else None,
            "subscription_status": subscription.status,
            "subscription_expires": subscription.current_period_end,
            "can_access_premium": is_active,
            "remaining_free_episodes": None if is_active else 3
        }
    
    @staticmethod
    def create_user_with_stripe_customer(db: Session, user_data: schemas.UserCreate) -> User:
        """Create a new user and Stripe customer."""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        from enhanced_auth_service import PasswordValidator
        password_validation = PasswordValidator.validate_password_strength(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
            )
        
        # Create Stripe customer
        try:
            stripe_customer = stripe_client.create_customer(
                email=user_data.email,
                name=f"{user_data.first_name} {user_data.last_name}".strip() if user_data.first_name else None,
                metadata={"source": "pecantv_signup"}
            )
        except Exception as e:
            # If Stripe fails, still create the user but without customer ID
            print(f"Failed to create Stripe customer: {e}")
            stripe_customer = None
        
        # Create user
        hashed_password = AuthService.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            stripe_customer_id=stripe_customer.id if stripe_customer else None
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def login_user(db: Session, login_data: schemas.UserLogin) -> schemas.AuthResponse:
        """Login user and return authentication response with subscription status."""
        # Authenticate user
        user = AuthService.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get subscription status
        subscription_status = AuthService.get_user_subscription_status(db, user.id)
        
        # Create user with subscription info
        user_with_subscription = schemas.UserWithSubscription(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            stripe_customer_id=user.stripe_customer_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
            **subscription_status
        )
        
        # Create access token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.uuid), "user_id": user.id}
        )
        
        # Get subscription plans if user doesn't have active subscription
        subscription_plans = None
        if not subscription_status["has_active_subscription"]:
            plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
            subscription_plans = [
                {
                    "id": plan.id,
                    "name": plan.name,
                    "description": plan.description,
                    "price": plan.price,
                    "currency": plan.currency,
                    "interval": plan.interval,
                    "features": plan.features,
                    "stripe_price_id": plan.stripe_price_id
                }
                for plan in plans
            ]
        
        return schemas.AuthResponse(
            user=user_with_subscription,
            access_token=access_token,
            subscription_required=not subscription_status["has_active_subscription"],
            subscription_plans=subscription_plans
        )
    
    @staticmethod
    def register_user(db: Session, user_data: schemas.UserCreate) -> schemas.AuthResponse:
        """Register a new user and return authentication response."""
        # Create user with Stripe customer
        user = AuthService.create_user_with_stripe_customer(db, user_data)
        
        # Get subscription status (new users start with free tier)
        subscription_status = AuthService.get_user_subscription_status(db, user.id)
        
        # Create user with subscription info
        user_with_subscription = schemas.UserWithSubscription(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            stripe_customer_id=user.stripe_customer_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
            **subscription_status
        )
        
        # Create access token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.uuid), "user_id": user.id}
        )
        
        # Get subscription plans for new user
        plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
        subscription_plans = [
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "price": plan.price,
                "currency": plan.currency,
                "interval": plan.interval,
                "features": plan.features,
                "stripe_price_id": plan.stripe_price_id
            }
            for plan in plans
        ]
        
        return schemas.AuthResponse(
            user=user_with_subscription,
            access_token=access_token,
            subscription_required=True,  # New users need to choose a plan
            subscription_plans=subscription_plans
        )
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from JWT token."""
        payload = AuthService.verify_token(token)
        user_uuid = payload.get("sub")
        if user_uuid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = db.query(User).filter(User.uuid == user_uuid).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    @staticmethod
    def check_subscription_access(db: Session, user_id: int) -> bool:
        """Check if user has access to premium content."""
        subscription_status = AuthService.get_user_subscription_status(db, user_id)
        return subscription_status["can_access_premium"] 