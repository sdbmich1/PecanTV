#!/usr/bin/env python3
"""
Script to cleanup miscellaneous episodes and set unknown ones to NONE
"""

from database import get_db
from models import Content, ContentType
from sqlalchemy import text

def cleanup_misc_episodes():
    """Cleanup miscellaneous episodes"""
    
    db = next(get_db())
    
    try:
        # IDs to set to NONE (unknown origin)
        none_ids = [620, 621, 622, 624]  # The Golden Cage, Death in High Places, The Double Negative, Mirror Mirror
        
        # Petrocelli episodes to remove (already in episodes table)
        petrocelli_ids = [643, 646, 653, 655]  # Jubilee Jones, The Gamblers, Death Ride, A Lonely Victim
        
        # Mike Hammer episode to remove (already in episodes table)
        mh_ids = [675]  # Play Belles' Toll
        
        print("🔍 Processing entries...")
        
        # Set unknown entries to NONE
        for id in none_ids:
            content = db.query(Content).filter(Content.id == id).first()
            if content:
                print(f"🎬 Setting {content.title} (ID {id}) poster_url to 'NONE'")
                content.poster_url = 'NONE'
            else:
                print(f"❌ ID {id} not found")
        
        # Remove Petrocelli duplicates
        for id in petrocelli_ids:
            content = db.query(Content).filter(Content.id == id).first()
            if content:
                print(f"🗑️ Removing Petrocelli duplicate: {content.title} (ID {id})")
                db.delete(content)
            else:
                print(f"❌ ID {id} not found")
        
        # Remove Mike Hammer duplicate
        for id in mh_ids:
            content = db.query(Content).filter(Content.id == id).first()
            if content:
                print(f"🗑️ Removing Mike Hammer duplicate: {content.title} (ID {id})")
                db.delete(content)
            else:
                print(f"❌ ID {id} not found")
        
        # Commit all changes
        db.commit()
        
        print("\n✅ Cleanup completed successfully!")
        print("📝 Summary:")
        print(f"   - Set {len(none_ids)} unknown entries to 'NONE'")
        print(f"   - Removed {len(petrocelli_ids)} Petrocelli duplicates")
        print(f"   - Removed {len(mh_ids)} Mike Hammer duplicate")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_misc_episodes() 