#!/usr/bin/env python3
"""
Script to check content URLs for Longstreet and Petrocelli episodes in the episodes table.
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

def check_episode_content_urls():
    """Check content URLs for Longstreet and Petrocelli episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Checking Episode Content URLs")
        print("=" * 50)
        
        # Check Longstreet episodes
        print("\n📺 Longstreet Episodes:")
        print("-" * 30)
        cur.execute("""
            SELECT e.id, e.title, e.season_number, e.episode_number, e.content_url,
                   CASE 
                       WHEN e.content_url IS NULL THEN 'NULL'
                       WHEN e.content_url = '' THEN 'EMPTY'
                       ELSE 'VALID'
                   END as url_status
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE c.title = 'Longstreet'
            ORDER BY e.season_number, e.episode_number
        """)
        
        longstreet_episodes = cur.fetchall()
        if not longstreet_episodes:
            print("❌ No Longstreet episodes found")
        else:
            null_count = 0
            empty_count = 0
            valid_count = 0
            
            for ep in longstreet_episodes:
                ep_id, title, season, episode, content_url, status = ep
                print(f"  S{season:02d}E{episode:02d} - {title}")
                print(f"    Content URL: {content_url}")
                print(f"    Status: {status}")
                print()
                
                if status == 'NULL':
                    null_count += 1
                elif status == 'EMPTY':
                    empty_count += 1
                else:
                    valid_count += 1
            
            print(f"📊 Longstreet Summary:")
            print(f"  Total episodes: {len(longstreet_episodes)}")
            print(f"  Valid URLs: {valid_count}")
            print(f"  Empty URLs: {empty_count}")
            print(f"  Null URLs: {null_count}")
        
        # Check Petrocelli episodes
        print("\n📺 Petrocelli Episodes:")
        print("-" * 30)
        cur.execute("""
            SELECT e.id, e.title, e.season_number, e.episode_number, e.content_url,
                   CASE 
                       WHEN e.content_url IS NULL THEN 'NULL'
                       WHEN e.content_url = '' THEN 'EMPTY'
                       ELSE 'VALID'
                   END as url_status
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE c.title = 'Petrocelli'
            ORDER BY e.season_number, e.episode_number
        """)
        
        petrocelli_episodes = cur.fetchall()
        if not petrocelli_episodes:
            print("❌ No Petrocelli episodes found")
        else:
            null_count = 0
            empty_count = 0
            valid_count = 0
            
            for ep in petrocelli_episodes:
                ep_id, title, season, episode, content_url, status = ep
                print(f"  S{season:02d}E{episode:02d} - {title}")
                print(f"    Content URL: {content_url}")
                print(f"    Status: {status}")
                print()
                
                if status == 'NULL':
                    null_count += 1
                elif status == 'EMPTY':
                    empty_count += 1
                else:
                    valid_count += 1
            
            print(f"📊 Petrocelli Summary:")
            print(f"  Total episodes: {len(petrocelli_episodes)}")
            print(f"  Valid URLs: {valid_count}")
            print(f"  Empty URLs: {empty_count}")
            print(f"  Null URLs: {null_count}")
        
        # Overall summary
        print("\n📊 Overall Summary:")
        print("-" * 30)
        cur.execute("""
            SELECT 
                COUNT(*) as total_episodes,
                COUNT(CASE WHEN content_url IS NULL THEN 1 END) as null_urls,
                COUNT(CASE WHEN content_url = '' THEN 1 END) as empty_urls,
                COUNT(CASE WHEN content_url IS NOT NULL AND content_url != '' THEN 1 END) as valid_urls
            FROM episodes
        """)
        
        overall = cur.fetchone()
        total, null_count, empty_count, valid_count = overall
        
        print(f"  Total episodes in database: {total}")
        print(f"  Episodes with valid URLs: {valid_count}")
        print(f"  Episodes with empty URLs: {empty_count}")
        print(f"  Episodes with null URLs: {null_count}")
        
        if null_count > 0 or empty_count > 0:
            print(f"\n⚠️  Found {null_count + empty_count} episodes with missing content URLs!")
        else:
            print(f"\n✅ All episodes have valid content URLs!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_episode_content_urls() 