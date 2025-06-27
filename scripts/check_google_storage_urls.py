#!/usr/bin/env python3
"""
Script to check what the actual Google Cloud Storage URLs should be for episodes.
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

def check_google_storage_urls():
    """Check what the actual Google Cloud Storage URLs should be."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking Episode URLs in Database")
        print("=" * 60)
        
        # Get sample episodes to see the URL patterns
        cur.execute("""
            SELECT e.title, e.content_url, e.poster_url, c.title as series_title
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            ORDER BY c.title, e.season_number, e.episode_number
            LIMIT 10
        """)
        
        episodes = cur.fetchall()
        
        print("📊 Sample Episode URLs:")
        print("-" * 40)
        
        for ep in episodes:
            print(f"\n🎬 {ep['series_title']} - {ep['title']}")
            print(f"  📹 Content URL: {ep['content_url']}")
            print(f"  🖼️  Poster URL: {ep['poster_url']}")
            
            # Check if content_url looks like a Google Cloud Storage URL
            if ep['content_url'] and ep['content_url'].startswith('https://storage.googleapis.com/'):
                print(f"  ✅ Content URL is Google Cloud Storage")
            elif ep['content_url'] and ep['content_url'].startswith('pecantv_series/'):
                print(f"  ⚠️  Content URL is relative path (should be Google Cloud Storage)")
            else:
                print(f"  ❓ Content URL format unknown")
            
            # Check poster URL
            if ep['poster_url'] and ep['poster_url'].startswith('https://storage.googleapis.com/'):
                print(f"  ✅ Poster URL is Google Cloud Storage")
            elif ep['poster_url'] and ep['poster_url'].startswith('pecantv_series/'):
                print(f"  ⚠️  Poster URL is relative path")
            else:
                print(f"  ❓ Poster URL format unknown")
        
        # Check URL patterns across all episodes
        print(f"\n📈 URL Pattern Analysis:")
        print("-" * 40)
        
        cur.execute("""
            SELECT 
                CASE 
                    WHEN content_url LIKE 'https://storage.googleapis.com/%' THEN 'Google Cloud Storage'
                    WHEN content_url LIKE 'pecantv_series/%' THEN 'Relative Path'
                    WHEN content_url LIKE 'http%' THEN 'Other HTTP'
                    ELSE 'Other'
                END as content_url_type,
                COUNT(*) as count
            FROM episodes 
            WHERE content_url IS NOT NULL
            GROUP BY content_url_type
        """)
        
        content_url_patterns = cur.fetchall()
        
        print("Content URL Patterns:")
        for pattern in content_url_patterns:
            print(f"  {pattern['content_url_type']}: {pattern['count']} episodes")
        
        cur.execute("""
            SELECT 
                CASE 
                    WHEN poster_url LIKE 'https://storage.googleapis.com/%' THEN 'Google Cloud Storage'
                    WHEN poster_url LIKE 'pecantv_series/%' THEN 'Relative Path'
                    WHEN poster_url LIKE 'http%' THEN 'Other HTTP'
                    ELSE 'Other'
                END as poster_url_type,
                COUNT(*) as count
            FROM episodes 
            WHERE poster_url IS NOT NULL
            GROUP BY poster_url_type
        """)
        
        poster_url_patterns = cur.fetchall()
        
        print("\nPoster URL Patterns:")
        for pattern in poster_url_patterns:
            print(f"  {pattern['poster_url_type']}: {pattern['count']} episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_google_storage_urls() 