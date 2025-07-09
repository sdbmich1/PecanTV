#!/usr/bin/env python3
"""
Check what Dragnet episodes actually exist and what their file names should be
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_dragnet_actual_episodes():
    """Check what Dragnet episodes actually exist"""
    
    with engine.connect() as conn:
        print("🔍 Checking what Dragnet episodes actually exist...")
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
        
        for episode_id, episode_num, title, content_url in dragnet_episodes:
            print(f"Episode {episode_num}: {title}")
            print(f"  Current URL: {content_url}")
            print()
        
        # Check what episodes we think should exist based on file naming
        print("📁 Based on file naming pattern, these episodes should exist:")
        print("Dragnet14_2p-1080-wCredits.mp4")
        print("Dragnet15_2p-1080-wCredits.mp4")
        print()
        
        # Ask user what other episodes exist
        print("❓ What other Dragnet episodes actually exist in GCS?")
        print("Please provide the actual file names like:")
        print("- Dragnet14_2p-1080-wCredits.mp4")
        print("- Dragnet15_2p-1080-wCredits.mp4")
        print("- etc.")

if __name__ == "__main__":
    check_dragnet_actual_episodes() 