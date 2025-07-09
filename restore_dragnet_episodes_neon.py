#!/usr/bin/env python3
"""
Restore all 13 Dragnet episodes with correct content URLs to Neon database
"""

import psycopg2
from datetime import datetime, timezone

DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# Dragnet episodes 1-13 with titles and content URLs
DRAGNET_EPISODES = [
    (1, "The Human Bomb", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet1.mp4"),
    (2, "The Big Phone", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet2.mp4"),
    (3, "The Big Cast", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet3.mp4"),
    (4, "The Big Sorrow", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet4.mp4"),
    (5, "The Big Deal", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet5.mp4"),
    (6, "The Big Break", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet6.mp4"),
    (7, "The Big Barbeque", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet7.mp4"),
    (8, "The Big Book", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet8.mp4"),
    (9, "The Big Bullet", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet9.mp4"),
    (10, "The Big Boys", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet10.mp4"),
    (11, "The Big Betty", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet11.mp4"),
    (12, "The Big Baby", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet12.mp4"),
    (13, "The Big Ad", "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet13.mp4"),
]

def restore_dragnet_episodes():
    print("🔧 Restoring all 13 Dragnet episodes to Neon database...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Get Dragnet series ID from Neon database
        cur.execute("SELECT id FROM content WHERE title = 'Dragnet' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Dragnet series not found in Neon database")
            return
        series_id = series_record[0]
        print(f"✅ Found Dragnet series (ID: {series_id})")
        
        # Check which episodes already exist
        cur.execute("SELECT episode_number FROM episodes WHERE series_id = %s", (series_id,))
        existing_episodes = [row[0] for row in cur.fetchall()]
        
        added_count = 0
        for episode_num, title, content_url in DRAGNET_EPISODES:
            if episode_num not in existing_episodes:
                # Insert the episode
                cur.execute("""
                    INSERT INTO episodes (series_id, season_number, episode_number, title, content_url, poster_url, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    series_id,
                    1,   # season_number
                    episode_num,
                    title,
                    content_url,
                    f"https://storage.googleapis.com/pecantv_series/dragnet/Dragnet{episode_num}_poster.jpg",
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                print(f"  ✅ Added S1E{episode_num}: {title}")
                added_count += 1
            else:
                print(f"  ⏭️  S1E{episode_num} already exists")
        
        conn.commit()
        print(f"\n🎉 Successfully added {added_count} Dragnet episodes!")
        
        # Verify total count
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        total_episodes = cur.fetchone()[0]
        print(f"📊 Total Dragnet episodes: {total_episodes}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    restore_dragnet_episodes() 