#!/usr/bin/env python3
"""
Script to update Dragnet episodes with proper content URLs.
"""

import psycopg2
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

def update_dragnet_episodes():
    """Update Dragnet episodes with proper content URLs."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        print("🎬 Updating Dragnet Episodes with Content URLs")
        print("=" * 50)
        
        # Get Dragnet series ID
        cur.execute("SELECT id FROM content WHERE title = 'Dragnet' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Dragnet series not found")
            return
        series_id = series_record[0]
        print(f"✅ Found Dragnet series (ID: {series_id})")
        
        # Update episodes with content URLs
        episode_updates = [
            (1, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet1.mp4"),
            (2, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet2.mp4"),
            (3, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet3.mp4"),
            (4, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet4.mp4"),
            (5, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet5.mp4"),
            (6, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet6.mp4"),
            (7, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet7.mp4"),
            (8, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet8.mp4"),
            (9, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet9.mp4"),
            (10, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet10.mp4"),
            (11, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet11.mp4"),
            (12, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet12.mp4"),
            (13, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet13.mp4"),
        ]
        
        updated = 0
        for episode_num, content_url in episode_updates:
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (content_url, datetime.now(timezone.utc), series_id, episode_num))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated Episode {episode_num}: {content_url}")
                updated += 1
            else:
                print(f"  ⚠️  Episode {episode_num} not found")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Dragnet episodes with content URLs.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_dragnet_episodes() 