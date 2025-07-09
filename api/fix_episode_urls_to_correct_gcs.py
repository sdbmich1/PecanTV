#!/usr/bin/env python3
"""
Fix episode URLs to use the correct GCS format that actually exists
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_episode_urls_to_correct_gcs():
    """Fix episode URLs to use correct GCS format"""
    
    with engine.connect() as conn:
        print("🔧 Fixing episode URLs to use correct GCS format...")
        print("=" * 50)
        
        # 1. Fix Longstreet episodes - use the correct GCS format
        print("📺 Fixing Longstreet episodes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 49 
            ORDER BY episode_number
        """))
        
        longstreet_episodes = result.fetchall()
        print(f"Found {len(longstreet_episodes)} Longstreet episodes")
        
        for episode_id, episode_num, title, old_url in longstreet_episodes:
            # Use the correct GCS format that actually exists
            gcs_url = f"https://storage.googleapis.com/pecantv_series/longstreet/Longstreet{episode_num}_2p-1080-wCredits.mp4"
            
            conn.execute(text("""
                UPDATE episodes 
                SET content_url = :content_url
                WHERE id = :episode_id
            """), {
                "content_url": gcs_url,
                "episode_id": episode_id
            })
            print(f"✅ Updated Episode {episode_num}: {title}")
            print(f"   New URL: {gcs_url}")
        
        # 2. Fix Count of Monte Cristo episodes
        print("\n📺 Fixing Count of Monte Cristo episodes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 72 
            ORDER BY episode_number
        """))
        
        monte_cristo_episodes = result.fetchall()
        print(f"Found {len(monte_cristo_episodes)} Count of Monte Cristo episodes")
        
        for episode_id, episode_num, title, old_url in monte_cristo_episodes:
            # Use the correct GCS format that actually exists
            gcs_url = f"https://storage.googleapis.com/pecantv_series/count_of_monte_cristo/Count-of-Monte-Cristo-Episode-{episode_num}_2p-1080-wCredits.mp4"
            
            conn.execute(text("""
                UPDATE episodes 
                SET content_url = :content_url
                WHERE id = :episode_id
            """), {
                "content_url": gcs_url,
                "episode_id": episode_id
            })
            print(f"✅ Updated Episode {episode_num}: {title}")
            print(f"   New URL: {gcs_url}")
        
        # 3. Fix Man with a Camera episodes
        print("\n📺 Fixing Man with a Camera episodes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 700 
            ORDER BY episode_number
        """))
        
        man_with_camera_episodes = result.fetchall()
        print(f"Found {len(man_with_camera_episodes)} Man with a Camera episodes")
        
        for episode_id, episode_num, title, old_url in man_with_camera_episodes:
            # Use the correct GCS format that actually exists
            gcs_url = f"https://storage.googleapis.com/pecantv_series/man_with_a_camera/Man_with_a_Camera_Episode_{episode_num}_2p-1080-wCredits.mp4"
            
            conn.execute(text("""
                UPDATE episodes 
                SET content_url = :content_url
                WHERE id = :episode_id
            """), {
                "content_url": gcs_url,
                "episode_id": episode_id
            })
            print(f"✅ Updated Episode {episode_num}: {title}")
            print(f"   New URL: {gcs_url}")
        
        # 4. Fix Ghost Squad episodes
        print("\n📺 Fixing Ghost Squad episodes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 62 
            ORDER BY episode_number
        """))
        
        ghost_squad_episodes = result.fetchall()
        print(f"Found {len(ghost_squad_episodes)} Ghost Squad episodes")
        
        for episode_id, episode_num, title, old_url in ghost_squad_episodes:
            # Use the correct GCS format that actually exists
            gcs_url = f"https://storage.googleapis.com/pecantv_series/ghost_squad/Ghost_Squad_Episode_{episode_num}_2p-1080-wCredits.mp4"
            
            conn.execute(text("""
                UPDATE episodes 
                SET content_url = :content_url
                WHERE id = :episode_id
            """), {
                "content_url": gcs_url,
                "episode_id": episode_id
            })
            print(f"✅ Updated Episode {episode_num}: {title}")
            print(f"   New URL: {gcs_url}")
        
        conn.commit()
        print(f"\n🎉 Successfully updated all episode URLs to correct GCS format!")

if __name__ == "__main__":
    fix_episode_urls_to_correct_gcs() 