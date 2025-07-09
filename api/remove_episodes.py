#!/usr/bin/env python3
"""
Script to remove specific episodes from the database.
"""

import sys
from sqlalchemy.orm import Session

# Add the current directory to Python path
sys.path.append('.')

from database import SessionLocal
from models import Content

def remove_episodes(episode_ids):
    """Remove episodes by ID from the database"""
    if not episode_ids:
        print("❌ No episode IDs provided")
        return
    
    db = SessionLocal()
    try:
        # Get episodes before deletion for confirmation
        episodes_to_remove = []
        for episode_id in episode_ids:
            episode = db.query(Content).filter(Content.id == episode_id).first()
            if episode:
                episodes_to_remove.append(episode)
                print(f"📺 Found episode: ID {episode.id}, Title: '{episode.title}', Type: {episode.type}")
            else:
                print(f"❌ Episode with ID {episode_id} not found")
        
        if not episodes_to_remove:
            print("❌ No episodes found to remove")
            return
        
        print(f"\n🗑️  About to remove {len(episodes_to_remove)} episodes:")
        for episode in episodes_to_remove:
            print(f"   - ID {episode.id}: '{episode.title}'")
        
        # Ask for confirmation
        response = input("\n❓ Are you sure you want to remove these episodes? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Operation cancelled")
            return
        
        # Remove episodes
        removed_count = 0
        for episode in episodes_to_remove:
            try:
                db.delete(episode)
                removed_count += 1
                print(f"✅ Removed episode: ID {episode.id}, Title: '{episode.title}'")
            except Exception as e:
                print(f"❌ Error removing episode {episode.id}: {e}")
        
        # Commit changes
        db.commit()
        print(f"\n🎉 Successfully removed {removed_count} episodes from database")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Episode IDs to remove
    episode_ids = [673, 654, 648]
    
    print("🗑️  Episode Removal Script")
    print("=" * 40)
    print(f"Target episode IDs: {episode_ids}")
    print()
    
    remove_episodes(episode_ids) 