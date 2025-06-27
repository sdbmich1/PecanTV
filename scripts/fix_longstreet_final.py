#!/usr/bin/env python3
"""
Script to fix Longstreet episodes to have exactly 30 episodes.
Fix missing poster URLs and add missing episodes.
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

def fix_longstreet_episodes():
    """Fix Longstreet episodes to have exactly 30 episodes."""
    print("🔧 Fixing Longstreet Episodes")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Longstreet series ID
        cur.execute("""
            SELECT id, uuid, title FROM content 
            WHERE title ILIKE '%Longstreet%' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Longstreet series not found")
            return
        
        series_id, series_uuid, series_title = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        
        # First, fix missing poster URLs for existing episodes
        print("🔧 Fixing missing poster URLs...")
        cur.execute("""
            UPDATE episodes 
            SET poster_url = 'https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png',
                updated_at = %s
            WHERE series_id = %s AND (poster_url IS NULL OR poster_url = '')
        """, (datetime.now(timezone.utc), series_id))
        
        poster_fixes = cur.rowcount
        print(f"✅ Fixed {poster_fixes} missing poster URLs")
        
        # Get current episode count
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        current_count = cur.fetchone()[0]
        print(f"📊 Current episodes: {current_count}")
        
        # Check for missing episode numbers
        cur.execute("""
            SELECT episode_number FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        existing_episodes = [row[0] for row in cur.fetchall()]
        print(f"Existing episode numbers: {existing_episodes}")
        
        # Find missing episode numbers
        missing_episodes = []
        for i in range(1, 31):  # Check episodes 1-30
            if i not in existing_episodes:
                missing_episodes.append(i)
        
        print(f"Missing episode numbers: {missing_episodes}")
        
        # Add missing episodes with placeholder content
        added_count = 0
        for episode_num in missing_episodes:
            title = f"Longstreet Episode {episode_num}"
            content_url = f"https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-{episode_num}_2p-1080-withCredits.mp4"
            poster_url = "https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png"
            
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
                f"Longstreet Episode {episode_num}",
                1,
                episode_num,
                60,  # 60 minutes runtime
                content_url,
                poster_url,
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            print(f"  ✅ Added episode {episode_num}: {title}")
            added_count += 1
        
        conn.commit()
        
        # Verify the result
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        final_count = cur.fetchone()[0]
        print(f"📊 Final episode count: {final_count}")
        
        if final_count == 30:
            print("✅ Longstreet now has exactly 30 episodes!")
            
            # Show sample of episodes
            cur.execute("""
                SELECT episode_number, title, content_url, poster_url 
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number
                LIMIT 5
            """, (series_id,))
            
            episodes = cur.fetchall()
            print("\n📺 Sample episodes:")
            for episode_number, title, content_url, poster_url in episodes:
                print(f"  S1E{episode_number}: {title}")
                print(f"    Content: {content_url}")
                print(f"    Poster: {poster_url}")
                print()
        else:
            print(f"⚠️  Expected 30 episodes, but found {final_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_longstreet_episodes() 