#!/usr/bin/env python3
"""
Script to check the current status of Count of Monte Cristo episodes in the database.
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

def check_count_of_monte_cristo_status():
    """Check Count of Monte Cristo episodes status."""
    print("🔍 Checking Count of Monte Cristo episodes status")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Count of Monte Cristo series ID
        cur.execute("""
            SELECT id, title FROM content 
            WHERE title = 'The Count of Monte Cristo' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Count of Monte Cristo series not found")
            return
        
        series_id, series_title = result
        print(f"✅ Found Count of Monte Cristo series: {series_title} (ID: {series_id})")
        
        # Get episodes for Count of Monte Cristo
        cur.execute("""
            SELECT id, episode_number, title, content_url, poster_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        if not episodes:
            print("📺 No episodes found for Count of Monte Cristo")
            return
        
        print(f"📺 Found {len(episodes)} Count of Monte Cristo episodes:")
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
    check_count_of_monte_cristo_status() 