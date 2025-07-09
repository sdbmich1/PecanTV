#!/usr/bin/env python3
"""
Script to update NLD film (ID 4) poster URL
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def update_nld_poster():
    """Update NLD film poster URL"""
    
    db = next(get_db())
    
    try:
        # Find NLD film by ID
        nld_film = db.query(Content).filter(
            Content.id == 4,
            Content.type == ContentType.FILM
        ).first()
        
        if not nld_film:
            print("❌ NLD film (ID 4) not found in database")
            return
        
        print(f"🎬 Found film: {nld_film.title}")
        print(f"📸 Current poster: {nld_film.poster_url}")
        
        # New poster URL
        new_poster_url = "https://storage.googleapis.com/pecantv_title_images/NLD_title-Img-color.png"
        
        # Update the poster URL
        nld_film.poster_url = new_poster_url
        db.commit()
        
        print(f"✅ Updated poster URL to: {new_poster_url}")
        
        # Verify the update
        updated_film = db.query(Content).filter(Content.id == 4).first()
        print(f"🔍 Verification - New poster: {updated_film.poster_url}")
        
    except Exception as e:
        print(f"❌ Error updating NLD film: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_nld_poster() 