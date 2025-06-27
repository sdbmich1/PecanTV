"""
API routes for subscription management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import stripe
import os

from database import get_db
from models import User
from subscription_models import SubscriptionPlan, UserSubscription, SubscriptionHistory
from subscription_schemas import (
    SubscriptionPlanResponse, UserSubscriptionResponse, SubscriptionStatusResponse,
    CreateSubscriptionRequest, CancelSubscriptionRequest, UpdateSubscriptionRequest,
    PaymentIntentResponse, CustomerResponse
)
from stripe_client import stripe_client, DEFAULT_PLANS

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# Dependency to get current user (you'll need to implement this)
def get_current_user(db: Session = Depends(get_db), token: str = None):
    """Get current authenticated user."""
    # This is a placeholder - implement your authentication logic
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Decode token and get user
    # user = decode_token_and_get_user(token, db)
    # return user
    
    # For now, return a mock user
    return db.query(User).first()

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(db: Session = Depends(get_db)):
    """Get all available subscription plans."""
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return plans

@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription status."""
    # Get active subscription
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id,
        UserSubscription.status == "active"
    ).first()
    
    # Get plan details
    current_plan = None
    if subscription:
        current_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription.plan_id
        ).first()
    
    # Check if user can access premium content
    can_access_premium = subscription is not None and subscription.status == "active"
    
    # Calculate remaining free episodes (for free tier)
    remaining_free_episodes = None
    if not can_access_premium:
        # Implement logic to track free episode usage
        remaining_free_episodes = 3  # Placeholder
    
    return SubscriptionStatusResponse(
        has_active_subscription=can_access_premium,
        current_plan=current_plan,
        subscription=subscription,
        can_access_premium=can_access_premium,
        remaining_free_episodes=remaining_free_episodes,
        max_devices=current_plan.max_devices if current_plan else 1,
        max_quality=current_plan.max_quality if current_plan else "480p"
    )

@router.post("/create", response_model=UserSubscriptionResponse)
async def create_subscription(
    request: CreateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new subscription for the current user."""
    # Get the plan
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == request.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check if user already has an active subscription
    existing_subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id,
        UserSubscription.status == "active"
    ).first()
    
    if existing_subscription:
        raise HTTPException(status_code=400, detail="User already has an active subscription")
    
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe_client.create_customer(
                email=current_user.email,
                name=current_user.name
            )
            current_user.stripe_customer_id = customer.id
            db.commit()
        
        # Create Stripe subscription
        stripe_subscription = stripe_client.create_subscription(
            customer_id=current_user.stripe_customer_id,
            price_id=plan.stripe_price_id,
            trial_days=request.trial_days
        )
        
        # Create subscription record
        subscription = UserSubscription(
            user_id=current_user.id,
            plan_id=plan.id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=current_user.stripe_customer_id,
            status=stripe_subscription.status,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")

@router.post("/cancel", response_model=UserSubscriptionResponse)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel the current user's subscription."""
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id,
        UserSubscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    try:
        # Cancel in Stripe
        stripe_subscription = stripe_client.cancel_subscription(
            subscription_id=subscription.stripe_subscription_id,
            at_period_end=request.at_period_end
        )
        
        # Update local record
        subscription.status = stripe_subscription.status
        subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end
        
        # Add to history
        history = SubscriptionHistory(
            user_id=current_user.id,
            subscription_id=subscription.id,
            event_type="canceled",
            event_data={"cancel_at_period_end": request.at_period_end}
        )
        
        db.add(history)
        db.commit()
        db.refresh(subscription)
        
        return subscription
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")

@router.post("/update", response_model=UserSubscriptionResponse)
async def update_subscription(
    request: UpdateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the current user's subscription to a different plan."""
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id,
        UserSubscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    # Get the new plan
    new_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == request.plan_id).first()
    if not new_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    try:
        # Update in Stripe
        stripe_subscription = stripe_client.update_subscription(
            subscription_id=subscription.stripe_subscription_id,
            price_id=new_plan.stripe_price_id
        )
        
        # Update local record
        subscription.plan_id = new_plan.id
        subscription.status = stripe_subscription.status
        subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
        subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        
        # Add to history
        history = SubscriptionHistory(
            user_id=current_user.id,
            subscription_id=subscription.id,
            event_type="updated",
            event_data={"new_plan_id": new_plan.id}
        )
        
        db.add(history)
        db.commit()
        db.refresh(subscription)
        
        return subscription
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")

@router.get("/history", response_model=List[SubscriptionHistoryResponse])
async def get_subscription_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subscription history for the current user."""
    history = db.query(SubscriptionHistory).filter(
        SubscriptionHistory.user_id == current_user.id
    ).order_by(SubscriptionHistory.created_at.desc()).all()
    
    return history

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        event = stripe_client.verify_webhook_signature(payload, sig_header, webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")
    
    # Handle different event types
    if event["type"] == "customer.subscription.updated":
        await handle_subscription_updated(event, db)
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_deleted(event, db)
    elif event["type"] == "invoice.payment_succeeded":
        await handle_payment_succeeded(event, db)
    elif event["type"] == "invoice.payment_failed":
        await handle_payment_failed(event, db)
    
    return {"status": "success"}

async def handle_subscription_updated(event: dict, db: Session):
    """Handle subscription updated webhook."""
    subscription_data = event["data"]["object"]
    
    # Update local subscription record
    subscription = db.query(UserSubscription).filter(
        UserSubscription.stripe_subscription_id == subscription_data["id"]
    ).first()
    
    if subscription:
        subscription.status = subscription_data["status"]
        subscription.current_period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
        subscription.current_period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
        subscription.cancel_at_period_end = subscription_data["cancel_at_period_end"]
        
        # Add to history
        history = SubscriptionHistory(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            event_type="updated",
            event_data=subscription_data,
            stripe_event_id=event["id"]
        )
        
        db.add(history)
        db.commit()

async def handle_subscription_deleted(event: dict, db: Session):
    """Handle subscription deleted webhook."""
    subscription_data = event["data"]["object"]
    
    subscription = db.query(UserSubscription).filter(
        UserSubscription.stripe_subscription_id == subscription_data["id"]
    ).first()
    
    if subscription:
        subscription.status = "canceled"
        
        # Add to history
        history = SubscriptionHistory(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            event_type="deleted",
            event_data=subscription_data,
            stripe_event_id=event["id"]
        )
        
        db.add(history)
        db.commit()

async def handle_payment_succeeded(event: dict, db: Session):
    """Handle payment succeeded webhook."""
    invoice_data = event["data"]["object"]
    
    # Find subscription by invoice
    subscription = db.query(UserSubscription).filter(
        UserSubscription.stripe_subscription_id == invoice_data["subscription"]
    ).first()
    
    if subscription:
        # Add to history
        history = SubscriptionHistory(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            event_type="payment_succeeded",
            event_data=invoice_data,
            stripe_event_id=event["id"]
        )
        
        db.add(history)
        db.commit()

async def handle_payment_failed(event: dict, db: Session):
    """Handle payment failed webhook."""
    invoice_data = event["data"]["object"]
    
    subscription = db.query(UserSubscription).filter(
        UserSubscription.stripe_subscription_id == invoice_data["subscription"]
    ).first()
    
    if subscription:
        subscription.status = "past_due"
        
        # Add to history
        history = SubscriptionHistory(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            event_type="payment_failed",
            event_data=invoice_data,
            stripe_event_id=event["id"]
        )
        
        db.add(history)
        db.commit() 