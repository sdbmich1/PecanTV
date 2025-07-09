#!/usr/bin/env python3
"""
Test script to verify Stripe connection and configuration.
"""

import os
from dotenv import load_dotenv
import stripe

# Load environment variables
load_dotenv()

def test_stripe_connection():
    """Test Stripe API connection."""
    print("🧪 Testing Stripe Connection...")
    print("=" * 50)
    
    # Check if environment variables are loaded
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
    
    if not stripe_secret_key:
        print("❌ STRIPE_SECRET_KEY not found in environment variables")
        return False
    
    if not stripe_publishable_key:
        print("❌ STRIPE_PUBLISHABLE_KEY not found in environment variables")
        return False
    
    print(f"✅ Stripe Secret Key: {stripe_secret_key[:20]}...")
    print(f"✅ Stripe Publishable Key: {stripe_publishable_key[:20]}...")
    
    # Configure Stripe
    stripe.api_key = stripe_secret_key
    
    try:
        # Test API connection by retrieving account information
        account = stripe.Account.retrieve()
        print(f"✅ Stripe Account: {account.business_profile.name or 'No business name set'}")
        print(f"✅ Account ID: {account.id}")
        print(f"✅ Country: {account.country}")
        print(f"✅ Charges Enabled: {account.charges_enabled}")
        print(f"✅ Payouts Enabled: {account.payouts_enabled}")
        
        # Test listing products
        products = stripe.Product.list(limit=5)
        print(f"✅ Found {len(products.data)} existing products")
        
        for product in products.data:
            print(f"   • {product.name} (ID: {product.id})")
        
        # Test listing prices
        prices = stripe.Price.list(limit=5)
        print(f"✅ Found {len(prices.data)} existing prices")
        
        for price in prices.data:
            print(f"   • {price.unit_amount/100} {price.currency.upper()} (ID: {price.id})")
        
        print("\n🎉 Stripe connection successful!")
        return True
        
    except stripe.error.AuthenticationError:
        print("❌ Authentication failed. Check your Stripe secret key.")
        return False
    except stripe.error.APIConnectionError:
        print("❌ Network error. Check your internet connection.")
        return False
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def check_environment():
    """Check environment configuration."""
    print("\n🔧 Environment Configuration:")
    print("=" * 30)
    
    env_vars = [
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY", 
        "STRIPE_WEBHOOK_SECRET",
        "DEBUG"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var and len(value) > 20:
                print(f"✅ {var}: {value[:20]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set")

if __name__ == "__main__":
    check_environment()
    success = test_stripe_connection()
    
    if success:
        print("\n🚀 Ready to proceed with subscription setup!")
        print("\nNext steps:")
        print("1. Create subscription products in Stripe dashboard")
        print("2. Run database migration: python create_subscription_tables.py")
        print("3. Test subscription endpoints")
    else:
        print("\n❌ Please fix Stripe configuration before proceeding.") 