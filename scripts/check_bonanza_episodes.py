#!/usr/bin/env python3
"""
Script to check what Bonanza episodes are in the database.
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

def check_bonanza_episodes():
    """Check what Bonanza episodes are in the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Checking Bonanza Episodes in Database")
        print("=" * 50)
        
        # Get Bonanza series ID
        cur.execute("SELECT id FROM content WHERE title = 'Bonanza' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Bonanza series not found")
            return
        
        series_id = series_result[0]
        print(f"✅ Found Bonanza series (ID: {series_id})")
        
        # Get all Bonanza episodes
        cur.execute("""
            SELECT id, title, season_number, episode_number, content_url, poster_url
            FROM episodes 
            WHERE series_id = %s
            ORDER BY season_number, episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"\n📺 Found {len(episodes)} Bonanza episodes in database:")
        print("-" * 60)
        
        for ep_id, title, season, episode, content_url, poster_url in episodes:
            status = "✅" if content_url and content_url.strip() else "❌"
            print(f"{status} S{season:02d}E{episode:02d} - {title}")
            if content_url and content_url.strip():
                print(f"     Content URL: {content_url}")
            else:
                print(f"     Content URL: MISSING")
        
        # Count missing content URLs
        missing_count = sum(1 for _, _, _, _, content_url, _ in episodes if not content_url or not content_url.strip())
        print(f"\n📊 Summary:")
        print(f"  Total episodes: {len(episodes)}")
        print(f"  Episodes with content URLs: {len(episodes) - missing_count}")
        print(f"  Episodes missing content URLs: {missing_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_bonanza_episodes() 