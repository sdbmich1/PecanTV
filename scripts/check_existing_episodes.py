#!/usr/bin/env python3
"""
Script to check what episodes already exist for the series we're trying to process.
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

def check_existing_episodes():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Check episodes for each series
        series_to_check = [
            ('Lone Ranger', 691),
            ('Green Hornet', 692),
            ('Commando Cody - Sky Marshal of the Universe', 699)
        ]
        
        for series_name, series_id in series_to_check:
            print(f"\n📺 Episodes for {series_name} (ID: {series_id}):")
            print("=" * 50)
            
            cur.execute("""
                SELECT id, title, season_number, episode_number, content_url, poster_url
                FROM episodes 
                WHERE series_id = %s
                ORDER BY season_number, episode_number
            """, (series_id,))
            
            episodes = cur.fetchall()
            if episodes:
                for ep_id, title, season, episode, content_url, poster_url in episodes:
                    print(f"  S{season}E{episode}: {title}")
                    print(f"    Content URL: {'✅' if content_url else '❌'}")
                    print(f"    Poster URL: {'✅' if poster_url else '❌'}")
            else:
                print("  No episodes found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_existing_episodes() 