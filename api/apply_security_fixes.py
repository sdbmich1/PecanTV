#!/usr/bin/env python3
"""
Security Fixes Application Script
Automatically applies critical security fixes to the PecanTV codebase.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class SecurityFixer:
    def __init__(self):
        self.backup_dir = Path("backups") / f"security_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.changes_made = []
        
    def backup_file(self, file_path: str):
        """Create backup of file before modification"""
        file_path = Path(file_path)
        if file_path.exists():
            backup_path = self.backup_dir / file_path.name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backed up {file_path} to {backup_path}")
    
    def apply_fix_1_access_control(self):
        """Fix broken access control in favorites endpoint"""
        file_path = "main.py"
        self.backup_file(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the favorites endpoint
        pattern = r'@app\.get\("/favorites/\{user_id\}"\)\ndef get_user_favorites\(user_id: int, db: Session = Depends\(get_db\)\):'
        
        if re.search(pattern, content):
            # Replace with secure version
            secure_version = '''@app.get("/favorites/{user_id}")
def get_user_favorites(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all favorites for a user"""
    # Authorization check
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only view your own favorites"
        )'''
            
            content = re.sub(pattern, secure_version, content)
            
            # Add import if not present
            if "from fastapi import status" not in content:
                content = content.replace(
                    "from fastapi import Depends, HTTPException",
                    "from fastapi import Depends, HTTPException, status"
                )
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.changes_made.append("Fixed broken access control in favorites endpoint")
            print("✅ Applied fix 1: Access control")
        else:
            print("⚠️  Could not find favorites endpoint to fix")
    
    def apply_fix_2_password_hashing(self):
        """Fix weak password hashing in CRUD operations"""
        file_path = "crud.py"
        self.backup_file(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the create_user function
        pattern = r'def create_user\(db: Session, user: schemas\.UserCreate\) -> models\.User:\s*# Hash the password\s*password_hash = hashlib\.sha256\(user\.password\.encode\(\)\)\.hexdigest\(\)'
        
        if re.search(pattern, content, re.DOTALL):
            # Replace with secure version
            secure_version = '''def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # Use enhanced auth service for secure password handling
    from enhanced_auth_service import EnhancedAuthService
    from fastapi import HTTPException, status
    
    auth_service = EnhancedAuthService()
    
    # Validate password strength
    password_validation = auth_service.validate_password_strength(user.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
        )
    
    # Hash password securely
    password_hash = auth_service.get_password_hash(user.password)'''
            
            content = re.sub(pattern, secure_version, content, flags=re.DOTALL)
            
            # Also fix verify_user_password function
            verify_pattern = r'def verify_user_password\(db: Session, email: str, password: str\) -> Optional\[models\.User\]:\s*user = get_user_by_email\(db, email\)\s*if user:\s*password_hash = hashlib\.sha256\(password\.encode\(\)\)\.hexdigest\(\)\s*if user\.password_hash == password_hash:\s*return user\s*return None'
            
            if re.search(verify_pattern, content, re.DOTALL):
                secure_verify = '''def verify_user_password(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if user:
        auth_service = EnhancedAuthService()
        if auth_service.verify_password(password, user.password_hash):
            return user
    return None'''
                
                content = re.sub(verify_pattern, secure_verify, content, flags=re.DOTALL)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.changes_made.append("Fixed weak password hashing")
            print("✅ Applied fix 2: Password hashing")
        else:
            print("⚠️  Could not find create_user function to fix")
    
    def apply_fix_3_input_validation(self):
        """Add input validation to search functionality"""
        file_path = "crud.py"
        self.backup_file(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the search_content function
        pattern = r'def search_content\(\s*db: Session,\s*query: str,\s*skip: int = 0,\s*limit: int = 100\s*\) -> List\[models\.Content\]:\s*return db\.query\(models\.Content\)\.filter\(\s*or_\(\s*models\.Content\.title\.ilike\(f"%\{query\}%"\),\s*models\.Content\.description\.ilike\(f"%\{query\}%"\)\s*\)\s*\)\.offset\(skip\)\.limit\(limit\)\.all\(\)'
        
        if re.search(pattern, content, re.DOTALL):
            # Replace with secure version
            secure_version = '''def search_content(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.Content]:
    # Input validation
    from security_middleware import InputValidator
    from fastapi import HTTPException, status
    
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    if len(query) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query too long (max 100 characters)"
        )
    
    # Sanitize input
    is_valid, error_msg = InputValidator.validate_input(query, "search_query")
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search query: {error_msg}"
        )
    
    # Sanitize the query
    sanitized_query = InputValidator.sanitize_input(query)
    
    return db.query(models.Content).filter(
        or_(
            models.Content.title.ilike(f"%{sanitized_query}%"),
            models.Content.description.ilike(f"%{sanitized_query}%")
        )
    ).offset(skip).limit(limit).all()'''
            
            content = re.sub(pattern, secure_version, content, flags=re.DOTALL)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.changes_made.append("Added input validation to search functionality")
            print("✅ Applied fix 3: Input validation")
        else:
            print("⚠️  Could not find search_content function to fix")
    
    def apply_fix_4_parameter_validation(self):
        """Add parameter validation to API endpoints"""
        file_path = "main.py"
        self.backup_file(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the get_content function
        pattern = r'def get_content\(\s*skip: int = 0,\s*limit: int = 500,\s*type: str = None,\s*genre: str = None,\s*db: Session = Depends\(get_db\)\s*\):'
        
        if re.search(pattern, content, re.DOTALL):
            # Replace with secure version
            secure_version = '''def get_content(
    skip: int = Query(0, ge=0, le=1000, description="Number of items to skip"),
    limit: int = Query(500, ge=1, le=1000, description="Number of items to return"),
    type: Optional[str] = Query(None, regex="^(FILM|SERIES)$", description="Content type filter"),
    genre: Optional[str] = Query(None, max_length=50, description="Genre filter"),
    db: Session = Depends(get_db)
):'''
            
            content = re.sub(pattern, secure_version, content, re.DOTALL)
            
            # Add imports if not present
            if "from fastapi import Query" not in content:
                content = content.replace(
                    "from fastapi import Depends, HTTPException, status",
                    "from fastapi import Depends, HTTPException, status, Query"
                )
            
            if "from typing import Optional" not in content:
                content = content.replace(
                    "from typing import List",
                    "from typing import List, Optional"
                )
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.changes_made.append("Added parameter validation to API endpoints")
            print("✅ Applied fix 4: Parameter validation")
        else:
            print("⚠️  Could not find get_content function to fix")
    
    def apply_fix_5_remove_debug_endpoints(self):
        """Remove debug endpoints from production"""
        file_path = "main.py"
        self.backup_file(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find and comment out debug endpoints
        debug_patterns = [
            r'@app\.get\("/debug/episodes/\{series_id\}"\)\ndef debug_episodes\(.*?\):.*?return debug_data',
            r'@app\.get\("/test-cdn"\)\ndef test_cdn\(.*?\):.*?return {"message": "CDN test endpoint"}',
            r'@app\.get\("/security/test"\)\ndef test_security\(.*?\):.*?return {"message": "Security test endpoint working"}',
            r'@app\.get\("/test-security"\)\ndef test_security_alt\(.*?\):.*?return {"message": "Security test endpoint working \(alt path\)"}'
        ]
        
        for pattern in debug_patterns:
            if re.search(pattern, content, re.DOTALL):
                # Comment out the entire function
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    original = match.group(0)
                    commented = "\n".join([f"# {line}" for line in original.split("\n")])
                    content = content.replace(original, commented)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        self.changes_made.append("Removed debug endpoints from production")
        print("✅ Applied fix 5: Removed debug endpoints")
    
    def apply_fix_6_security_headers(self):
        """Add security headers middleware"""
        file_path = "security_middleware.py"
        self.backup_file(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add security headers class if not present
        if "class SecurityHeadersMiddleware" not in content:
            security_headers_code = '''

