#!/usr/bin/env python3
"""
Script to check the current status of Dragnet episodes in the database.
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

def check_dragnet_status():
    """Check Dragnet episodes status."""
    print("🔍 Checking Dragnet episodes status")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Dragnet series ID
        cur.execute("""
            SELECT id, title FROM content 
            WHERE title ILIKE '%Dragnet%' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Dragnet series not found")
            return
        
        series_id, series_title = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        
        # Get episodes for Dragnet
        cur.execute("""
            SELECT id, episode_number, title, content_url, poster_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        if not episodes:
            print("📺 No episodes found for Dragnet")
            return
        
        print(f"📺 Found {len(episodes)} episodes:")
        print("=" * 50)
        
        for episode in episodes:
            episode_id, episode_number, title, content_url, poster_url = episode
            content_status = "✅" if content_url else "❌"
            poster_status = "✅" if poster_url else "❌"
            
            print(f"  S1E{episode_number}: {title}")
            print(f"    Content URL: {content_status} {content_url}")
            print(f"    Poster URL: {poster_status} {poster_url}")
            print()
        
        print(f"Total episodes: {len(episodes)}")
        print(f"Expected episodes: 13")
        
        if len(episodes) == 13:
            print("✅ Correct number of episodes!")
        elif len(episodes) > 13:
            print(f"⚠️  Too many episodes - need to delete {len(episodes) - 13}")
        else:
            print(f"⚠️  Too few episodes - need to add {13 - len(episodes)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_dragnet_status() 