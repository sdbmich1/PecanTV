#!/usr/bin/env python3
"""
Restore all 13 Dragnet episodes first
"""

import sys
import uuid
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def restore_dragnet_episodes():
    """Restore all 13 Dragnet episodes"""
    
    with engine.connect() as conn:
        print("🔧 Restoring all 13 Dragnet episodes...")
        print("=" * 50)
        
        # Use the existing Dragnet content UUID
        dragnet_content_uuid = "5464912e-44e7-4e1b-a320-540048f17f54"
        
        # First, delete any existing episodes
        print("🗑️ Deleting existing episodes...")
        conn.execute(text("DELETE FROM episodes WHERE series_id = 68"))
        
        # Add all 13 episodes
        print("➕ Adding all 13 episodes...")
        
        for episode_num in range(1, 14):
            episode_uuid = str(uuid.uuid4())
            
            # Use Dragnet14 for episode 1, Dragnet15 for episode 3, and normal numbering for others
            if episode_num == 1:
                filename = "Dragnet14_2p-1080-wCredits.mp4"
            elif episode_num == 3:
                filename = "Dragnet15_2p-1080-wCredits.mp4"
            else:
                filename = f"Dragnet{episode_num}_2p-1080-wCredits.mp4"
            
            conn.execute(text("""
                INSERT INTO episodes (series_id, season_number, episode_number, title, content_url, uuid, content_uuid)
                VALUES (:series_id, :season_number, :episode_number, :title, :content_url, :uuid, :content_uuid)
            """), {
                'series_id': 68,
                'season_number': 1,
                'episode_number': episode_num,
                'title': f'Dragnet Animated - Episode {episode_num}',
                'content_url': f'https://storage.googleapis.com/pecantv_series/dragnet/{filename}',
                'uuid': episode_uuid,
                'content_uuid': dragnet_content_uuid
            })
        
        print("✅ Added all 13 episodes")
        
        # Verify the changes
        print("\n🔍 Verifying changes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 
            ORDER BY episode_number
        """))
        
        dragnet_episodes = result.fetchall()
        print(f"Found {len(dragnet_episodes)} Dragnet episodes")
        
        for episode_id, episode_num, title, content_url in dragnet_episodes:
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"Episode {episode_num}: {title}")
            print(f"  URL: {content_url}")
            print(f"  Filename: {filename}")
            print()
        
        print("✅ All 13 Dragnet episodes restored!")

if __name__ == "__main__":
    restore_dragnet_episodes() 