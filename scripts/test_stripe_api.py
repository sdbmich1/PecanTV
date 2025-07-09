#!/usr/bin/env python3
"""
Test script for PecanTV Stripe integration
Run this after setting up the integration to test all endpoints
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_subscription_plans():
    """Test getting subscription plans."""
    print("Testing subscription plans endpoint...")
    response = requests.get(f"{API_BASE_URL}/subscriptions/plans")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        plans = response.json()
        print(f"Found {len(plans)} plans:")
        for plan in plans:
            print(f"  - {plan['name']}: ${plan['price']}/month")
    else:
        print(f"Error: {response.text}")

def test_create_subscription():
    """Test creating a subscription."""
    print("\nTesting subscription creation...")
    data = {
        "plan_id": 1,
        "customer_id": "test_customer_123"
    }
    response = requests.post(f"{API_BASE_URL}/subscriptions/create", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        subscription = response.json()
        print(f"Created subscription: {subscription}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_subscription_plans()
    test_create_subscription()
