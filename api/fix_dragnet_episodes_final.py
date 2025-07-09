#!/usr/bin/env python3
"""
Fix Dragnet episodes by replacing episodes 1 and 3 with episodes 14 and 15
"""

import sys
import uuid
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_dragnet_episodes_final():
    """Fix Dragnet episodes by replacing episodes 1 and 3 with episodes 14 and 15"""
    
    with engine.connect() as conn:
        print("🔧 Fixing Dragnet episodes - replacing episodes 1 and 3 with 14 and 15...")
        print("=" * 60)
        
        # Use the existing Dragnet content UUID
        dragnet_content_uuid = "5464912e-44e7-4e1b-a320-540048f17f54"
        
        # Generate UUIDs for the new episodes
        episode1_uuid = str(uuid.uuid4())
        episode3_uuid = str(uuid.uuid4())
        
        # Update episode 1 to use Dragnet14
        print("📝 Updating episode 1 to use Dragnet14...")
        conn.execute(text("""
            UPDATE episodes 
            SET title = 'Dragnet Animated - Episode 1',
                content_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet14_2p-1080-wCredits.mp4',
                uuid = :uuid
            WHERE series_id = 68 AND episode_number = 1
        """), {
            'uuid': episode1_uuid
        })
        
        # Update episode 3 to use Dragnet15
        print("📝 Updating episode 3 to use Dragnet15...")
        conn.execute(text("""
            UPDATE episodes 
            SET title = 'Dragnet Animated - Episode 3',
                content_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet15_2p-1080-wCredits.mp4',
                uuid = :uuid
            WHERE series_id = 68 AND episode_number = 3
        """), {
            'uuid': episode3_uuid
        })
        
        print("✅ Updated episodes 1 and 3 with correct URLs")
        
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
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"Episode {episode_num}: {title}")
            print(f"  URL: {content_url}")
            print(f"  Filename: {filename}")
            print()
        
        print("✅ Dragnet episodes fixed! Now has 13 episodes with episodes 1 and 3 using Dragnet14 and Dragnet15.")

if __name__ == "__main__":
    fix_dragnet_episodes_final() 