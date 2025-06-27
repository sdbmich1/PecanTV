"""
Pydantic schemas for subscription API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class SubscriptionPlanBase(BaseModel):
    """Base subscription plan schema."""
    name: str = Field(..., description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    price: float = Field(..., description="Plan price")
    currency: str = Field(default="USD", description="Currency")
    interval: str = Field(default="month", description="Billing interval")
    features: Dict[str, Any] = Field(..., description="Plan features")
    max_devices: int = Field(default=1, description="Maximum devices")
    max_quality: str = Field(default="720p", description="Maximum quality")

class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan."""
    stripe_product_id: Optional[str] = Field(None, description="Stripe product ID")
    stripe_price_id: Optional[str] = Field(None, description="Stripe price ID")

class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Schema for subscription plan response."""
    id: int
    uuid: UUID
    stripe_product_id: Optional[str]
    stripe_price_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserSubscriptionBase(BaseModel):
    """Base user subscription schema."""
    plan_id: int = Field(..., description="Plan ID")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")

class UserSubscriptionCreate(UserSubscriptionBase):
    """Schema for creating a user subscription."""
    pass

class UserSubscriptionResponse(UserSubscriptionBase):
    """Schema for user subscription response."""
    id: int
    uuid: UUID
    user_id: int
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    trial_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    plan: SubscriptionPlanResponse
    
    class Config:
        from_attributes = True

class SubscriptionHistoryBase(BaseModel):
    """Base subscription history schema."""
    event_type: str = Field(..., description="Event type")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event data")
    stripe_event_id: Optional[str] = Field(None, description="Stripe event ID")

class SubscriptionHistoryResponse(SubscriptionHistoryBase):
    """Schema for subscription history response."""
    id: int
    uuid: UUID
    user_id: int
    subscription_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CreateSubscriptionRequest(BaseModel):
    """Schema for creating a subscription request."""
    plan_id: int = Field(..., description="Plan ID to subscribe to")
    payment_method_id: Optional[str] = Field(None, description="Stripe payment method ID")
    trial_days: int = Field(default=0, description="Trial period in days")

class CancelSubscriptionRequest(BaseModel):
    """Schema for canceling a subscription request."""
    at_period_end: bool = Field(default=True, description="Cancel at period end")

class UpdateSubscriptionRequest(BaseModel):
    """Schema for updating a subscription request."""
    plan_id: int = Field(..., description="New plan ID")

class SubscriptionStatusResponse(BaseModel):
    """Schema for subscription status response."""
    has_active_subscription: bool
    current_plan: Optional[SubscriptionPlanResponse]
    subscription: Optional[UserSubscriptionResponse]
    can_access_premium: bool
    remaining_free_episodes: Optional[int]
    max_devices: int
    max_quality: str

class StripeWebhookEvent(BaseModel):
    """Schema for Stripe webhook events."""
    id: str
    object: str
    api_version: str
    created: int
    data: Dict[str, Any]
    livemode: bool
    pending_webhooks: int
    request: Dict[str, Any]
    type: str

class PaymentIntentResponse(BaseModel):
    """Schema for payment intent response."""
    id: str
    amount: int
    currency: str
    status: str
    client_secret: str
    customer: Optional[str]

class CustomerResponse(BaseModel):
    """Schema for customer response."""
    id: str
    email: str
    name: Optional[str]
    created: int
    subscriptions: List[Dict[str, Any]] 