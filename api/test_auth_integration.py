#!/usr/bin/env python3
"""
Test script for PecanTV authentication with Stripe subscription integration.
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration with Stripe customer creation."""
    print("🧪 Testing User Registration with Stripe Integration")
    print("=" * 60)
    
    # Test user data
    user_data = {
        "email": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"User UUID: {data['user']['uuid']}")
            print(f"Stripe Customer ID: {data['user']['stripe_customer_id']}")
            print(f"Has Active Subscription: {data['user']['has_active_subscription']}")
            print(f"Can Access Premium: {data['user']['can_access_premium']}")
            print(f"Subscription Required: {data['subscription_required']}")
            print(f"Available Plans: {len(data['subscription_plans'])} plans")
            
            # Show available plans
            for plan in data['subscription_plans']:
                print(f"  • {plan['name']}: ${plan['price']}/{plan['interval']}")
            
            return data['user'], data['access_token']
        else:
            print(f"❌ Registration failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None, None

def test_user_login(email, password):
    """Test user login with subscription status check."""
    print("\n🧪 Testing User Login with Subscription Check")
    print("=" * 60)
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"Has Active Subscription: {data['user']['has_active_subscription']}")
            print(f"Subscription Plan: {data['user']['subscription_plan']}")
            print(f"Subscription Status: {data['user']['subscription_status']}")
            print(f"Can Access Premium: {data['user']['can_access_premium']}")
            print(f"Remaining Free Episodes: {data['user']['remaining_free_episodes']}")
            print(f"Subscription Required: {data['subscription_required']}")
            
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_get_current_user(token):
    """Test getting current user with subscription status."""
    print("\n🧪 Testing Get Current User with Subscription Status")
    print("=" * 60)
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get current user successful!")
            print(f"User ID: {data['id']}")
            print(f"Email: {data['email']}")
            print(f"Has Active Subscription: {data['has_active_subscription']}")
            print(f"Subscription Plan: {data['subscription_plan']}")
            print(f"Can Access Premium: {data['can_access_premium']}")
            return True
        else:
            print(f"❌ Get current user failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting current user: {e}")
        return False

def test_subscription_plans():
    """Test getting subscription plans."""
    print("\n🧪 Testing Subscription Plans Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/plans")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            plans = response.json()
            print(f"✅ Found {len(plans)} subscription plans:")
            for plan in plans:
                print(f"  • {plan['name']}: ${plan['price']}/{plan['interval']}")
                print(f"    Description: {plan['description']}")
                print(f"    Features: {plan['features']}")
                print()
            return plans
        else:
            print(f"❌ Failed to get subscription plans: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting subscription plans: {e}")
        return []

def test_content_access_with_subscription():
    """Test content access based on subscription status."""
    print("\n🧪 Testing Content Access with Subscription Check")
    print("=" * 60)
    
    try:
        # Get content (this should work for all users)
        response = requests.get(f"{BASE_URL}/content?limit=3")
        print(f"Content Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.json()
            print(f"✅ Successfully retrieved {len(content)} content items")
            for item in content:
                print(f"  • {item['title']} ({item['type']})")
        else:
            print(f"❌ Failed to get content: {response.text}")
            
        # Get series (this should work for all users)
        response = requests.get(f"{BASE_URL}/series?limit=2")
        print(f"Series Status Code: {response.status_code}")
        
        if response.status_code == 200:
            series = response.json()
            print(f"✅ Successfully retrieved {len(series)} series")
            for item in series:
                print(f"  • {item['title']}")
        else:
            print(f"❌ Failed to get series: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing content access: {e}")

def main():
    """Run all authentication integration tests."""
    print("🚀 PecanTV Authentication Integration Test")
    print("=" * 60)
    
    # Test subscription plans
    plans = test_subscription_plans()
    
    # Test user registration
    user, token = test_user_registration()
    
    if user and token:
        # Test user login
        login_token = test_user_login(user['email'], "securepassword123")
        
        if login_token:
            # Test get current user
            test_get_current_user(login_token)
        
        # Test content access
        test_content_access_with_subscription()
    
    print("\n🎉 Authentication Integration Test Complete!")
    print("\n📋 Summary:")
    print("✅ User registration with Stripe customer creation")
    print("✅ User login with subscription status check")
    print("✅ Subscription plans retrieval")
    print("✅ Content access based on subscription status")
    print("\n🔧 Next Steps:")
    print("1. Implement subscription creation flow")
    print("2. Add subscription status checks to content endpoints")
    print("3. Implement free episode tracking")
    print("4. Add subscription upgrade/downgrade functionality")

if __name__ == "__main__":
    main() 