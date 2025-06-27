#!/usr/bin/env python3
"""
Script to fix Mike Hammer episodes to have exactly 4 episodes with correct URLs.
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

SERIES_NAME = 'Mike Hammer'
EXPECTED_EPISODES = 4
SUBFOLDER = 'mike_hammer'

def fix_mike_hammer_episodes():
    """Fix Mike Hammer episodes to have exactly 4 episodes with correct URLs."""
    print("🎬 Fixing Mike Hammer Episodes")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Mike Hammer series ID
        cur.execute("""
            SELECT id, uuid, title FROM content 
            WHERE title ILIKE '%Mike Hammer%' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Mike Hammer series not found")
            return
        
        series_id, series_uuid, series_title = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        
        # Get current episodes
        cur.execute("""
            SELECT id, episode_number, title FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        current_episodes = cur.fetchall()
        print(f"📺 Current episodes: {len(current_episodes)}")
        
        # Delete all existing episodes
        if current_episodes:
            cur.execute("DELETE FROM episodes WHERE series_id = %s", (series_id,))
            print(f"🗑️  Deleted {len(current_episodes)} existing episodes")
        
        # Create 4 episodes with correct URLs
        for episode_num in range(1, EXPECTED_EPISODES + 1):
            # Generate content and poster URLs
            content_url = f"/pecantv_series/{SUBFOLDER}/MikeHammer{episode_num}.mp4"
            poster_url = f"/pecantv_series/{SUBFOLDER}/MikeHammer{episode_num}_poster.jpg"
            
            # Create episode title
            title = f"Mike Hammer Episode {episode_num}"
            
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
                f"Episode {episode_num} of Mike Hammer",
                1,  # Season number
                episode_num,
                60,  # Runtime in minutes
                content_url,
                poster_url,
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            
            print(f"  ✅ Created episode {episode_num}: {title}")
            print(f"     Content: {content_url}")
            print(f"     Poster: {poster_url}")
        
        conn.commit()
        print(f"\n✅ Successfully created {EXPECTED_EPISODES} Mike Hammer episodes")
        
        # Verify the result
        cur.execute("""
            SELECT COUNT(*) FROM episodes WHERE series_id = %s
        """, (series_id,))
        
        final_count = cur.fetchone()[0]
        print(f"📊 Final episode count: {final_count}")
        
        if final_count == EXPECTED_EPISODES:
            print("✅ Mike Hammer episodes fixed successfully!")
        else:
            print(f"⚠️  Expected {EXPECTED_EPISODES} episodes, got {final_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_mike_hammer_episodes() 