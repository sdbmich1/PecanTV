"""
Enhanced Authentication service with advanced security features for PecanTV.
Includes password strength validation, account lockout, session management, and security monitoring.
"""

import os
import jwt
import re
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
import logging

from models import User
from subscription_models import UserSubscription, SubscriptionPlan
from stripe_client import stripe_client
import schemas

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing with stronger configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased from default 12 for better security
)

# JWT Configuration with better security
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGITS = True
PASSWORD_REQUIRE_SPECIAL = True

class PasswordValidator:
    """Password strength validation"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return detailed feedback"""
        errors = []
        warnings = []
        
        # Check length
        if len(password) < PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
        
        # Check for uppercase letters
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letters
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digits
        if PASSWORD_REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        # Check for special characters
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            warnings.append("Password contains repeated characters")
        
        if re.search(r'(123|abc|qwe|password|admin)', password.lower()):
            warnings.append("Password contains common patterns")
        
        # Calculate strength score
        score = 0
        if len(password) >= 8: score += 1
        if re.search(r'[A-Z]', password): score += 1
        if re.search(r'[a-z]', password): score += 1
        if re.search(r'\d', password): score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 1
        if len(password) >= 12: score += 1
        
        strength = "weak" if score < 3 else "medium" if score < 5 else "strong"
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "strength": strength,
            "score": score
        }

class AccountLockoutManager:
    """Manage account lockout functionality"""
    
    def __init__(self):
        self.failed_attempts = {}  # IP -> {count: int, locked_until: datetime}
    
    def record_failed_attempt(self, ip_address: str) -> Dict[str, Any]:
        """Record a failed login attempt and check if account should be locked"""
        now = datetime.now(timezone.utc)
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = {"count": 0, "locked_until": None}
        
        record = self.failed_attempts[ip_address]
        
        # Check if currently locked
        if record["locked_until"] and now < record["locked_until"]:
            remaining_time = (record["locked_until"] - now).total_seconds()
            return {
                "locked": True,
                "remaining_seconds": int(remaining_time),
                "attempts_remaining": 0
            }
        
        # Reset if lockout period has expired
        if record["locked_until"] and now >= record["locked_until"]:
            record["count"] = 0
            record["locked_until"] = None
        
        # Increment failed attempts
        record["count"] += 1
        
        # Check if should be locked
        if record["count"] >= MAX_LOGIN_ATTEMPTS:
            record["locked_until"] = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            return {
                "locked": True,
                "remaining_seconds": LOCKOUT_DURATION_MINUTES * 60,
                "attempts_remaining": 0
            }
        
        return {
            "locked": False,
            "remaining_seconds": 0,
            "attempts_remaining": MAX_LOGIN_ATTEMPTS - record["count"]
        }
    
    def reset_failed_attempts(self, ip_address: str):
        """Reset failed attempts for successful login"""
        if ip_address in self.failed_attempts:
            self.failed_attempts[ip_address] = {"count": 0, "locked_until": None}

