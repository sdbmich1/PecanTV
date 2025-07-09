#!/usr/bin/env python3
"""
Fix Lone Ranger episode content URLs.
"""

import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Database configuration
DATABASE_URL = 'postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require'

def fix_lone_ranger_urls():
    """Update Lone Ranger episodes with correct content URLs."""
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    try:
        print("🤠 Fixing Lone Ranger episode URLs...")
        
        # Define the URL mappings for the 4 episodes
        url_mappings = [
            {
                "episode_number": 1,
                "title": "Chapter 1 - Enter the Lone Ranger",
                "url": "https://storage.googleapis.com/pecantv_series/lone_ranger/LoneRanger-ch1-wCredits_1pass.mp4"
            },
            {
                "episode_number": 2,
                "title": "Chapter 2 - The Lone Ranger Fights On",
                "url": "https://storage.googleapis.com/pecantv_series/lone_ranger/LoneRanger-ch2-wCredits_1pass.mp4"
            },
            {
                "episode_number": 3,
                "title": "Chapter 3 - The Lone Ranger's Triumph",
                "url": "https://storage.googleapis.com/pecantv_series/lone_ranger/LoneRanger-ch3-wCredits_1pass.mp4"
            },
            {
                "episode_number": 4,
                "title": "Chapter 4 - Legion of Old Timers",
                "url": "https://storage.googleapis.com/pecantv_series/lone_ranger/LoneRanger-ch4-wCredits_1pass.mp4"
            }
        ]
        
        for mapping in url_mappings:
            print(f"\n   Updating Episode {mapping['episode_number']}: {mapping['title']}")
            
            # Update the content_url for this episode
            result = conn.execute(text("""
                UPDATE episodes 
                SET content_url = :url, updated_at = NOW()
                WHERE series_id = 691 AND episode_number = :episode_number
            """), {
                "url": mapping["url"],
                "episode_number": mapping["episode_number"]
            })
            
            if result.rowcount > 0:
                print(f"     ✅ Updated with URL: {mapping['url']}")
            else:
                print(f"     ❌ No episode found with episode_number {mapping['episode_number']}")
        
        # Commit all changes
        conn.commit()
        print("\n✅ All Lone Ranger episode URLs updated successfully!")
        
        # Verify the updates
        print("\n🔍 Verifying updates...")
        result = conn.execute(text("""
            SELECT episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 691 
            ORDER BY episode_number
        """))
        
        rows = result.fetchall()
        for row in rows:
            print(f"   Episode {row[0]}: {row[1]}")
            print(f"     URL: {row[2]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_lone_ranger_urls() 