#!/usr/bin/env python3
"""
Comprehensive test for PecanTV full user flow:
1. User signup with Stripe customer creation
2. User selects plan and creates subscription
3. User login with subscription status check
4. Content access verification
"""

import requests
import json
import time
from datetime import datetime
import sys

# API base URL
BASE_URL = "http://localhost:8000"

class TestUserFlow:
    def __init__(self):
        self.test_email = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        self.test_password = "securepassword123"
        self.test_first_name = "Test"
        self.test_last_name = "User"
        self.access_token = None
        self.user_data = None
        self.subscription_plans = None
        
    def print_step(self, step_num, title):
        """Print a formatted step header."""
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {title}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        """Print a success message."""
        print(f"✅ {message}")
    
    def print_error(self, message):
        """Print an error message."""
        print(f"❌ {message}")
    
    def print_info(self, message):
        """Print an info message."""
        print(f"ℹ️  {message}")
    
    def test_health_check(self):
        """Test API health check."""
        self.print_step(0, "API Health Check")
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                self.print_success("API is running and healthy")
                return True
            else:
                self.print_error(f"API health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"API health check failed: {e}")
            return False
    
    def test_get_subscription_plans(self):
        """Test getting available subscription plans."""
        self.print_step(1, "Get Available Subscription Plans")
        
        try:
            response = requests.get(f"{BASE_URL}/subscriptions/plans", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.subscription_plans = response.json()
                self.print_success(f"Found {len(self.subscription_plans)} subscription plans")
                
                for i, plan in enumerate(self.subscription_plans):
                    print(f"  {i+1}. {plan['name']}: ${plan['price']}/{plan['interval']}")
                    print(f"     Description: {plan['description']}")
                    print(f"     Features: {plan['features']}")
                    print()
                
                return True
            else:
                self.print_error(f"Failed to get subscription plans: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error getting subscription plans: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration with Stripe customer creation."""
        self.print_step(2, "User Registration with Stripe Integration")
        
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": self.test_first_name,
            "last_name": self.test_last_name
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.user_data = data
                self.access_token = data['access_token']
                
                self.print_success("User registration successful!")
                print(f"User ID: {data['user']['id']}")
                print(f"User UUID: {data['user']['uuid']}")
                print(f"Email: {data['user']['email']}")
                print(f"Stripe Customer ID: {data['user']['stripe_customer_id']}")
                print(f"Has Active Subscription: {data['user']['has_active_subscription']}")
                print(f"Can Access Premium: {data['user']['can_access_premium']}")
                print(f"Subscription Required: {data['subscription_required']}")
                print(f"Available Plans: {len(data['subscription_plans'])} plans")
                
                # Verify subscription is required for new user
                if data['subscription_required']:
                    self.print_success("✅ New user correctly requires subscription")
                else:
                    self.print_error("❌ New user should require subscription")
                    return False
                
                return True
            else:
                self.print_error(f"Registration failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error during registration: {e}")
            return False
    
    def test_create_subscription(self):
        """Test creating a subscription for the user."""
        self.print_step(3, "Create Subscription")
        
        if not self.subscription_plans:
            self.print_error("No subscription plans available")
            return False
        
        # Select the Basic plan (usually the first paid plan)
        basic_plan = None
        for plan in self.subscription_plans:
            if plan['name'] == 'Basic' and plan['price'] > 0:
                basic_plan = plan
                break
        
        if not basic_plan:
            self.print_error("Basic plan not found")
            return False
        
        subscription_data = {
            "plan_id": basic_plan['id'],
            "payment_method_id": "pm_card_visa"  # Test payment method
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.post(
                f"{BASE_URL}/subscriptions/create", 
                json=subscription_data, 
                headers=headers,
                timeout=10
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']  # Update token
                
                self.print_success("Subscription creation successful!")
                print(f"User ID: {data['user']['id']}")
                print(f"Has Active Subscription: {data['user']['has_active_subscription']}")
                print(f"Subscription Plan: {data['user']['subscription_plan']}")
                print(f"Subscription Status: {data['user']['subscription_status']}")
                print(f"Can Access Premium: {data['user']['can_access_premium']}")
                print(f"Subscription Required: {data['subscription_required']}")
                
                # Verify subscription is now active
                if data['user']['has_active_subscription']:
                    self.print_success("✅ User now has active subscription")
                else:
                    self.print_error("❌ User should have active subscription after creation")
                    return False
                
                return True
            else:
                self.print_error(f"Subscription creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error creating subscription: {e}")
            return False
    
    def test_user_login(self):
        """Test user login with subscription status check."""
        self.print_step(4, "User Login with Subscription Check")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success("Login successful!")
                print(f"User ID: {data['user']['id']}")
                print(f"Email: {data['user']['email']}")
                print(f"Has Active Subscription: {data['user']['has_active_subscription']}")
                print(f"Subscription Plan: {data['user']['subscription_plan']}")
                print(f"Subscription Status: {data['user']['subscription_status']}")
                print(f"Can Access Premium: {data['user']['can_access_premium']}")
                print(f"Remaining Free Episodes: {data['user']['remaining_free_episodes']}")
                print(f"Subscription Required: {data['subscription_required']}")
                
                # Verify user has active subscription
                if data['user']['has_active_subscription']:
                    self.print_success("✅ User has active subscription on login")
                else:
                    self.print_error("❌ User should have active subscription on login")
                    return False
                
                return True
            else:
                self.print_error(f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error during login: {e}")
            return False
    
    def test_get_current_user(self):
        """Test getting current user with subscription status."""
        self.print_step(5, "Get Current User with Subscription Status")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success("Get current user successful!")
                print(f"User ID: {data['id']}")
                print(f"Email: {data['email']}")
                print(f"Has Active Subscription: {data['has_active_subscription']}")
                print(f"Subscription Plan: {data['subscription_plan']}")
                print(f"Can Access Premium: {data['can_access_premium']}")
                
                return True
            else:
                self.print_error(f"Get current user failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error getting current user: {e}")
            return False
    
    def test_content_access(self):
        """Test content access with subscription."""
        self.print_step(6, "Content Access with Subscription")
        
        try:
            # Test content access
            response = requests.get(f"{BASE_URL}/content?limit=3", timeout=10)
            print(f"Content Status Code: {response.status_code}")
            
            if response.status_code == 200:
                content = response.json()
                self.print_success(f"Successfully retrieved {len(content)} content items")
                for item in content:
                    print(f"  • {item['title']} ({item['type']})")
            else:
                self.print_error(f"Failed to get content: {response.text}")
                return False
            
            # Test series access
            response = requests.get(f"{BASE_URL}/series?limit=2", timeout=10)
            print(f"Series Status Code: {response.status_code}")
            
            if response.status_code == 200:
                series = response.json()
                self.print_success(f"Successfully retrieved {len(series)} series")
                for item in series:
                    print(f"  • {item['title']}")
            else:
                self.print_error(f"Failed to get series: {response.text}")
                return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Error testing content access: {e}")
            return False
    
    def test_subscription_status(self):
        """Test subscription status endpoint."""
        self.print_step(7, "Subscription Status Check")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{BASE_URL}/subscriptions/status", headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success("Subscription status check successful!")
                print(f"Has Active Subscription: {data['has_active_subscription']}")
                print(f"Can Access Premium: {data['can_access_premium']}")
                print(f"Current Plan: {data['current_plan']['name'] if data['current_plan'] else 'None'}")
                print(f"Max Devices: {data['max_devices']}")
                print(f"Max Quality: {data['max_quality']}")
                
                return True
            else:
                self.print_error(f"Subscription status check failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error checking subscription status: {e}")
            return False
    
    def run_full_test(self):
        """Run the complete user flow test."""
        print("🚀 PecanTV Full User Flow Test")
        print("Testing: Signup → Subscription Creation → Login → Content Access")
        print(f"Test User: {self.test_email}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test steps
        tests = [
            self.test_health_check,
            self.test_get_subscription_plans,
            self.test_user_registration,
            self.test_create_subscription,
            self.test_user_login,
            self.test_get_current_user,
            self.test_content_access,
            self.test_subscription_status
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    print(f"\n❌ Test failed: {test.__name__}")
                    break
            except Exception as e:
                print(f"\n❌ Test error: {test.__name__} - {e}")
                break
        
        # Print summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ User signup with Stripe customer creation")
            print("✅ Subscription creation and activation")
            print("✅ User login with subscription verification")
            print("✅ Content access with subscription")
            print("✅ Full Netflix-style flow working correctly")
        else:
            print(f"\n❌ {total - passed} test(s) failed")
            print("Please check the errors above and fix any issues")
        
        print(f"\n📋 Test User Details:")
        print(f"Email: {self.test_email}")
        print(f"Password: {self.test_password}")
        if self.user_data:
            print(f"User ID: {self.user_data['user']['id']}")
            print(f"Stripe Customer ID: {self.user_data['user']['stripe_customer_id']}")

def main():
    """Main test runner."""
    test_flow = TestUserFlow()
    test_flow.run_full_test()

if __name__ == "__main__":
    main() 