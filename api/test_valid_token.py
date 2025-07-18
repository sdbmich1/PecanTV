#!/usr/bin/env python3
"""
Generate a valid JWT token for testing
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from database import get_db
from models import User

def generate_test_token():
    """Generate a valid JWT token for user 13"""
    
    # JWT Configuration (should match the API)
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    
    # Get user 13 from database
    db = next(get_db())
    user_13 = db.query(User).filter(User.id == 13).first()
    
    if not user_13:
        print("❌ User 13 not found in database")
        return None
    
    user_uuid = str(user_13.uuid)
    user_id = user_13.id
    
    # Create token payload
    payload = {
        "sub": user_uuid,
        "user_id": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iss": "pecantv-api",
        "aud": "pecantv-users"
    }
    
    # Generate token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    print(f"🔑 Generated test token for user {user_id}:")
    print(f"Token: {token}")
    print(f"User UUID: {user_uuid}")
    print(f"User ID: {user_id}")
    print(f"User Email: {user_13.email}")
    
    db.close()
    return token

if __name__ == "__main__":
    generate_test_token() 