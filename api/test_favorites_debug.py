#!/usr/bin/env python3
"""
Debug script to test favorites endpoint
"""

import requests
import json
import sys

def test_favorites_endpoint():
    """Test the favorites endpoint with different scenarios"""
    
    base_url = "https://pecantv-api-production.up.railway.app"
    
    print("🔍 Testing Favorites Endpoint")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Health check: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Test 2: Test without authentication
    print("\n2. Testing favorites without authentication...")
    try:
        response = requests.get(f"{base_url}/favorites/13")
        print(f"   No auth response: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected without auth")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ No auth test error: {e}")
    
    # Test 3: Test with invalid token
    print("\n3. Testing favorites with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{base_url}/favorites/13", headers=headers)
        print(f"   Invalid token response: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected invalid token")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Invalid token test error: {e}")
    
    # Test 4: Test with malformed token
    print("\n4. Testing favorites with malformed token...")
    try:
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5YzFjYzFjYy1jYzFjLWMxY2MtY2MxYy1jYzFjYzFjY2MxY2MiLCJ1c2VyX2lkIjoxMywiaWF0IjoxNzM0NzI4MDAwLCJleHAiOjE3MzQ3Mjk4MDAsImlzcyI6InBlY2FudHYtYXBpIiwiYXVkIjoicGVjYW50di11c2VycyJ9.test"}
        response = requests.get(f"{base_url}/favorites/13", headers=headers)
        print(f"   Malformed token response: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Malformed token test error: {e}")
    
    # Test 5: Test content endpoint (should work without auth)
    print("\n5. Testing content endpoint...")
    try:
        response = requests.get(f"{base_url}/content?limit=1")
        print(f"   Content response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Content endpoint works, found {len(data)} items")
        else:
            print(f"   ❌ Content endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Content test error: {e}")

if __name__ == "__main__":
    test_favorites_endpoint() 