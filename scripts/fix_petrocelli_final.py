#!/usr/bin/env python3
"""
Simple script to fix Petrocelli episodes with the 9 actual files we have.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# The 9 actual files we found in GCS
ACTUAL_FILES = [
    "Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4",
    "Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4", 
    "Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4",
    "Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4",
    "Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4",
    "Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4",
    "Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4",
    "Petrocelli-Survival_2p-1080-wCredits.mp4",
    "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4"
]

BASE_URL = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

def fix_petrocelli_episodes():
    """Fix Petrocelli episodes with actual files for episodes 1-9, placeholders for 10-22."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing Petrocelli episodes with actual files...")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Get all episodes ordered by episode number
        cur.execute("""
            SELECT id, episode_number, title, content_url
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} episodes in database")
        
        updated_count = 0
        
        for i, ep in enumerate(episodes):
            episode_num = ep['episode_number']
            
            if i < len(ACTUAL_FILES):
                # Episodes 1-9 get actual files
                filename = ACTUAL_FILES[i]
                new_url = BASE_URL + filename
                
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_url, datetime.now(timezone.utc), ep['id']))
                
                print(f"✅ Episode {episode_num}: {filename}")
                updated_count += 1
            else:
                # Episodes 10-22 get placeholder URLs
                placeholder_url = "https://storage.googleapis.com/pecantv_series/placeholder/not_available.mp4"
                
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, updated_at = %s
                    WHERE id = %s
                """, (placeholder_url, datetime.now(timezone.utc), ep['id']))
                
                print(f"⚠️  Episode {episode_num}: placeholder (no file available)")
                updated_count += 1
        
        conn.commit()
        print(f"\n✅ Updated {updated_count} episodes")
        print(f"📝 Episodes 1-9 now have actual video files")
        print(f"📝 Episodes 10-22 have placeholder URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_petrocelli_episodes() 