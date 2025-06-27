#!/usr/bin/env python3
"""
Script to fix Commando Cody episode URLs to point to the correct local folder structure.
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

def fix_commando_cody_urls():
    """Update Commando Cody episode URLs to use local folder structure."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        print("🎬 Fixing Commando Cody Episode URLs")
        print("=" * 50)
        
        # Get Commando Cody series ID
        cur.execute("SELECT id FROM content WHERE title = 'Commando Cody - Sky Marshal of the Universe'")
        series_id = cur.fetchone()[0]
        print(f"✅ Found Commando Cody series ID: {series_id}")
        
        # Get all episodes for this series
        cur.execute("SELECT id, title, content_url, poster_url FROM episodes WHERE series_id = %s", (series_id,))
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} episodes to update")
        
        updated = 0
        for episode_id, title, content_url, poster_url in episodes:
            # Extract chapter number from title
            if "Chapter" in title:
                chapter_num = title.split("Chapter")[1].split("-")[0].strip()
                # Create new URLs pointing to local folder
                new_content_url = f"commando_cody/Commando-Cody-ch{chapter_num}.mp4"
                new_poster_url = f"commando_cody/Commando-Cody-ch{chapter_num}_poster.jpg"
                
                # Update the database
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, poster_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode_id))
                
                print(f"  ✅ Updated episode {episode_id}: {title}")
                print(f"     Content URL: {content_url} → {new_content_url}")
                print(f"     Poster URL: {poster_url} → {new_poster_url}")
                updated += 1
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated} Commando Cody episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_commando_cody_urls() 