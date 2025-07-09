#!/usr/bin/env python3
"""
Script to check all series poster URL patterns to understand the correct format.
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

def check_all_series_poster_patterns():
    """Check poster URL patterns across all series."""
    print("🔍 Checking poster URL patterns across all series")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get all series with their poster URLs
        cur.execute("""
            SELECT c.id, c.title, c.poster_url
            FROM content c
            WHERE c.type = 'SERIES'
            ORDER BY c.title
        """)
        
        series_list = cur.fetchall()
        
        print(f"📺 Found {len(series_list)} series:")
        print()
        
        for series_id, title, poster_url in series_list:
            print(f"🎬 {title} (ID: {series_id})")
            print(f"   Series Poster: {poster_url}")
            
            # Get a sample episode poster URL
            cur.execute("""
                SELECT episode_number, title, poster_url
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number 
                LIMIT 1
            """, (series_id,))
            
            episode_result = cur.fetchone()
            if episode_result:
                ep_num, ep_title, ep_poster_url = episode_result
                print(f"   Episode {ep_num} Poster: {ep_poster_url}")
            else:
                print(f"   No episodes found")
            
            print()
        
        # Now check specific series that we know work well
        print("🔍 DETAILED ANALYSIS OF WORKING SERIES:")
        print("=" * 50)
        
        working_series = ['Longstreet', 'Petrocelli', 'Dragnet', 'Ghost Squad']
        
        for series_name in working_series:
            print(f"\n📺 {series_name.upper()}:")
            print("-" * 30)
            
            # Get series info
            cur.execute("""
                SELECT id, poster_url FROM content 
                WHERE title = %s AND type = 'SERIES'
            """, (series_name,))
            
            series_result = cur.fetchone()
            if series_result:
                series_id, series_poster = series_result
                print(f"  Series ID: {series_id}")
                print(f"  Series Poster: {series_poster}")
                
                # Get episode poster patterns
                cur.execute("""
                    SELECT episode_number, title, poster_url
                    FROM episodes 
                    WHERE series_id = %s 
                    ORDER BY episode_number 
                    LIMIT 3
                """, (series_id,))
                
                episodes = cur.fetchall()
                for ep_num, ep_title, ep_poster in episodes:
                    print(f"  Episode {ep_num}: {ep_poster}")
            else:
                print(f"  ❌ Series not found")
        
        # Check Count of Monte Cristo specifically
        print(f"\n📺 COUNT OF MONTE CRISTO ANALYSIS:")
        print("-" * 40)
        
        cur.execute("""
            SELECT id, poster_url FROM content 
            WHERE title = 'The Count of Monte Cristo' AND type = 'SERIES'
        """)
        
        cmc_result = cur.fetchone()
        if cmc_result:
            cmc_id, cmc_poster = cmc_result
            print(f"  Series ID: {cmc_id}")
            print(f"  Series Poster: {cmc_poster}")
            
            # Get episode poster patterns
            cur.execute("""
                SELECT episode_number, title, poster_url
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number 
                LIMIT 3
            """, (cmc_id,))
            
            cmc_episodes = cur.fetchall()
            for ep_num, ep_title, ep_poster in cmc_episodes:
                print(f"  Episode {ep_num}: {ep_poster}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_all_series_poster_patterns() 