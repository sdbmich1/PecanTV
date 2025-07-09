#!/usr/bin/env python3
"""
Script to fix Inframan and Lady Frankenstein issues:
1. Set Inframan poster_url to 'NONE' to hide it from display
2. Update Lady Frankenstein poster_url to correct URL
"""

from database import get_db
from models import Content, ContentType

def fix_inframan_and_lady_frankenstein():
    """Fix both Inframan and Lady Frankenstein issues"""
    
    db = next(get_db())
    
    try:
        # Fix Inframan - hide it from display
        print("🔧 Fixing Inframan...")
        inframan = db.query(Content).filter(
            Content.title == 'Inframan',
            Content.type == ContentType.FILM
        ).first()
        
        if inframan:
            print(f"🎬 Found Inframan (ID: {inframan.id})")
            print(f"📸 Current poster: {inframan.poster_url}")
            
            # Set poster_url to 'NONE' to hide from carousel
            inframan.poster_url = 'NONE'
            db.commit()
            db.refresh(inframan)
            
            print(f"✅ Updated Inframan poster to: {inframan.poster_url}")
            print("🎯 Inframan will now be hidden from carousel display")
        else:
            print("❌ Inframan not found in database")
        
        print()
        
        # Fix Lady Frankenstein - update poster URL
        print("🔧 Fixing Lady Frankenstein...")
        lady_frank = db.query(Content).filter(
            Content.title == 'Lady Frankenstein',
            Content.type == ContentType.FILM
        ).first()
        
        if lady_frank:
            print(f"🎬 Found Lady Frankenstein (ID: {lady_frank.id})")
            print(f"📸 Current poster: {lady_frank.poster_url}")
            
            # Update to correct poster URL
            correct_poster = "https://storage.googleapis.com/pecantv_title_images/Lady-Frankenstein_Title-Img.png"
            lady_frank.poster_url = correct_poster
            db.commit()
            db.refresh(lady_frank)
            
            print(f"✅ Updated Lady Frankenstein poster to: {lady_frank.poster_url}")
        else:
            print("❌ Lady Frankenstein not found in database")
            
    except Exception as e:
        print(f"❌ Error fixing content: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_inframan_and_lady_frankenstein() 