#!/usr/bin/env python3
"""
Script to fix Dragnet episodes to have exactly 13 episodes with correct URL mapping.
"""

import psycopg2
import uuid
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

def fix_dragnet_episodes():
    """Fix Dragnet episodes to have exactly 13 episodes with correct URLs."""
    print("🔧 Fixing Dragnet Episodes")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Dragnet series ID
        cur.execute("""
            SELECT id, uuid, title FROM content 
            WHERE title ILIKE '%Dragnet%' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Dragnet series not found")
            return
        
        series_id, series_uuid, series_title = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        
        # Define the correct episode mapping
        # Episode number -> Dragnet file number
        episode_mapping = {
            1: 1,   # Dragnet1
            2: 2,   # Dragnet2  
            3: 3,   # Dragnet3
            4: 4,   # Dragnet4
            5: 5,   # Dragnet5
            6: 6,   # Dragnet6
            7: 7,   # Dragnet7
            8: 8,   # Dragnet8
            9: 9,   # Dragnet9
            10: 10, # Dragnet10
            11: 11, # Dragnet11
            12: 12, # Dragnet12
            13: 13  # Dragnet13
        }
        
        # First, delete all existing episodes
        cur.execute("DELETE FROM episodes WHERE series_id = %s", (series_id,))
        deleted_count = cur.rowcount
        print(f"🗑️  Deleted {deleted_count} existing episodes")
        
        # Insert the correct 13 episodes
        inserted = 0
        for episode_num in range(1, 14):
            dragnet_num = episode_mapping[episode_num]
            title = f"Dragnet Animated - Episode {episode_num}"
            content_url = f"https://storage.googleapis.com/pecantv_series/dragnet/Dragnet{dragnet_num}_2p-1080-wCredits.mp4"
            poster_url = "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet_title-img.png"
            
            cur.execute("""
                INSERT INTO episodes (
                    uuid, title, description, season_number, episode_number, runtime,
                    content_url, poster_url, series_id, content_uuid,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                str(uuid.uuid4()),
                title,
                f"Dragnet Animated Episode {episode_num}",
                1,
                episode_num,
                30,  # 30 minutes runtime
                content_url,
                poster_url,
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            print(f"  ✅ Added episode {episode_num}: {title}")
            inserted += 1
        
        conn.commit()
        print(f"\n✅ Successfully created {inserted} Dragnet episodes")
        
        # Verify the result
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        final_count = cur.fetchone()[0]
        print(f"📊 Final episode count: {final_count}")
        
        if final_count == 13:
            print("✅ Dragnet now has exactly 13 episodes!")
        else:
            print(f"⚠️  Expected 13 episodes, but found {final_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_dragnet_episodes() 