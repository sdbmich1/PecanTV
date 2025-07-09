#!/usr/bin/env python3
"""
Delete all Dragnet episodes and add only episodes 14 and 15 that actually exist
"""

import sys
import uuid
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_dragnet_episodes_correct():
    """Delete all Dragnet episodes and add only episodes that actually exist"""
    
    with engine.connect() as conn:
        print("🔧 Fixing Dragnet episodes - deleting all and adding only existing ones...")
        print("=" * 60)
        
        # First, delete ALL Dragnet episodes
        print("🗑️ Deleting ALL Dragnet episodes...")
        result = conn.execute(text("""
            DELETE FROM episodes 
            WHERE series_id = 68
        """))
        
        deleted_count = result.rowcount
        print(f"Deleted {deleted_count} episodes")
        
        # Now add only the episodes that actually exist
        print("\n➕ Adding episodes that actually exist...")
        
        # Use the existing Dragnet content UUID
        dragnet_content_uuid = "5464912e-44e7-4e1b-a320-540048f17f54"
        
        # Generate UUIDs for the new episodes
        episode1_uuid = str(uuid.uuid4())
        episode2_uuid = str(uuid.uuid4())
        
        # Add episode 14 as episode 1
        conn.execute(text("""
            INSERT INTO episodes (series_id, season_number, episode_number, title, content_url, uuid, content_uuid)
            VALUES (:series_id, :season_number, :episode_number, :title, :content_url, :uuid, :content_uuid)
        """), {
            'series_id': 68,
            'season_number': 1,
            'episode_number': 1,
            'title': 'Dragnet Animated - Episode 1',
            'content_url': 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet14_2p-1080-wCredits.mp4',
            'uuid': episode1_uuid,
            'content_uuid': dragnet_content_uuid
        })
        
        # Add episode 15 as episode 2
        conn.execute(text("""
            INSERT INTO episodes (series_id, season_number, episode_number, title, content_url, uuid, content_uuid)
            VALUES (:series_id, :season_number, :episode_number, :title, :content_url, :uuid, :content_uuid)
        """), {
            'series_id': 68,
            'season_number': 1,
            'episode_number': 2,
            'title': 'Dragnet Animated - Episode 2',
            'content_url': 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet15_2p-1080-wCredits.mp4',
            'uuid': episode2_uuid,
            'content_uuid': dragnet_content_uuid
        })
        
        print("✅ Added episodes 1 and 2 with correct URLs")
        
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
    fix_dragnet_episodes_correct() 