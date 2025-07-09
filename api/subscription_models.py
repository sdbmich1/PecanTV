"""Subscription models for PecanTV Stripe integration."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    interval = Column(String, default="month")  # month, year
    features = Column(JSON)  # Store features as JSON
    stripe_product_id = Column(String)
    stripe_price_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    stripe_subscription_id = Column(String)
    stripe_customer_id = Column(String)
    status = Column(String, default="active")  # active, canceled, past_due, etc.
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship
    plan = relationship("SubscriptionPlan")

class SubscriptionHistory(Base):
    __tablename__ = "subscription_history"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"))
    event_type = Column(String, nullable=False)  # created, updated, canceled, etc.
    stripe_event_id = Column(String)
    event_data = Column(JSON)  # Store full event data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    subscription = relationship("UserSubscription")
