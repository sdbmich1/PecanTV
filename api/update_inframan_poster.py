#!/usr/bin/env python3
"""
Script to set Inframan (ID 84) poster_url to 'NONE'
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def update_inframan_poster():
    """Set Inframan poster_url to 'NONE'"""
    
    db = next(get_db())
    
    try:
        # Find Inframan film by ID
        inframan = db.query(Content).filter(
            Content.id == 84,
            Content.type == ContentType.FILM
        ).first()
        
        if not inframan:
            print("❌ Inframan film (ID 84) not found in database")
            return
        
        print(f"🎬 Found film: {inframan.title}")
        print(f"📸 Current poster: {inframan.poster_url}")
        
        # Set poster_url to 'NONE'
        inframan.poster_url = 'NONE'
        
        # Commit the change
        db.commit()
        
        # Verify the change
        db.refresh(inframan)
        print(f"✅ Updated poster to: {inframan.poster_url}")
        print("🎯 Inframan will now be hidden from carousel display")
        
    except Exception as e:
        print(f"❌ Error updating Inframan poster: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_inframan_poster() 