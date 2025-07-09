#!/usr/bin/env python3
"""
Fix Petrocelli episode URLs to point to the correct GCS paths
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_petrocelli_episodes():
    """Fix Petrocelli episode URLs"""
    
    with engine.begin() as conn:
        print("🔧 Fixing Petrocelli episode URLs...")
        print("=" * 50)
        
        # Petrocelli episode mappings based on the pattern from the example
        petrocelli_episodes = {
            1: "Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4",
            2: "Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4", 
            3: "Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4",
            4: "Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4",
            5: "Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4",
            6: "Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4",
            7: "Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4",
            8: "Petrocelli-Survival_2p-1080-wCredits.mp4",
            9: "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4",
            10: "Petrocelli-Once-Upon-a-Victim_2p-1080-wCredits.mp4",
            11: "Petrocelli-Counterploy_2p-1080-wCredits.mp4",
            12: "Petrocelli-By-Reason-of-Madness_2p-1080-wCredits.mp4",
            13: "Petrocelli-A-Fallen-Idol_2p-1080-wCredits.mp4"
        }
        
        print(f"Updating {len(petrocelli_episodes)} Petrocelli episodes...")
        
        for episode_number, filename in petrocelli_episodes.items():
            content_url = f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{filename}"
            
            result = conn.execute(text("""
                UPDATE episodes 
                SET content_url = :content_url
                WHERE series_id = 21 AND episode_number = :episode_number
            """), {
                'content_url': content_url,
                'episode_number': episode_number
            })
            
            if result.rowcount > 0:
                print(f"  ✅ Episode {episode_number}: {filename}")
            else:
                print(f"  ❌ Episode {episode_number}: Not found")
        
        # Verify the fixes
        print("\n🔍 Verifying Petrocelli episode fixes...")
        result = conn.execute(text("""
            SELECT episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 21 
            ORDER BY episode_number
        """))
        
        episodes = result.fetchall()
        print(f"Found {len(episodes)} Petrocelli episodes:")
        for episode_num, title, content_url in episodes:
            if content_url:
                filename = content_url.split('/')[-1]
                print(f"  Episode {episode_num}: {title} - {filename}")
            else:
                print(f"  Episode {episode_num}: {title} - NO URL")
        
        print("\n✅ Petrocelli episodes fixed!")

if __name__ == "__main__":
    fix_petrocelli_episodes() 