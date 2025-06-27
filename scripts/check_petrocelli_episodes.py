#!/usr/bin/env python3
"""
Script to check current Petrocelli episodes in the database.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_petrocelli_episodes():
    """Check current Petrocelli episodes in the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking Petrocelli episodes in database...")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id, title FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series: {series_result['title']} (ID: {series_id})")
        
        # Get all Petrocelli episodes
        cur.execute("""
            SELECT id, title, episode_number, season_number, content_url, poster_url
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"\n📺 Found {len(episodes)} Petrocelli episodes:")
        print("-" * 60)
        
        for ep in episodes:
            print(f"Episode {ep['episode_number']}: {ep['title']}")
            print(f"  Content URL: {ep['content_url']}")
            print(f"  Poster URL: {ep['poster_url']}")
            print()
        
        # Check content table for Petrocelli entries
        cur.execute("""
            SELECT id, title, content_url, poster_url, trailer_url
            FROM content 
            WHERE title LIKE '%Petrocelli%' AND type = 'EPISODE'
            ORDER BY title
        """)
        
        content_episodes = cur.fetchall()
        print(f"\n📋 Found {len(content_episodes)} Petrocelli episodes in content table:")
        print("-" * 60)
        
        for ep in content_episodes:
            print(f"Title: {ep['title']}")
            print(f"  Content URL: {ep['content_url']}")
            print(f"  Poster URL: {ep['poster_url']}")
            print(f"  Trailer URL: {ep['trailer_url']}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_petrocelli_episodes() 