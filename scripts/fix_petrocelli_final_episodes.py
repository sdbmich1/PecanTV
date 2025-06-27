#!/usr/bin/env python3
"""
Script to fix Petrocelli episode URLs to point to the correct petrocelli_final_episodes folder.
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

def fix_petrocelli_final_episodes():
    """Fix Petrocelli episode URLs to point to the correct petrocelli_final_episodes folder."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing Petrocelli Episode URLs to petrocelli_final_episodes folder")
        print("=" * 70)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Get all Petrocelli episodes
        cur.execute("""
            SELECT id, title, content_url, poster_url, episode_number 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"Found {len(episodes)} Petrocelli episodes")
        
        updated = 0
        for episode in episodes:
            old_content_url = episode['content_url']
            old_poster_url = episode['poster_url']
            
            # Fix content URL
            if '/petrocelli/Petrocelli' in old_content_url:
                new_content_url = old_content_url.replace('/petrocelli/Petrocelli', '/petrocelli_final_episodes/Petrocelli')
            else:
                new_content_url = old_content_url
            
            # Fix poster URL
            if '/petrocelli/Petrocelli' in old_poster_url:
                new_poster_url = old_poster_url.replace('/petrocelli/Petrocelli', '/petrocelli_final_episodes/Petrocelli')
            else:
                new_poster_url = old_poster_url
            
            # Update the episode URLs
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, poster_url = %s, updated_at = %s
                WHERE id = %s
            """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode['id']))
            
            print(f"  ✅ Episode {episode['episode_number']}:")
            print(f"     Content: {old_content_url} → {new_content_url}")
            print(f"     Poster:  {old_poster_url} → {new_poster_url}")
            updated += 1
        
        conn.commit()
        print(f"\n✅ Updated {updated} Petrocelli episode URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_petrocelli_final_episodes() 