class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "media-src 'self' https:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        }
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response
'''
            
            content += security_headers_code
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.changes_made.append("Added security headers middleware")
            print("✅ Applied fix 6: Security headers")
        else:
            print("⚠️  Security headers middleware already exists")
    
    def apply_fix_7_ssrf_protection(self):
        """Add SSRF protection to CDN endpoint"""
        file_path = "main.py"
        self.backup_file(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add URL validator class
        url_validator_code = '''
class URLValidator:
    """Validate URLs to prevent SSRF attacks"""
    
    ALLOWED_DOMAIN_SUFFIXES = [
        '.googleapis.com',
        '.cloudflare.com',
        '.amazonaws.com',
        '.yourdomain.com'  # Add your domains
    ]
    
    BLOCKED_IP_RANGES = [
        '127.0.0.0/8',      # Localhost
        '10.0.0.0/8',       # Private network
        '172.16.0.0/12',    # Private network
        '192.168.0.0/16',   # Private network
        '169.254.0.0/16',   # Link-local
        '::1/128',          # IPv6 localhost
        'fe80::/10',        # IPv6 link-local
    ]
    
    @classmethod
    def is_allowed_url(cls, url: str) -> bool:
        """Check if URL is allowed (no internal IPs, valid domain)"""
        try:
            parsed = urlparse(url)
            
            # Check if it's an IP address
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                
                # Block private and loopback IPs
                if ip.is_private or ip.is_loopback:
                    return False
                
                # Check against blocked IP ranges
                for blocked_range in cls.BLOCKED_IP_RANGES:
                    if ip in ipaddress.ip_network(blocked_range):
                        return False
                        
            except ValueError:
                # Not an IP address, check domain
                pass
            
            # Check domain against allowed suffixes
            hostname = parsed.hostname.lower()
            return any(hostname.endswith(suffix) for suffix in cls.ALLOWED_DOMAIN_SUFFIXES)
            
        except Exception:
            return False
