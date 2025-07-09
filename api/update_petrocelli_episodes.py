#!/usr/bin/env python3
"""
Script to update Petrocelli episodes to correct type and parent series
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def update_petrocelli_episodes():
    """Update Petrocelli episodes to EPISODE type and set parent series"""
    
    db = next(get_db())
    
    try:
        # Find Petrocelli episodes by ID
        episode_433 = db.query(Content).filter(
            Content.id == 433
        ).first()
        
        if not episode_433:
            print("❌ Episode 433 not found in database")
            return
        
        print(f"🎬 Found content: {episode_433.title}")
        print(f"📺 Current type: {episode_433.type}")
        print(f"👥 Current parent: {episode_433.parent_id}")
        
        # Update type to EPISODE
        episode_433.type = ContentType.EPISODE
        
        # Set parent to Petrocelli series (ID 21)
        episode_433.parent_id = 21
        
        # Commit the changes
        db.commit()
        
        # Verify the change
        db.refresh(episode_433)
        print(f"✅ Updated type to: {episode_433.type}")
        print(f"✅ Updated parent to: {episode_433.parent_id}")
        print(f"🎬 Content: {episode_433.title}")
        
        print("\n✅ Petrocelli episode update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating Petrocelli episodes: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_petrocelli_episodes() 