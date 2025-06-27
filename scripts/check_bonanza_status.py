#!/usr/bin/env python3
"""
Script to check the current status of Bonanza episodes in the database.
"""

import psycopg2

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_bonanza_status():
    """Check Bonanza episodes status."""
    print("🔍 Checking Bonanza episodes status")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Bonanza series ID
        cur.execute("""
            SELECT id, title FROM content 
            WHERE title = 'Bonanza' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Bonanza series not found")
            return
        
        series_id, series_title = result
        print(f"✅ Found Bonanza series: {series_title} (ID: {series_id})")
        
        # Get episodes for Bonanza
        cur.execute("""
            SELECT id, episode_number, title, content_url, poster_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        if not episodes:
            print("📺 No episodes found for Bonanza")
            return
        
        print(f"📺 Found {len(episodes)} Bonanza episodes:")
        print("=" * 50)
        
        for episode in episodes:
            episode_id, episode_number, title, content_url, poster_url = episode
            content_status = "✅" if content_url else "❌"
            poster_status = "✅" if poster_url else "❌"
            
            print(f"  S1E{episode_number}: {title}")
            print(f"    Content URL: {content_status} {content_url}")
            print(f"    Poster URL: {poster_status} {poster_url}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_bonanza_status() 