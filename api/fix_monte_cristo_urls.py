#!/usr/bin/env python3
"""
Fix Count of Monte Cristo URLs to match the actual file naming convention
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_monte_cristo_urls():
    """Fix Count of Monte Cristo URLs to match actual file names"""
    
    with engine.connect() as conn:
        print("🔧 Fixing Count of Monte Cristo URLs to match actual file names...")
        print("=" * 50)
        
        # Get all Count of Monte Cristo episodes with their titles
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 72 
            ORDER BY episode_number
        """))
        
        monte_cristo_episodes = result.fetchall()
        print(f"Found {len(monte_cristo_episodes)} Count of Monte Cristo episodes")
        
        # Define the mapping of episode numbers to actual file names
        episode_file_mapping = {
            1: "CMC1-a-toy-for-the-infanta",
            2: "CMC2-marseilles", 
            3: "CMC3-the-luxembourg-affair",
            4: "CMC4-the-texas-affair",
            5: "CMC5-the-mazzini-affair",
            6: "CMC6-the-carbonari",
            7: "CMC7-the-devils-emissary",
            8: "CMC8-bordeaux",
            9: "CMC9-flight-to-carais",
            10: "CMC10-albania",
            11: "CMC11-the-coast-of-italy",
            12: "CMC12-the-act-of-terror",
            13: "CMC13-the-experiment",
            14: "CMC14-mecklenburg",
            15: "CMC15-the-portuguese-affair",
            16: "CMC16-lichtenburg",
            17: "CMC17-burgundy",
            18: "CMC18-majorca",
            19: "CMC19-sicily",
            20: "CMC20-a-matter-of-justice",
            21: "CMC21-athens",
            22: "CMC22-the-tallyrand-affair",
            23: "CMC23-the-island",
            24: "CMC24-the-barefoot-empress",
            25: "CMC25-the-grecian-gift",
            26: "CMC26-monaco",
            27: "CMC27-point-counterpoint",
            28: "CMC28-the-black-death",
            29: "CMC29-victor-hugo",
            30: "CMC30-return-to-the-chateau-dif",
            31: "CMC31-the-pen-and-the-sword",
            32: "CMC32-the-sardinian-affair",
            33: "CMC33-the-affair-of-the-three-napoleons",
            34: "CMC34-the-dubarry-affair",
            35: "CMC35-the-first-train-to-paris",
            36: "CMC36-the-golden-blade",
            37: "CMC37-the-duel",
            38: "CMC38-andorra",
            39: "CMC39-an-affair-of-honour"
        }
        
        for episode_id, episode_num, title, old_url in monte_cristo_episodes:
            if episode_num in episode_file_mapping:
                # Use the correct file name format
                file_name = episode_file_mapping[episode_num]
                gcs_url = f"https://storage.googleapis.com/pecantv_series/count_of_monte_cristo/{file_name}_2p-1080-wCredits.mp4"
                
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
        print(f"\n🎉 Successfully updated Count of Monte Cristo URLs!")

if __name__ == "__main__":
    fix_monte_cristo_urls() 