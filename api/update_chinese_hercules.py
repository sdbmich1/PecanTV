#!/usr/bin/env python3
"""
Script to update Chinese Hercules film (ID 74) poster URL
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def update_chinese_hercules():
    """Update Chinese Hercules film poster URL"""
    
    db = next(get_db())
    
    try:
        # Find Chinese Hercules film by ID
        chinese_hercules = db.query(Content).filter(
            Content.id == 74,
            Content.type == ContentType.FILM
        ).first()
        
        if not chinese_hercules:
            print("❌ Chinese Hercules film (ID 74) not found in database")
            return
        
        print(f"🎬 Found film: {chinese_hercules.title}")
        print(f"📸 Current poster: {chinese_hercules.poster_url}")
        
        # New poster URL
        new_poster_url = "https://storage.googleapis.com/pecantv_title_images/Chinese-Hercules_title-img.png"
        
        # Update the poster URL
        chinese_hercules.poster_url = new_poster_url
        db.commit()
        
        print(f"✅ Updated poster URL to: {new_poster_url}")
        
        # Verify the update
        updated_film = db.query(Content).filter(Content.id == 74).first()
        print(f"🔍 Verification - New poster: {updated_film.poster_url}")
        
    except Exception as e:
        print(f"❌ Error updating Chinese Hercules film: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_chinese_hercules() 