#!/usr/bin/env python3
"""
Fix Ghost Squad URLs to match the actual file naming convention
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_ghost_squad_urls():
    """Fix Ghost Squad URLs to match actual file names"""
    
    with engine.connect() as conn:
        print("🔧 Fixing Ghost Squad URLs to match actual file names...")
        print("=" * 50)
        
        # Get all Ghost Squad episodes with their titles
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 62 
            ORDER BY episode_number
        """))
        
        ghost_squad_episodes = result.fetchall()
        print(f"Found {len(ghost_squad_episodes)} Ghost Squad episodes")
        
        # Define the mapping of episode numbers to actual file names
        episode_file_mapping = {
            1: "GS-The-Man-with-Delicate-Hands",
            2: "GS-The-Menacing-Mazurka", 
            3: "GS-The-Last-Jump",
            4: "GS-Ticket-for-Blackmail"
        }
        
        for episode_id, episode_num, title, old_url in ghost_squad_episodes:
            if episode_num in episode_file_mapping:
                # Use the correct file name format
                file_name = episode_file_mapping[episode_num]
                gcs_url = f"https://storage.googleapis.com/pecantv_series/ghost_squad/{file_name}_1080-wCredits.mp4"
                
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
        print(f"\n🎉 Successfully updated Ghost Squad URLs!")

if __name__ == "__main__":
    fix_ghost_squad_urls() 