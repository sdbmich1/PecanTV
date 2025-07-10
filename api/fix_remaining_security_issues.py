#!/usr/bin/env python3
"""
Fix Remaining Security Issues
Addresses the access control and debug endpoint issues identified in security tests.
"""

import os
import re
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the file before modifying"""
    backup_path = f"{file_path}.backup2"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backed up {file_path} to {backup_path}")

def fix_authentication_dependency():
    """Fix the authentication dependency issue in main.py"""
    print("🔐 Fixing authentication dependency...")
    
    main_py_path = "main.py"
    if os.path.exists(main_py_path):
        backup_file(main_py_path)
        
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Add proper imports
        if 'from fastapi import HTTPException, status' not in content:
            content = content.replace('from fastapi import FastAPI, HTTPException, Depends, Request, Query', 
                                    'from fastapi import FastAPI, HTTPException, Depends, Request, Query, status')
        
        # Create a proper authentication dependency function
        auth_dependency = '''
def get_current_user_dependency(token: str = Depends(HTTPBearer()), db: Session = Depends(get_db)) -> User:
    """Dependency to get current user from JWT token"""
    try:
        user = AuthService.get_current_user(db, token.credentials)
        return user
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

'''
        
        # Add the dependency function after the imports
        if 'def get_current_user_dependency' not in content:
            # Find the first function definition and add before it
            match = re.search(r'@app\.get\("/"\)', content)
            if match:
                insert_pos = match.start()
                content = content[:insert_pos] + auth_dependency + content[insert_pos:]
        
        # Update the favorites endpoint to use the proper dependency
        favorites_pattern = r'(@app\.get\("/favorites/\{user_id\}"\)\ndef get_user_favorites\([^)]*user_id: int[^)]*db: Session = Depends\(get_db\),\s*)(current_user: User = Depends\(get_current_user\))([^)]*\):)'
        
        if re.search(favorites_pattern, content):
            content = re.sub(favorites_pattern, r'\1current_user: User = Depends(get_current_user_dependency)\3', content)
        
        # Also fix the toggle_favorite endpoint to require authentication
        toggle_pattern = r'(@app\.post\("/favorites/\{user_id\}/toggle/\{content_id\}"\)\ndef toggle_favorite\([^)]*user_id: int[^)]*content_id: int[^)]*db: Session = Depends\(get_db\))([^)]*\):)'
        
        if re.search(toggle_pattern, content):
            content = re.sub(toggle_pattern, r'\1, current_user: User = Depends(get_current_user_dependency)\2:', content)
            
            # Add authorization check to toggle_favorite
            toggle_body_pattern = r'(def toggle_favorite\([^)]*\):\s*"""Toggle favorite status for a content item"""\s*)(result = crud\.toggle_user_favorite)'
            if re.search(toggle_body_pattern, content):
                auth_check = '''
    # Authorization check
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only modify your own favorites"
        )
    
    '''
                content = re.sub(toggle_body_pattern, r'\1' + auth_check + r'\2', content)
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print("✅ Authentication dependency fixed")
    
    return True

def remove_remaining_debug_endpoints():
    """Remove any remaining debug endpoints"""
    print("🚫 Removing remaining debug endpoints...")
    
    main_py_path = "main.py"
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Remove any remaining debug endpoints
        debug_patterns = [
            r'@app\.get\("/debug/[^"]*"\).*?def.*?\{.*?\}',
            r'@app\.post\("/debug/[^"]*"\).*?def.*?\{.*?\}',
            r'@app\.put\("/debug/[^"]*"\).*?def.*?\{.*?\}',
            r'@app\.delete\("/debug/[^"]*"\).*?def.*?\{.*?\}',
        ]
        
        for pattern in debug_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Remove commented debug endpoints
        content = re.sub(r'# @app\.get\("/debug.*?\n', '', content)
        content = re.sub(r'# @app\.post\("/debug.*?\n', '', content)
        content = re.sub(r'# @app\.put\("/debug.*?\n', '', content)
        content = re.sub(r'# @app\.delete\("/debug.*?\n', '', content)
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print("✅ Remaining debug endpoints removed")
    
    return True

def add_http_bearer_import():
    """Add HTTPBearer import for authentication"""
    print("🔑 Adding HTTPBearer import...")
    
    main_py_path = "main.py"
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Add HTTPBearer import
        if 'from fastapi.security import HTTPBearer' not in content:
            content = content.replace('from fastapi import FastAPI, HTTPException, Depends, Request, Query, status', 
                                    'from fastapi import FastAPI, HTTPException, Depends, Request, Query, status\nfrom fastapi.security import HTTPBearer')
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print("✅ HTTPBearer import added")
    
    return True

def fix_remaining_issues():
    """Fix all remaining security issues"""
    print("🔒 Fixing Remaining Security Issues...")
    print("=" * 50)
    
    # Fix authentication dependency
    fix_authentication_dependency()
    
    # Add HTTPBearer import
    add_http_bearer_import()
    
    # Remove remaining debug endpoints
    remove_remaining_debug_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Remaining security issues fixed!")
    print("\nNext steps:")
    print("1. Test the application: python3 main.py")
    print("2. Run security tests: python3 security_tests_new.py")
    print("3. Verify all tests pass")

if __name__ == "__main__":
    fix_remaining_issues() 