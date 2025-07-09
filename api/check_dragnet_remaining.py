#!/usr/bin/env python3
"""
Check what Dragnet episodes remain in the database
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_dragnet_remaining():
    """Check what Dragnet episodes remain in the database"""
    
    with engine.connect() as conn:
        print("🔍 Checking what Dragnet episodes remain in the database...")
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
        
        if dragnet_episodes:
            for episode_id, episode_num, title, content_url in dragnet_episodes:
                print(f"Episode {episode_num}: {title}")
                print(f"  URL: {content_url}")
                print()
        else:
            print("❌ No Dragnet episodes found in database!")
            print("We need to add the episodes that actually exist:")
            print("- Dragnet14_2p-1080-wCredits.mp4")
            print("- Dragnet15_2p-1080-wCredits.mp4")

if __name__ == "__main__":
    check_dragnet_remaining() 