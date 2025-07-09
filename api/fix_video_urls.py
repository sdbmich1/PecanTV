#!/usr/bin/env python3
"""
Fix video URLs to use local paths instead of GCS
"""

from database import get_db
from models import Episode
from sqlalchemy.orm import Session
import os

def fix_video_urls():
    """Fix video URLs to use local paths"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔧 Fixing video URLs to use local paths...\n")
        
        # Get all episodes with video content
        episodes = db.query(Episode).filter(
            Episode.content_url.isnot(None),
            Episode.content_url != ""
        ).all()
        
        print(f"Found {len(episodes)} episodes with video content")
        
        # Check what video files actually exist locally
        video_files = {}
        for root, dirs, files in os.walk("../pecantv_series"):
            for file in files:
                if file.endswith('.mp4'):
                    # Get the series name from the path
                    path_parts = root.split('/')
                    if len(path_parts) >= 2:
                        series_name = path_parts[-1]
                        video_files[series_name] = video_files.get(series_name, []) + [file]
        
        print(f"Found local video files: {video_files}")
        
        # Fix URLs for episodes that have local files
        fixed_count = 0
        for episode in episodes:
            # Extract series name from the current URL
            if "storage.googleapis.com/pecantv_series/" in episode.content_url:
                # Extract series name from GCS URL
                url_parts = episode.content_url.split('/')
                if len(url_parts) >= 5:
                    series_name = url_parts[4]  # pecantv_series/[series_name]/...
                    
                    # Check if we have local files for this series
                    if series_name in video_files:
                        # Find the corresponding episode file
                        episode_number = episode.episode_number
                        expected_filename = f"{series_name.capitalize()}{episode_number}.mp4"
                        
                        if expected_filename in video_files[series_name]:
                            # Update to local path
                            old_url = episode.content_url
                            new_url = f"http://localhost:8000/pecantv_series/{series_name}/{expected_filename}"
                            
                            if old_url != new_url:
                                episode.content_url = new_url
                                print(f"✅ Fixed {episode.title}: {new_url}")
                                fixed_count += 1
                            else:
                                print(f"✅ Already correct: {episode.title}")
                        else:
                            print(f"❌ No local file for {episode.title} (expected: {expected_filename})")
                            # Remove invalid URL
                            episode.content_url = ""
                    else:
                        print(f"❌ No local files for series: {series_name}")
                        # Remove invalid URL
                        episode.content_url = ""
        
        # Commit changes
        db.commit()
        print(f"\n✅ Fixed {fixed_count} video URLs")
        
        # Verify the fix
        print("\nVerification:")
        fixed_episodes = db.query(Episode).filter(
            Episode.content_url.isnot(None),
            Episode.content_url != ""
        ).all()
        
        for episode in fixed_episodes[:5]:  # Show first 5
            print(f"  - {episode.title}: {episode.content_url}")
        
        if len(fixed_episodes) > 5:
            print(f"  ... and {len(fixed_episodes) - 5} more")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_video_urls() 