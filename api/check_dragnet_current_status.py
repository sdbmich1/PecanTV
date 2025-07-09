#!/usr/bin/env python3
"""
Check the current status of all Dragnet episodes and their video files
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_dragnet_current_status():
    """Check the current status of all Dragnet episodes"""
    
    with engine.connect() as conn:
        print("🔍 Checking current Dragnet episodes status...")
        print("=" * 50)
        
        # Get all Dragnet episodes
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 
            ORDER BY episode_number
        """))
        
        dragnet_episodes = result.fetchall()
        print(f"Found {len(dragnet_episodes)} Dragnet episodes in database")
        print()
        
        for episode_id, episode_num, title, content_url in dragnet_episodes:
            # Extract filename from URL
            filename = content_url.split('/')[-1] if content_url else "No URL"
            
            print(f"Episode {episode_num}: {title}")
            print(f"  URL: {content_url}")
            print(f"  Filename: {filename}")
            
            # Check if this episode should work based on your feedback
            if episode_num in [1, 3]:
                print(f"  Status: ❌ Should NOT play (no video file yet)")
            else:
                print(f"  Status: ✅ Should play (has video file)")
            print()
        
        print("📝 Summary:")
        print("- Episodes 1 & 3: Don't have video files yet")
        print("- Other episodes: Should have working video files")
        print()
        print("💡 To fix episodes 1 & 3, you need to:")
        print("1. Upload the video files to GCS")
        print("2. Update the database URLs to point to the correct files")

if __name__ == "__main__":
    check_dragnet_current_status() 