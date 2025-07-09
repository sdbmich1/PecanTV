#!/usr/bin/env python3
"""
Restore all 30 Longstreet episodes with correct content URLs to Neon database
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

# Longstreet episodes 1-30 with titles and content URLs
LONGSTREET_EPISODES = [
    (1, "Longstreet Episode 1", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-1_2p-1080-withCredits.mp4"),
    (2, "Longstreet Episode 2", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-2_2p-1080-withCredits.mp4"),
    (3, "Longstreet Episode 3", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-3_2p-1080-withCredits.mp4"),
    (4, "Longstreet Episode 4", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-4_2p-1080-withCredits.mp4"),
    (5, "Longstreet Episode 5", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-5_2p-1080-withCredits.mp4"),
    (6, "Longstreet Episode 6", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-6_2p-1080-withCredits.mp4"),
    (7, "Longstreet Episode 7", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-7_2p-1080-withCredits.mp4"),
    (8, "Longstreet Episode 8", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-8_2p-1080-withCredits.mp4"),
    (9, "Longstreet Episode 9", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-9_2p-1080-withCredits.mp4"),
    (10, "Longstreet Episode 10", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-10_2p-1080-withCredits.mp4"),
    (11, "Longstreet Episode 11", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-11_2p-1080-withCredits.mp4"),
    (12, "Longstreet Episode 12", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-12_2p-1080-withCredits.mp4"),
    (13, "Longstreet Episode 13", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-13_2p-1080-withCredits.mp4"),
    (14, "Longstreet Episode 14", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-14_2p-1080-withCredits.mp4"),
    (15, "Longstreet Episode 15", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-15_2p-1080-withCredits.mp4"),
    (16, "Longstreet Episode 16", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-16_2p-1080-withCredits.mp4"),
    (17, "Longstreet Episode 17", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-17_2p-1080-withCredits.mp4"),
    (18, "Longstreet Episode 18", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-18_2p-1080-withCredits.mp4"),
    (19, "Longstreet Episode 19", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-19_2p-1080-withCredits.mp4"),
    (20, "Longstreet Episode 20", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-20_2p-1080-withCredits.mp4"),
    (21, "Longstreet Episode 21", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-21_2p-1080-withCredits.mp4"),
    (22, "Longstreet Episode 22", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-22_2p-1080-withCredits.mp4"),
    (23, "Longstreet Episode 23", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-23_2p-1080-withCredits.mp4"),
    (24, "Longstreet Episode 24", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-24_2p-1080-withCredits.mp4"),
    (25, "Longstreet Episode 25", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-25_2p-1080-withCredits.mp4"),
    (26, "Longstreet Episode 26", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-26_2p-1080-withCredits.mp4"),
    (27, "Longstreet Episode 27", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-27_2p-1080-withCredits.mp4"),
    (28, "Longstreet Episode 28", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-28_2p-1080-withCredits.mp4"),
    (29, "Longstreet Episode 29", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-29_2p-1080-withCredits.mp4"),
    (30, "Longstreet Episode 30", "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-30_2p-1080-withCredits.mp4"),
]

def restore_longstreet_episodes():
    print("🔧 Restoring all 30 Longstreet episodes to Neon database...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Get Longstreet series ID and UUID from Neon database
        cur.execute("SELECT id, uuid FROM content WHERE title ILIKE '%Longstreet%' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Longstreet series not found in Neon database")
            return
        series_id, series_uuid = series_record
        print(f"✅ Found Longstreet series (ID: {series_id}, UUID: {series_uuid})")
        
        # Check which episodes already exist
        cur.execute("SELECT episode_number FROM episodes WHERE series_id = %s", (series_id,))
        existing_episodes = [row[0] for row in cur.fetchall()]
        
        added_count = 0
        for episode_num, title, content_url in LONGSTREET_EPISODES:
            if episode_num not in existing_episodes:
                # Insert the episode with UUID
                cur.execute("""
                    INSERT INTO episodes (uuid, series_id, season_number, episode_number, title, content_url, poster_url, content_uuid, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    series_id,
                    1,   # season_number
                    episode_num,
                    title,
                    content_url,
                    "https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png",
                    str(series_uuid),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                print(f"  ✅ Added S1E{episode_num}: {title}")
                added_count += 1
            else:
                print(f"  ⏭️  S1E{episode_num} already exists")
        
        conn.commit()
        print(f"\n🎉 Successfully added {added_count} Longstreet episodes!")
        
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
    restore_longstreet_episodes() 