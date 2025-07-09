#!/usr/bin/env python3
"""
Fix Dragnet episode URLs in the database
"""

from database import get_db
from models import Episode
from sqlalchemy.orm import Session

def fix_dragnet_urls():
    """Fix Dragnet episode URLs to match actual files"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔧 Fixing Dragnet episode URLs...\n")
        
        # Get all Dragnet episodes
        dragnet_episodes = db.query(Episode).filter(
            Episode.series_id == 68  # Dragnet series ID
        ).all()
        
        print(f"Found {len(dragnet_episodes)} Dragnet episodes")
        
        # Check what files actually exist
        import os
        dragnet_dir = "../pecantv_series/dragnet/"
        existing_files = []
        if os.path.exists(dragnet_dir):
            for file in os.listdir(dragnet_dir):
                if file.endswith('.mp4'):
                    existing_files.append(file)
        
        print(f"Existing files: {existing_files}")
        
        # Fix URLs for episodes that have actual files
        for i, episode in enumerate(dragnet_episodes):
            print(f"\nEpisode {i+1}: {episode.title}")
            print(f"  Current URL: {episode.content_url}")
            
            # Check if we have a corresponding file
            episode_number = episode.episode_number
            expected_filename = f"Dragnet{episode_number}.mp4"
            
            if expected_filename in existing_files:
                # Fix the URL
                old_url = episode.content_url
                new_url = f"https://storage.googleapis.com/pecantv_series/dragnet/{expected_filename}"
                
                if old_url != new_url:
                    episode.content_url = new_url
                    print(f"  ✅ Fixed URL: {new_url}")
                else:
                    print(f"  ✅ URL already correct")
            else:
                print(f"  ❌ No file found for episode {episode_number}")
                # Set a placeholder or remove the URL
                episode.content_url = ""
                print(f"  ⚠️  Removed invalid URL")
        
        # Commit changes
        db.commit()
        print(f"\n✅ Fixed {len(dragnet_episodes)} Dragnet episode URLs")
        
        # Verify the fix
        print("\nVerification:")
        fixed_episodes = db.query(Episode).filter(
            Episode.series_id == 68
        ).all()
        
        for episode in fixed_episodes:
            print(f"  - {episode.title}: {episode.content_url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_dragnet_urls() 