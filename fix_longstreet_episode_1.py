#!/usr/bin/env python3
"""
Add missing Longstreet episode 1
"""

import psycopg2
import uuid
from datetime import datetime, timezone

DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def add_longstreet_episode_1():
    print("🔧 Adding missing Longstreet episode 1...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Get Longstreet series info
        cur.execute("SELECT id, uuid FROM content WHERE title ILIKE '%Longstreet%' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Longstreet series not found")
            return
        
        series_id, series_uuid = series_record
        print(f"✅ Found Longstreet series (ID: {series_id})")
        
        # Check if episode 1 already exists
        cur.execute("SELECT id FROM episodes WHERE series_id = %s AND episode_number = 1", (series_id,))
        if cur.fetchone():
            print("⚠️  Episode 1 already exists")
            return
        
        # Add episode 1
        cur.execute("""
            INSERT INTO episodes (uuid, series_id, season_number, episode_number, title, content_url, poster_url, content_uuid, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            series_id,
            1,   # season_number
            1,   # episode_number
            "Longstreet Episode 1",
            "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-1_2p-1080-withCredits.mp4",
            "https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png",
            str(series_uuid),
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        print("✅ Added Longstreet Episode 1")
        
        # Verify total count
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        total_episodes = cur.fetchone()[0]
        print(f"📊 Total Longstreet episodes: {total_episodes}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    add_longstreet_episode_1() 