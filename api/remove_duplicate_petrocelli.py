#!/usr/bin/env python3
"""
Script to remove duplicate Petrocelli episode from content table
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def remove_duplicate_petrocelli():
    """Remove duplicate Petrocelli episode from content table"""
    
    db = next(get_db())
    
    try:
        # Find the duplicate Petrocelli episode in content table
        duplicate_episode = db.query(Content).filter(
            Content.id == 433,
            Content.title == "Counterploy"
        ).first()
        
        if not duplicate_episode:
            print("❌ Duplicate Petrocelli episode (ID 433) not found in content table")
            return
        
        print(f"🎬 Found duplicate: {duplicate_episode.title}")
        print(f"📺 Type: {duplicate_episode.type}")
        print(f"🆔 ID: {duplicate_episode.id}")
        
        # Remove the duplicate entry
        db.delete(duplicate_episode)
        
        # Commit the changes
        db.commit()
        
        print(f"✅ Successfully removed duplicate episode: {duplicate_episode.title}")
        print("\n✅ Petrocelli episode cleanup completed successfully!")
        print("📝 Note: The episode already exists properly in the episodes table with series_id = 21")
        
    except Exception as e:
        print(f"❌ Error removing duplicate Petrocelli episode: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_duplicate_petrocelli() 