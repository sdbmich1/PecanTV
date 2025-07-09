#!/usr/bin/env python3
"""
Script to update Carnival of Souls poster URL
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def update_carnival_of_souls():
    """Update Carnival of Souls poster URL"""
    
    db = next(get_db())
    
    try:
        # Find Carnival of Souls film
        carnival_film = db.query(Content).filter(
            Content.type == ContentType.FILM,
            Content.title.ilike('%carnival%')
        ).first()
        
        if not carnival_film:
            print("❌ Carnival of Souls film not found in database")
            return
        
        print(f"🎬 Found film: {carnival_film.title}")
        print(f"📸 Current poster: {carnival_film.poster_url}")
        
        # New poster URL
        new_poster_url = "https://storage.googleapis.com/pecantv_title_images/Carnival-of-souls_Title-Img.png"
        
        # Update the poster URL
        carnival_film.poster_url = new_poster_url
        db.commit()
        
        print(f"✅ Updated poster URL to: {new_poster_url}")
        
        # Verify the update
        updated_film = db.query(Content).filter(Content.id == carnival_film.id).first()
        print(f"🔍 Verification - New poster: {updated_film.poster_url}")
        
    except Exception as e:
        print(f"❌ Error updating Carnival of Souls: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_carnival_of_souls() 