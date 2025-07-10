#!/usr/bin/env python3
"""
Security Tests for PecanTV API
Tests the security fixes applied to the application.
"""

import requests
import json
from typing import Dict, Any

class SecurityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_access_control(self) -> Dict[str, Any]:
        """Test access control fixes"""
        print("🔒 Testing access control...")
        
        # Test unauthorized access to favorites
        try:
            response = self.session.get(f"{self.base_url}/favorites/999")
            if response.status_code == 403:
                return {"test": "Access Control", "passed": True, "details": "Properly blocked unauthorized access"}
            else:
                return {"test": "Access Control", "passed": False, "details": f"Expected 403, got {response.status_code}"}
        except Exception as e:
            return {"test": "Access Control", "passed": False, "details": f"Error: {str(e)}"}
    
    def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation fixes"""
        print("🔍 Testing input validation...")
        
        # Test SQL injection attempts
        sql_injection_tests = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--"
        ]
        
        for test_input in sql_injection_tests:
            try:
                response = self.session.get(f"{self.base_url}/search?q={test_input}")
                if response.status_code == 400:
                    return {"test": "SQL Injection Protection", "passed": True, "details": f"Blocked: {test_input[:20]}..."}
                else:
                    return {"test": "SQL Injection Protection", "passed": False, "details": f"Failed to block: {test_input[:20]}..."}
            except Exception as e:
                return {"test": "SQL Injection Protection", "passed": False, "details": f"Error: {str(e)}"}
        
        return {"test": "Input Validation", "passed": True, "details": "All tests passed"}
    
    def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers"""
        print("🛡️ Testing security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            headers = response.headers
            
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Content-Security-Policy"
            ]
            
            missing_headers = [h for h in required_headers if h not in headers]
            
            if missing_headers:
                return {"test": "Security Headers", "passed": False, "details": f"Missing headers: {missing_headers}"}
            else:
                return {"test": "Security Headers", "passed": True, "details": "All required headers present"}
        except Exception as e:
            return {"test": "Security Headers", "passed": False, "details": f"Error: {str(e)}"}
    
    def test_debug_endpoints(self) -> Dict[str, Any]:
        """Test that debug endpoints are removed"""
        print("🚫 Testing debug endpoints...")
        
        debug_endpoints = [
            "/debug/episodes/1",
            "/test-cdn",
            "/security/test",
            "/test-security"
        ]
        
        for endpoint in debug_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code != 404:
                    return {"test": "Debug Endpoints", "passed": False, "details": f"Endpoint {endpoint} still accessible"}
            except Exception:
                pass  # Expected for removed endpoints
        
        return {"test": "Debug Endpoints", "passed": True, "details": "All debug endpoints properly removed"}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        print("🔐 Running comprehensive security tests...")
        
        tests = [
            self.test_access_control(),
            self.test_input_validation(),
            self.test_security_headers(),
            self.test_debug_endpoints()
        ]
        
        passed = sum(1 for test in tests if test["passed"])
        total = len(tests)
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        for test in tests:
            status = "✅" if test["passed"] else "❌"
            print(f"{status} {test['test']}: {test['details']}")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": (passed / total) * 100 if total > 0 else 0,
            "results": tests
        }

if __name__ == "__main__":
    tester = SecurityTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("security_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to security_test_results.json")
