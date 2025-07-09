#!/usr/bin/env python3
"""
Fix Longstreet URLs to match the actual file naming convention
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_longstreet_urls():
    """Fix Longstreet URLs to match actual file names"""
    
    with engine.connect() as conn:
        print("🔧 Fixing Longstreet URLs to match actual file names...")
        print("=" * 50)
        
        # Get all Longstreet episodes with their titles
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 49 
            ORDER BY episode_number
        """))
        
        longstreet_episodes = result.fetchall()
        print(f"Found {len(longstreet_episodes)} Longstreet episodes")
        
        # Define the mapping of episode numbers to actual file names
        episode_file_mapping = {
            1: "Longstreet-I-See-Said-the-Blind-Man",
            2: "Longstreet-Beginnings", 
            3: "Longstreet-Longstreet-Episode-3",
            4: "Longstreet-So-Whos-Fred-Hornbeck",
            5: "Longstreet-Elegy-in-Brass",
            6: "Longstreet-Spell-Legacy-Like-Death",
            7: "Longstreet-The-Shape-of-Nightmares",
            8: "Longstreet-The-Girl-with-the-Broom",
            9: "Longstreet-Wednesdays-Child",
            10: "Longstreet-Longstreet-Episode-10",
            11: "Longstreet-This-Little-Piggy-Went-to-Marquette",
            12: "Longstreet-There-Was-a-Crooked-Man",
            13: "Longstreet-The-Old-Team-Spirit",
            14: "Longstreet-The-Long-Way-Home",
            15: "Longstreet-Let-the-Memories-Be-Happy-Ones",
            16: "Longstreet-Survival-Times-Two",
            17: "Longstreet-Eye-of-the-Storm",
            18: "Longstreet-Please-Leave-the-Wreck-for-Others-to-Enjoy",
            19: "Longstreet-Anatomy-of-a-Mayday",
            20: "Longstreet-Sad-Songs-and-Other-Conversations",
            21: "Longstreet-Field-of-Honor",
            22: "Longstreet-Through-Shattering-Glass",
            23: "Longstreet-Longstreet-Episode-23",
            24: "Longstreet-Longstreet-Episode-24",
            25: "Longstreet-Longstreet-Episode-25",
            26: "Longstreet-Longstreet-Episode-26",
            27: "Longstreet-Longstreet-Episode-27",
            28: "Longstreet-Longstreet-Episode-28",
            29: "Longstreet-Longstreet-Episode-29",
            30: "Longstreet-Longstreet-Episode-30"
        }
        
        for episode_id, episode_num, title, old_url in longstreet_episodes:
            if episode_num in episode_file_mapping:
                # Use the correct file name format
                file_name = episode_file_mapping[episode_num]
                gcs_url = f"https://storage.googleapis.com/pecantv_series/longstreet/{file_name}_2p-1080-withCredits.mp4"
                
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
        print(f"\n🎉 Successfully updated Longstreet URLs!")

if __name__ == "__main__":
    fix_longstreet_urls() 