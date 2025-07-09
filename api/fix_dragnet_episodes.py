#!/usr/bin/env python3
"""
Fix Dragnet episodes to only include episodes 14 and 15 that actually exist
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_dragnet_episodes():
    """Fix Dragnet episodes to only include episodes that actually exist"""
    
    with engine.connect() as conn:
        print("🔧 Fixing Dragnet episodes to only include episodes that actually exist...")
        print("=" * 60)
        
        # First, delete episodes 1-13 that don't have video files
        print("🗑️ Deleting episodes 1-13 that don't have video files...")
        result = conn.execute(text("""
            DELETE FROM episodes 
            WHERE series_id = 68 AND episode_number BETWEEN 1 AND 13
        """))
        
        deleted_count = result.rowcount
        print(f"Deleted {deleted_count} episodes that don't exist")
        
        # Now update episodes 14 and 15 to be episodes 1 and 2
        print("\n📝 Updating episode numbers to be sequential...")
        
        # Update episode 14 to be episode 1
        conn.execute(text("""
            UPDATE episodes 
            SET episode_number = 1, 
                title = 'Dragnet Animated - Episode 1',
                content_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet14_2p-1080-wCredits.mp4'
            WHERE series_id = 68 AND episode_number = 14
        """))
        
        # Update episode 15 to be episode 2
        conn.execute(text("""
            UPDATE episodes 
            SET episode_number = 2, 
                title = 'Dragnet Animated - Episode 2',
                content_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet15_2p-1080-wCredits.mp4'
            WHERE series_id = 68 AND episode_number = 15
        """))
        
        print("✅ Updated episode numbers to be sequential (1 and 2)")
        
        # Verify the changes
        print("\n🔍 Verifying changes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 
            ORDER BY episode_number
        """))
        
        dragnet_episodes = result.fetchall()
        print(f"Found {len(dragnet_episodes)} Dragnet episodes after fix")
        
        for episode_id, episode_num, title, content_url in dragnet_episodes:
            print(f"Episode {episode_num}: {title}")
            print(f"  URL: {content_url}")
            print()
        
        print("✅ Dragnet episodes fixed! Only episodes with actual video files remain.")

if __name__ == "__main__":
    fix_dragnet_episodes() 