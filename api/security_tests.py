#!/usr/bin/env python3
"""
Security testing script for PecanTV API
Tests various security features and configurations
"""

import requests
import json
import time
import threading
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityTester:
    """Security testing class for PecanTV API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, details: str = None):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if details:
            logger.info(f"   Details: {details}")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        logger.info("Testing rate limiting...")
        
        # Test normal requests
        for i in range(5):
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code != 200:
                self.log_test("Rate Limiting - Normal Requests", False, f"Request {i+1} failed: {response.status_code}")
                return
        
        self.log_test("Rate Limiting - Normal Requests", True, "5 requests succeeded")
        
        # Test rate limit exceeded
        responses = []
        for i in range(70):  # Exceed 60/minute limit
            response = self.session.get(f"{self.base_url}/health")
            responses.append(response.status_code)
            if response.status_code == 429:  # Rate limited
                self.log_test("Rate Limiting - Limit Enforcement", True, f"Rate limited after {i+1} requests")
                break
        else:
            self.log_test("Rate Limiting - Limit Enforcement", False, "Rate limit not enforced")
    
    def test_security_headers(self):
        """Test security headers"""
        logger.info("Testing security headers...")
        
        response = self.session.get(f"{self.base_url}/health")
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Referrer-Policy",
            "Content-Security-Policy"
        ]
        
        missing_headers = []
        for header in required_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if missing_headers:
            self.log_test("Security Headers", False, f"Missing headers: {missing_headers}")
        else:
            self.log_test("Security Headers", True, "All required headers present")
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        logger.info("Testing CORS configuration...")
        
        # Test preflight request
        headers = {
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = self.session.options(f"{self.base_url}/health", headers=headers)
        
        # Check if CORS is properly configured
        if "Access-Control-Allow-Origin" in response.headers:
            allowed_origin = response.headers["Access-Control-Allow-Origin"]
            if allowed_origin == "*":
                self.log_test("CORS Configuration", False, "CORS allows all origins (security risk)")
            else:
                self.log_test("CORS Configuration", True, f"Proper CORS configuration: {allowed_origin}")
        else:
            self.log_test("CORS Configuration", True, "CORS headers not present (secure)")
    
    def test_input_validation(self):
        """Test input validation"""
        logger.info("Testing input validation...")
        
        # Test SQL injection attempts
        sql_injection_tests = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; SELECT * FROM users",
            "admin'--",
            "1 UNION SELECT * FROM users"
        ]
        
        for test_input in sql_injection_tests:
            response = self.session.get(f"{self.base_url}/search?q={test_input}")
            if response.status_code == 400:
                self.log_test(f"Input Validation - SQL Injection: {test_input[:20]}", True)
            else:
                self.log_test(f"Input Validation - SQL Injection: {test_input[:20]}", False, 
                             f"Status: {response.status_code}")
        
        # Test XSS attempts
        xss_tests = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src=javascript:alert('xss')>"
        ]
        
        for test_input in xss_tests:
            response = self.session.get(f"{self.base_url}/search?q={test_input}")
            if response.status_code == 400:
                self.log_test(f"Input Validation - XSS: {test_input[:20]}", True)
            else:
                self.log_test(f"Input Validation - XSS: {test_input[:20]}", False,
                             f"Status: {response.status_code}")
    
    def test_authentication_security(self):
        """Test authentication security"""
        logger.info("Testing authentication security...")
        
        # Test weak password
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=weak_password_data)
        if response.status_code == 400:
            self.log_test("Authentication - Weak Password Rejection", True)
        else:
            self.log_test("Authentication - Weak Password Rejection", False,
                         f"Status: {response.status_code}")
        
        # Test invalid email format
        invalid_email_data = {
            "email": "invalid-email",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=invalid_email_data)
        if response.status_code == 400:
            self.log_test("Authentication - Invalid Email Rejection", True)
        else:
            self.log_test("Authentication - Invalid Email Rejection", False,
                         f"Status: {response.status_code}")
    
    def test_endpoint_security(self):
        """Test endpoint security"""
        logger.info("Testing endpoint security...")
        
        # Test unauthorized access to protected endpoints
        protected_endpoints = [
            "/auth/me",
            "/favorites/1",
            "/subscriptions/current"
        ]
        
        for endpoint in protected_endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code in [401, 403]:
                self.log_test(f"Endpoint Security - {endpoint}", True)
            else:
                self.log_test(f"Endpoint Security - {endpoint}", False,
                             f"Status: {response.status_code}")
    
    def test_file_upload_security(self):
        """Test file upload security"""
        logger.info("Testing file upload security...")
        
        # Test malicious file upload
        malicious_files = [
            ("test.php", b"<?php echo 'malicious'; ?>", "application/x-php"),
            ("test.exe", b"malicious executable content", "application/x-executable"),
            ("test.sh", b"#!/bin/bash\nrm -rf /", "application/x-sh")
        ]
        
        for filename, content, content_type in malicious_files:
            files = {"file": (filename, content, content_type)}
            response = self.session.post(f"{self.base_url}/upload", files=files)
            
            # Should reject malicious files
            if response.status_code in [400, 403, 415]:
                self.log_test(f"File Upload Security - {filename}", True)
            else:
                self.log_test(f"File Upload Security - {filename}", False,
                             f"Status: {response.status_code}")
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        logger.info("Testing concurrent requests...")
        
        def make_request():
            return self.session.get(f"{self.base_url}/health")
        
        # Make 10 concurrent requests
        threads = []
        responses = []
        
        for _ in range(10):
            thread = threading.Thread(target=lambda: responses.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Check if all requests were handled properly
        success_count = sum(1 for r in responses if r.status_code == 200)
        if success_count == 10:
            self.log_test("Concurrent Requests", True, "All 10 concurrent requests succeeded")
        else:
            self.log_test("Concurrent Requests", False, f"Only {success_count}/10 requests succeeded")
    
    def test_error_handling(self):
        """Test error handling security"""
        logger.info("Testing error handling...")
        
        # Test for information disclosure in errors
        response = self.session.get(f"{self.base_url}/nonexistent-endpoint")
        
        # Check if error response contains sensitive information
        error_content = response.text.lower()
        sensitive_terms = ["password", "secret", "key", "token", "database", "sql"]
        
        exposed_info = []
        for term in sensitive_terms:
            if term in error_content:
                exposed_info.append(term)
        
        if exposed_info:
            self.log_test("Error Handling - Information Disclosure", False,
                         f"Sensitive terms found: {exposed_info}")
        else:
            self.log_test("Error Handling - Information Disclosure", True)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        logger.info("Starting comprehensive security testing...")
        
        tests = [
            self.test_rate_limiting,
            self.test_security_headers,
            self.test_cors_configuration,
            self.test_input_validation,
            self.test_authentication_security,
            self.test_endpoint_security,
            self.test_file_upload_security,
            self.test_concurrent_requests,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test failed with exception: {e}")
                self.log_test(test.__name__, False, f"Exception: {str(e)}")
        
        # Generate summary
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "results": self.test_results
        }
        
        logger.info(f"\n{'='*50}")
        logger.info(f"SECURITY TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] >= 90:
            logger.info("🎉 Excellent security posture!")
        elif summary['success_rate'] >= 75:
            logger.info("✅ Good security posture with room for improvement")
        elif summary['success_rate'] >= 50:
            logger.info("⚠️  Moderate security posture - improvements needed")
        else:
            logger.info("🚨 Poor security posture - immediate attention required")
        
        return summary

def main():
    """Main function to run security tests"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = SecurityTester(base_url)
    results = tester.run_all_tests()
    
    # Save results to file
    with open("security_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to security_test_results.json")

if __name__ == "__main__":
    main() 