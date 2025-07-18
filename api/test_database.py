#!/usr/bin/env python3
"""
Test database connection and data
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Favorite, Content
from database import get_db

def test_database():
    """Test database connection and data"""
    
    print("🔍 Testing Database Connection")
    print("=" * 50)
    
    try:
        # Get database session
        db = next(get_db())
        
        # Test 1: Check if users exist
        print("\n1. Checking users...")
        users = db.query(User).all()
        print(f"   Found {len(users)} users")
        for user in users[:5]:  # Show first 5 users
            print(f"   • User {user.id}: {user.email} (UUID: {user.uuid})")
        
        # Test 2: Check if content exists
        print("\n2. Checking content...")
        content = db.query(Content).all()
        print(f"   Found {len(content)} content items")
        for item in content[:5]:  # Show first 5 items
            print(f"   • Content {item.id}: {item.title}")
        
        # Test 3: Check if favorites exist
        print("\n3. Checking favorites...")
        favorites = db.query(Favorite).all()
        print(f"   Found {len(favorites)} favorites")
        for fav in favorites[:5]:  # Show first 5 favorites
            print(f"   • Favorite: User {fav.user_id} -> Content {fav.content_id}")
        
        # Test 4: Check specific user (ID 13)
        print("\n4. Checking user ID 13...")
        user_13 = db.query(User).filter(User.id == 13).first()
        if user_13:
            print(f"   ✅ User 13 exists: {user_13.email}")
            
            # Check their favorites
            user_favorites = db.query(Favorite).filter(Favorite.user_id == 13).all()
            print(f"   User 13 has {len(user_favorites)} favorites")
            for fav in user_favorites:
                content_item = db.query(Content).filter(Content.id == fav.content_id).first()
                if content_item:
                    print(f"   • {content_item.title} (ID: {content_item.id})")
        else:
            print("   ❌ User 13 does not exist")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database() 