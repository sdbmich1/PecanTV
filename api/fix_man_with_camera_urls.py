#!/usr/bin/env python3
"""
Fix Man with a Camera URLs to match the actual file naming convention
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_man_with_camera_urls():
    """Fix Man with a Camera URLs to match actual file names"""
    
    with engine.connect() as conn:
        print("🔧 Fixing Man with a Camera URLs to match actual file names...")
        print("=" * 50)
        
        # Get all Man with a Camera episodes with their titles
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 700 
            ORDER BY episode_number
        """))
        
        man_with_camera_episodes = result.fetchall()
        print(f"Found {len(man_with_camera_episodes)} Man with a Camera episodes")
        
        # Define the mapping of episode numbers to actual file names
        episode_file_mapping = {
            1: "MwC-The-Killer",
            2: "MwC-Eyewitness", 
            3: "MwC-The-Man-Below"
        }
        
        for episode_id, episode_num, title, old_url in man_with_camera_episodes:
            if episode_num in episode_file_mapping:
                # Use the correct file name format
                file_name = episode_file_mapping[episode_num]
                gcs_url = f"https://storage.googleapis.com/pecantv_series/man_with_a_camera/{file_name}_with-credits.mp4"
                
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
            else:
                print(f"⚠️  No mapping found for Episode {episode_num}: {title}")
        
        conn.commit()
        print(f"\n🎉 Successfully updated Man with a Camera URLs!")

if __name__ == "__main__":
    fix_man_with_camera_urls() 