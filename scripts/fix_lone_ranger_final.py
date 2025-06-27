#!/usr/bin/env python3
"""
Script to fix The Lone Ranger episodes to have exactly 4 episodes.
Keep only episodes 1-4 and delete the rest.
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

def fix_lone_ranger_episodes():
    """Fix The Lone Ranger episodes to have exactly 4 episodes."""
    print("🔧 Fixing The Lone Ranger Episodes")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get The Lone Ranger series ID
        cur.execute("""
            SELECT id, title FROM content 
            WHERE title ILIKE '%Lone Ranger%' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ The Lone Ranger series not found")
            return
        
        series_id, series_title = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        
        # Get current episode count
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        current_count = cur.fetchone()[0]
        print(f"📊 Current episodes: {current_count}")
        
        # Delete episodes beyond episode 4
        cur.execute("""
            DELETE FROM episodes 
            WHERE series_id = %s AND episode_number > 4
        """, (series_id,))
        
        deleted_count = cur.rowcount
        print(f"🗑️  Deleted {deleted_count} extra episodes (episodes 5-14)")
        
        conn.commit()
        
        # Verify the result
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        final_count = cur.fetchone()[0]
        print(f"📊 Final episode count: {final_count}")
        
        if final_count == 4:
            print("✅ The Lone Ranger now has exactly 4 episodes!")
            
            # Show the remaining episodes
            cur.execute("""
                SELECT episode_number, title, content_url, poster_url 
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number
            """, (series_id,))
            
            episodes = cur.fetchall()
            print("\n📺 Remaining episodes:")
            for episode_number, title, content_url, poster_url in episodes:
                print(f"  S1E{episode_number}: {title}")
                print(f"    Content: {content_url}")
                print(f"    Poster: {poster_url}")
                print()
        else:
            print(f"⚠️  Expected 4 episodes, but found {final_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_lone_ranger_episodes()