class SessionManager:
    """Manage user sessions and tokens"""
    
    def __init__(self):
        self.active_sessions = {}  # user_id -> List[Dict]
    
    def create_session(self, user_id: int, request: Request) -> Dict[str, Any]:
        """Create a new session for a user"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc)
        }
        
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = []
        
        self.active_sessions[user_id].append(session_data)
        
        # Limit sessions per user (keep only 5 most recent)
        if len(self.active_sessions[user_id]) > 5:
            self.active_sessions[user_id] = self.active_sessions[user_id][-5:]
        
        return session_data
    
    def validate_session(self, user_id: int, session_id: str) -> bool:
        """Validate if a session is still active"""
        if user_id not in self.active_sessions:
            return False
        
        for session in self.active_sessions[user_id]:
            if session["session_id"] == session_id:
                # Update last activity
                session["last_activity"] = datetime.now(timezone.utc)
                return True
        
        return False
    
    def invalidate_session(self, user_id: int, session_id: str):
        """Invalidate a specific session"""
        if user_id in self.active_sessions:
            self.active_sessions[user_id] = [
                s for s in self.active_sessions[user_id] 
                if s["session_id"] != session_id
            ]
    
    def invalidate_all_sessions(self, user_id: int):
        """Invalidate all sessions for a user"""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"

class EnhancedAuthService:
    """Enhanced authentication service with advanced security features"""
    
    def __init__(self):
        self.lockout_manager = AccountLockoutManager()
        self.session_manager = SessionManager()
    
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
        """Create a JWT access token with enhanced security."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add additional security claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": "pecantv-api",
            "aud": "pecantv-users"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": "pecantv-api",
            "aud": "pecantv-users",
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token with enhanced validation."""
        try:
            payload = jwt.decode(
                token, 
                SECRET_KEY, 
                algorithms=[ALGORITHM],
                issuer="pecantv-api",
                audience="pecantv-users"
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidIssuerError:
            logger.warning("Invalid token issuer")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except jwt.InvalidAudienceError:
            logger.warning("Invalid token audience")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except jwt.JWTError as e:
            logger.warning(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def login_user_secure(self, db: Session, login_data: schemas.UserLogin, request: Request) -> schemas.AuthResponse:
        """Login user with enhanced security features."""
        client_ip = self._get_client_ip(request)
        
        # Check for account lockout
        lockout_status = self.lockout_manager.record_failed_attempt(client_ip)
        if lockout_status["locked"]:
            logger.warning(f"Login attempt blocked due to lockout for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account temporarily locked. Try again in {lockout_status['remaining_seconds']} seconds."
            )
        
        # Authenticate user
        user = self.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            logger.warning(f"Failed login attempt for email: {login_data.email} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid email or password. {lockout_status['attempts_remaining']} attempts remaining."
            )
        
        # Reset failed attempts on successful login
        self.lockout_manager.reset_failed_attempts(client_ip)
        
        # Create session
        session_data = self.session_manager.create_session(user.id, request)
        
        # Get subscription status
        subscription_status = self.get_user_subscription_status(db, user.id)
        
        # Create tokens
        access_token = self.create_access_token(
            data={
                "sub": str(user.uuid), 
                "user_id": user.id,
                "session_id": session_data["session_id"]
            }
        )
        
        refresh_token = self.create_refresh_token(
            data={
                "sub": str(user.uuid),
                "user_id": user.id,
                "session_id": session_data["session_id"]
            }
        )
        
        logger.info(f"Successful login for user: {user.email} from IP: {client_ip}")
        
        return schemas.AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=schemas.UserWithSubscription(
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
        )
    
    def register_user_secure(self, db: Session, user_data: schemas.UserCreate, request: Request) -> schemas.AuthResponse:
        """Register user with enhanced security validation."""
        # Validate password strength
        password_validation = PasswordValidator.validate_password_strength(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "errors": password_validation["errors"],
                    "warnings": password_validation["warnings"]
                }
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user with enhanced security
        user = self.create_user_with_stripe_customer(db, user_data)
        
        # Create session
        session_data = self.session_manager.create_session(user.id, request)
        
        # Get subscription status
        subscription_status = self.get_user_subscription_status(db, user.id)
        
        # Create tokens
        access_token = self.create_access_token(
            data={
                "sub": str(user.uuid), 
                "user_id": user.id,
                "session_id": session_data["session_id"]
            }
        )
        
        refresh_token = self.create_refresh_token(
            data={
                "sub": str(user.uuid),
                "user_id": user.id,
                "session_id": session_data["session_id"]
            }
        )
        
        logger.info(f"New user registered: {user.email}")
        
        return schemas.AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=schemas.UserWithSubscription(
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
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    # Include other methods from the original AuthService
    @staticmethod
    def get_user_subscription_status(db: Session, user_id: int) -> Dict[str, Any]:
        """Get user's subscription status and details."""
        # Implementation from original AuthService
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
                "remaining_free_episodes": 3
            }
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription.plan_id
        ).first()
        
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
        # Implementation from original AuthService
        try:
            stripe_customer = stripe_client.create_customer(
                email=user_data.email,
                name=f"{user_data.first_name} {user_data.last_name}".strip() if user_data.first_name else None,
                metadata={"source": "pecantv_signup"}
            )
        except Exception as e:
            print(f"Failed to create Stripe customer: {e}")
            stripe_customer = None
        
        hashed_password = EnhancedAuthService.get_password_hash(user_data.password)
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
        if not EnhancedAuthService.verify_password(password, user.password_hash):
            return None
        return user

# Global instance
enhanced_auth_service = EnhancedAuthService() 