#!/usr/bin/env python3
"""
Script to verify the current status of all Bonanza episodes in the database.
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

def verify_bonanza_content_urls():
    """Verify the current status of all Bonanza episodes in the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Verifying Bonanza Episodes Content URLs")
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
        
        valid_count = 0
        missing_count = 0
        
        for ep_id, title, season, episode, content_url, poster_url in episodes:
            if content_url and content_url.strip():
                status = "✅"
                valid_count += 1
                print(f"{status} S{season:02d}E{episode:02d} - {title}")
                print(f"     Content URL: {content_url}")
            else:
                status = "❌"
                missing_count += 1
                print(f"{status} S{season:02d}E{episode:02d} - {title}")
                print(f"     Content URL: MISSING")
            
            if poster_url and poster_url.strip():
                print(f"     Poster URL: {poster_url}")
            else:
                print(f"     Poster URL: MISSING")
            print()
        
        # Summary
        print("📊 Summary:")
        print("-" * 30)
        print(f"  Total episodes: {len(episodes)}")
        print(f"  Episodes with valid content URLs: {valid_count}")
        print(f"  Episodes missing content URLs: {missing_count}")
        
        if valid_count == len(episodes):
            print(f"  ✅ ALL {len(episodes)} Bonanza episodes have valid content URLs!")
        else:
            print(f"  ⚠️  {missing_count} episodes still missing content URLs")
        
        # Check if we have exactly 13 episodes
        if len(episodes) == 13:
            print(f"  ✅ Correct number of episodes: {len(episodes)}")
        else:
            print(f"  ⚠️  Expected 13 episodes, found {len(episodes)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    verify_bonanza_content_urls() 