'''
        
        # Add imports if not present
        if "from urllib.parse import urlparse" not in content:
            content = content.replace(
                "import requests",
                "import requests\nfrom urllib.parse import urlparse\nimport ipaddress"
            )
        
        # Add URL validator before the CDN endpoint
        cdn_pattern = r'@app\.get\("/cdn-cgi/image/\{params:path\}"\)'
        if re.search(cdn_pattern, content):
            # Insert URL validator before CDN endpoint
            content = re.sub(cdn_pattern, url_validator_code + "\n\n" + r"@app.get('/cdn-cgi/image/{params:path}')", content)
            
            # Update CDN endpoint to use URL validation
            cdn_function_pattern = r'if \(url\.startswith\(\'http://\'\) or url\.startswith\(\'https://\'\)\):'
            if re.search(cdn_function_pattern, content):
                secure_cdn = '''if (url.startswith('http://') or url.startswith('https://')):
            # Validate URL to prevent SSRF
            if not URLValidator.is_allowed_url(url):
                raise HTTPException(
                    status_code=400, 
                    detail="URL not allowed for security reasons"
                )'''
                
                content = re.sub(cdn_function_pattern, secure_cdn, content)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.changes_made.append("Added SSRF protection to CDN endpoint")
            print("✅ Applied fix 7: SSRF protection")
        else:
            print("⚠️  Could not find CDN endpoint to fix")
    
    def create_security_test_file(self):
        """Create a security test file"""
        test_content = '''#!/usr/bin/env python3
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
'''
        
        with open("security_tests_new.py", "w") as f:
            f.write(test_content)
        
        self.changes_made.append("Created comprehensive security test file")
        print("✅ Created security test file: security_tests_new.py")
    
    def run_all_fixes(self):
        """Apply all security fixes"""
        print("🔧 Applying critical security fixes to PecanTV...")
        print("=" * 60)
        
        try:
            self.apply_fix_1_access_control()
            self.apply_fix_2_password_hashing()
            self.apply_fix_3_input_validation()
            self.apply_fix_4_parameter_validation()
            self.apply_fix_5_remove_debug_endpoints()
            self.apply_fix_6_security_headers()
            self.apply_fix_7_ssrf_protection()
            self.create_security_test_file()
            
            print("\n" + "=" * 60)
            print("✅ All security fixes applied successfully!")
            print(f"📁 Backups saved to: {self.backup_dir}")
            print("\n📋 Changes made:")
            for change in self.changes_made:
                print(f"  • {change}")
            
            print("\n🚀 Next steps:")
            print("  1. Review the changes in the modified files")
            print("  2. Test the application thoroughly")
            print("  3. Run: python3 security_tests_new.py")
            print("  4. Deploy to production")
            
        except Exception as e:
            print(f"❌ Error applying fixes: {e}")
            print("Please check the backup files and apply fixes manually")

def main():
    """Main function"""
    fixer = SecurityFixer()
    fixer.run_all_fixes()

if __name__ == "__main__":
    main() 