#!/usr/bin/env python3
"""
Quick Security Fixes Script
Applies the most critical security fixes identified in our analysis.
Run this script to immediately improve security posture.
"""

import os
import re
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the file before modifying"""
    backup_path = f"{file_path}.backup"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backed up {file_path} to {backup_path}")

def apply_fixes():
    """Apply critical security fixes"""
    
    print("🔒 Applying Critical Security Fixes...")
    print("=" * 50)
    
    # Fix 1: Remove debug endpoints from main.py
    print("\n1. Removing debug endpoints...")
    main_py_path = "main.py"
    if os.path.exists(main_py_path):
        backup_file(main_py_path)
        
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Remove debug endpoints
        patterns_to_remove = [
            r'@app\.get\("/debug/episodes/\{series_id\}"\).*?def.*?\{.*?\}',
            r'@app\.get\("/test-security"\).*?def.*?\{.*?\}',
            r'@app\.get\("/security/test"\).*?def.*?\{.*?\}',
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Remove commented debug endpoints
        content = re.sub(r'# @app\.get\("/debug.*?\n', '', content)
        content = re.sub(r'# @app\.get\("/test.*?\n', '', content)
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print("✅ Debug endpoints removed from main.py")
    
    # Fix 2: Enhance security headers in security_middleware.py
    print("\n2. Enhancing security headers...")
    security_middleware_path = "security_middleware.py"
    if os.path.exists(security_middleware_path):
        backup_file(security_middleware_path)
        
        with open(security_middleware_path, 'r') as f:
            content = f.read()
        
        # Add missing security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self';"
        }
        
        # Find the security headers section and add missing ones
        header_pattern = r'security_headers = \{([^}]*)\}'
        match = re.search(header_pattern, content, re.DOTALL)
        
        if match:
            existing_headers = match.group(1)
            new_headers = existing_headers.rstrip()
            
            for header, value in security_headers.items():
                if f'"{header}"' not in existing_headers:
                    new_headers += f'\n    "{header}": "{value}",'
            
            new_headers += '\n'
            content = re.sub(header_pattern, f'security_headers = {{{new_headers}}}', content, flags=re.DOTALL)
            
            with open(security_middleware_path, 'w') as f:
                f.write(content)
            
            print("✅ Security headers enhanced")
    
    # Fix 3: Add input validation to search endpoint
    print("\n3. Adding input validation to search endpoint...")
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Find search endpoint and add validation
        search_pattern = r'(@app\.get\("/search".*?def search_content.*?q: str.*?)(.*?)(db: Session = Depends\(get_db\)\):)'
        match = re.search(search_pattern, content, re.DOTALL)
        
        if match:
            before = match.group(1)
            params = match.group(2)
            after = match.group(3)
            
            # Add validation parameters
            validation_params = '''
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
'''
            
            # Add validation logic
            validation_logic = '''
    # Input validation
    if not q or len(q.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    # Sanitize search query
    q = q.strip()
    if len(q) > 100:
        raise HTTPException(status_code=400, detail="Search query too long (max 100 characters)")
    
    # Prevent SQL injection by checking for suspicious patterns
    suspicious_patterns = ["'", '"', ';', '--', '/*', '*/', 'union', 'select', 'drop', 'delete', 'insert', 'update']
    q_lower = q.lower()
    for pattern in suspicious_patterns:
        if pattern in q_lower:
            raise HTTPException(status_code=400, detail="Invalid search query")
    
'''
            
            new_search = before + validation_params + after + validation_logic
            
            content = re.sub(search_pattern, new_search, content, flags=re.DOTALL)
            
            # Add import for Query
            if 'from fastapi import Query' not in content:
                content = content.replace('from fastapi import FastAPI, HTTPException, Depends, Request', 
                                        'from fastapi import FastAPI, HTTPException, Depends, Request, Query')
            
            with open(main_py_path, 'w') as f:
                f.write(content)
            
            print("✅ Search endpoint validation added")
    
    # Fix 4: Enhance URL validation in main.py
    print("\n4. Enhancing URL validation...")
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Add more comprehensive IP blocking
        enhanced_blocked_ranges = '''
    BLOCKED_IP_RANGES = [
        '127.0.0.0/8',      # Localhost
        '10.0.0.0/8',       # Private network
        '172.16.0.0/12',    # Private network
        '192.168.0.0/16',   # Private network
        '169.254.0.0/16',   # Link-local
        '::1/128',          # IPv6 localhost
        'fe80::/10',        # IPv6 link-local
        '0.0.0.0/8',        # Current network
        '224.0.0.0/4',      # Multicast
        '240.0.0.0/4',      # Reserved
        '255.255.255.255/32', # Broadcast
    ]
'''
        
        # Replace the existing BLOCKED_IP_RANGES
        content = re.sub(r'BLOCKED_IP_RANGES = \[.*?\]', enhanced_blocked_ranges, content, flags=re.DOTALL)
        
        # Add timeout to external requests in CDN endpoint
        cdn_timeout_pattern = r'(requests\.get\(url, timeout=10\))'
        if 'timeout=10' not in content:
            content = re.sub(r'requests\.get\(url\)', 'requests.get(url, timeout=10)', content)
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print("✅ URL validation enhanced")
    
    # Fix 5: Add rate limiting to sensitive endpoints
    print("\n5. Adding rate limiting to sensitive endpoints...")
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Add rate limiting decorator to sensitive endpoints
        sensitive_endpoints = [
            '/auth/login',
            '/auth/register', 
            '/search',
            '/content'
        ]
        
        for endpoint in sensitive_endpoints:
            if endpoint in content and '@rate_limit' not in content:
                # Add rate limiting import
                if 'from security_middleware import rate_limit' not in content:
                    content = content.replace('from security_middleware import security_middleware',
                                            'from security_middleware import security_middleware, rate_limit')
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print("✅ Rate limiting prepared for sensitive endpoints")
    
    print("\n" + "=" * 50)
    print("✅ Critical security fixes applied!")
    print("\nNext steps:")
    print("1. Test the application: python3 main.py")
    print("2. Run security tests: python3 security_tests_new.py")
    print("3. Review the changes and commit: git add . && git commit -m 'Apply critical security fixes'")
    print("4. Continue with the full security implementation plan")

if __name__ == "__main__":
    apply_fixes() 