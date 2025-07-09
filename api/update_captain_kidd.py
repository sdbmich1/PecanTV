#!/usr/bin/env python3
"""
Script to update Captain Kidd film (ID 76) poster URL
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def update_captain_kidd():
    """Update Captain Kidd film poster URL"""
    
    db = next(get_db())
    
    try:
        # Find Captain Kidd film by ID
        captain_kidd = db.query(Content).filter(
            Content.id == 76,
            Content.type == ContentType.FILM
        ).first()
        
        if not captain_kidd:
            print("❌ Captain Kidd film (ID 76) not found in database")
            return
        
        print(f"🎬 Found film: {captain_kidd.title}")
        print(f"📸 Current poster: {captain_kidd.poster_url}")
        
        # New poster URL
        new_poster_url = "https://storage.googleapis.com/pecantv_title_images/Captain-Kidd_title-img.jpg"
        
        # Update the poster URL
        captain_kidd.poster_url = new_poster_url
        db.commit()
        
        print(f"✅ Updated poster URL to: {new_poster_url}")
        
        # Verify the update
        updated_film = db.query(Content).filter(Content.id == 76).first()
        print(f"🔍 Verification - New poster: {updated_film.poster_url}")
        
    except Exception as e:
        print(f"❌ Error updating Captain Kidd film: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_captain_kidd() 