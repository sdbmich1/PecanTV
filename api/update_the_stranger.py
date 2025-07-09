#!/usr/bin/env python3
"""
Script to set The Stranger (ID 85) poster_url to 'NONE'
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def update_the_stranger():
    """Set The Stranger poster_url to 'NONE'"""
    
    db = next(get_db())
    
    try:
        # Find The Stranger film by ID
        the_stranger = db.query(Content).filter(
            Content.id == 85,
            Content.type == ContentType.FILM
        ).first()
        
        if not the_stranger:
            print("❌ The Stranger film (ID 85) not found in database")
            return
        
        print(f"🎬 Found film: {the_stranger.title}")
        print(f"📸 Current poster: {the_stranger.poster_url}")
        
        # Set poster_url to 'NONE'
        the_stranger.poster_url = 'NONE'
        
        # Commit the change
        db.commit()
        
        # Verify the change
        db.refresh(the_stranger)
        print(f"✅ Updated poster to: {the_stranger.poster_url}")
        print("🎯 The Stranger will now be hidden from carousel display")
        
    except Exception as e:
        print(f"❌ Error updating The Stranger poster: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_the_stranger() 