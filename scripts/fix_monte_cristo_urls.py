#!/usr/bin/env python3
"""
Script to fix The Count of Monte Cristo URLs to use correct subfolder name.
Change from 'the_count_of_monte_cristo' to 'count_of_monte_cristo'
"""

import psycopg2
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

def fix_monte_cristo_urls():
    """Fix The Count of Monte Cristo URLs to use correct subfolder name."""
    print("🔧 Fixing The Count of Monte Cristo URLs")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get The Count of Monte Cristo series ID
        cur.execute("""
            SELECT id, title FROM content 
            WHERE title ILIKE '%Count of Monte Cristo%' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ The Count of Monte Cristo series not found")
            return
        
        series_id, series_title = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        
        # Update content URLs
        updated_content = cur.execute("""
            UPDATE episodes 
            SET content_url = REPLACE(content_url, 'pecantv_series/the_count_of_monte_cristo/', 'pecantv_series/count_of_monte_cristo/'),
                poster_url = REPLACE(poster_url, 'pecantv_series/the_count_of_monte_cristo/', 'pecantv_series/count_of_monte_cristo/'),
                updated_at = %s
            WHERE series_id = %s
        """, (datetime.now(timezone.utc), series_id))
        
        # Get count of updated rows
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        episode_count = cur.fetchone()[0]
        
        conn.commit()
        
        print(f"✅ Updated {episode_count} episodes")
        print("✅ Changed URLs from 'the_count_of_monte_cristo' to 'count_of_monte_cristo'")
        
        # Show sample of updated URLs
        cur.execute("""
            SELECT episode_number, title, content_url, poster_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number 
            LIMIT 3
        """, (series_id,))
        
        samples = cur.fetchall()
        print("\n📺 Sample updated URLs:")
        for episode_number, title, content_url, poster_url in samples:
            print(f"  S1E{episode_number}: {title}")
            print(f"    Content: {content_url}")
            print(f"    Poster: {poster_url}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_monte_cristo_urls() 