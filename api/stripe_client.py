"""
Stripe client configuration and helper functions for PecanTV subscriptions.
"""

import os
import stripe
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeClient:
    """Stripe client for handling subscriptions and payments."""
    
    def __init__(self):
        self.stripe = stripe
        
    def create_customer(self, email: str, name: str = None, metadata: dict = None):
        """Create a new Stripe customer."""
        try:
            customer_data = {
                "email": email,
                "metadata": metadata or {}
            }
            if name:
                customer_data["name"] = name
            
            customer = self.stripe.Customer.create(**customer_data)
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    def create_subscription(self, customer_id: str, price_id: str, trial_days: int = None):
        """Create a new Stripe subscription."""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"]
            }
            
            if trial_days:
                subscription_data["trial_period_days"] = trial_days
            
            subscription = self.stripe.Subscription.create(**subscription_data)
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe subscription: {str(e)}")
    
    def update_subscription(self, subscription_id: str, price_id: str):
        """Update an existing Stripe subscription."""
        try:
            subscription = self.stripe.Subscription.modify(
                subscription_id,
                items=[{"id": subscription.items.data[0].id, "price": price_id}]
            )
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to update Stripe subscription: {str(e)}")
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True):
        """Cancel a Stripe subscription."""
        try:
            if at_period_end:
                subscription = self.stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = self.stripe.Subscription.cancel(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel Stripe subscription: {str(e)}")
    
    def get_subscription(self, subscription_id: str):
        """Retrieve a Stripe subscription."""
        try:
            return self.stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve Stripe subscription: {str(e)}")
    
    def update_subscription_price(self, subscription_id: str, new_price_id: str):
        """Update subscription price."""
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            self.stripe.SubscriptionItem.modify(
                subscription.items.data[0].id,
                price=new_price_id
            )
            return self.stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to update subscription price: {str(e)}")
    
    def get_subscription_by_id(self, subscription_id: str):
        """Get subscription by ID."""
        try:
            return self.stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to get subscription: {str(e)}")
    
    def list_customer_subscriptions(self, customer_id: str):
        """List all subscriptions for a customer."""
        try:
            subscriptions = self.stripe.Subscription.list(customer=customer_id)
            return subscriptions.data
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to list customer subscriptions: {str(e)}")
    
    def create_payment_intent(self, amount: int, currency: str = "usd", customer_id: str = None, metadata: dict = None):
        """Create a payment intent for one-time payments."""
        try:
            payment_intent_data = {
                "amount": amount,
                "currency": currency,
                "metadata": metadata or {}
            }
            if customer_id:
                payment_intent_data["customer"] = customer_id
            
            return self.stripe.PaymentIntent.create(**payment_intent_data)
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    def verify_webhook_signature(self, payload: bytes, sig_header: str, webhook_secret: str):
        """Verify webhook signature."""
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            raise Exception(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {str(e)}")

# Default subscription plans configuration
DEFAULT_PLANS = [
    {
        "name": "Free",
        "description": "Limited access to basic content",
        "price": 0.00,
        "features": {
            "episodes_per_month": 3,
            "quality": "480p",
            "ads": True,
            "devices": 1,
            "downloads": False
        },
        "max_devices": 1,
        "max_quality": "480p"
    },
    {
        "name": "Basic",
        "description": "Unlimited episodes with no ads",
        "price": 9.99,
        "features": {
            "episodes_per_month": -1,
            "quality": "720p",
            "ads": False,
            "devices": 1,
            "downloads": False
        },
        "max_devices": 1,
        "max_quality": "720p"
    },
    {
        "name": "Premium",
        "description": "High quality streaming with downloads",
        "price": 14.99,
        "features": {
            "episodes_per_month": -1,
            "quality": "1080p",
            "ads": False,
            "devices": 2,
            "downloads": True
        },
        "max_devices": 2,
        "max_quality": "1080p"
    },
    {
        "name": "Family",
        "description": "Perfect for the whole family",
        "price": 19.99,
        "features": {
            "episodes_per_month": -1,
            "quality": "1080p",
            "ads": False,
            "devices": 4,
            "downloads": True,
            "parental_controls": True,
            "family_profiles": True
        },
        "max_devices": 4,
        "max_quality": "1080p"
    }
]

# Initialize Stripe client
stripe_client = StripeClient() 