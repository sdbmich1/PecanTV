#!/usr/bin/env python3
"""
Script to check trailerURL values for films to understand the URL pattern difference.
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

def check_trailer_urls():
    """Check trailerURL values for films to understand the URL pattern."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking Trailer URLs for Films")
        print("=" * 60)
        
        # Get films with trailer URLs
        cur.execute("""
            SELECT title, trailer_url, content_url, poster_url, type
            FROM content 
            WHERE type = 'FILM' AND trailer_url IS NOT NULL AND trailer_url != ''
            ORDER BY title
            LIMIT 10
        """)
        
        films = cur.fetchall()
        
        print("📊 Sample Film Trailer URLs:")
        print("-" * 40)
        
        for film in films:
            print(f"\n🎬 {film['title']} ({film['type']})")
            print(f"  🎥 Trailer URL: {film['trailer_url']}")
            print(f"  📹 Content URL: {film['content_url']}")
            print(f"  🖼️  Poster URL: {film['poster_url']}")
            
            # Check if trailer_url looks like a Google Cloud Storage URL
            if film['trailer_url'] and film['trailer_url'].startswith('https://storage.googleapis.com/'):
                print(f"  ✅ Trailer URL is Google Cloud Storage")
            elif film['trailer_url'] and film['trailer_url'].startswith('http'):
                print(f"  ✅ Trailer URL is HTTP/HTTPS")
            elif film['trailer_url'] and film['trailer_url'].startswith('pecantv_series/'):
                print(f"  ⚠️  Trailer URL is relative path")
            else:
                print(f"  ❓ Trailer URL format unknown")
        
        # Check URL patterns across all films
        print(f"\n📈 Film Trailer URL Pattern Analysis:")
        print("-" * 40)
        
        cur.execute("""
            SELECT 
                CASE 
                    WHEN trailer_url LIKE 'https://storage.googleapis.com/%' THEN 'Google Cloud Storage'
                    WHEN trailer_url LIKE 'http%' THEN 'HTTP/HTTPS'
                    WHEN trailer_url LIKE 'pecantv_series/%' THEN 'Relative Path'
                    ELSE 'Other'
                END as trailer_url_type,
                COUNT(*) as count
            FROM content 
            WHERE type = 'FILM' AND trailer_url IS NOT NULL AND trailer_url != ''
            GROUP BY trailer_url_type
        """)
        
        trailer_url_patterns = cur.fetchall()
        
        print("Film Trailer URL Patterns:")
        for pattern in trailer_url_patterns:
            print(f"  {pattern['trailer_url_type']}: {pattern['count']} films")
        
        # Compare with episode content URLs
        print(f"\n📈 Episode Content URL Pattern Analysis:")
        print("-" * 40)
        
        cur.execute("""
            SELECT 
                CASE 
                    WHEN content_url LIKE 'https://storage.googleapis.com/%' THEN 'Google Cloud Storage'
                    WHEN content_url LIKE 'http%' THEN 'HTTP/HTTPS'
                    WHEN content_url LIKE 'pecantv_series/%' THEN 'Relative Path'
                    ELSE 'Other'
                END as content_url_type,
                COUNT(*) as count
            FROM episodes 
            WHERE content_url IS NOT NULL
            GROUP BY content_url_type
        """)
        
        episode_content_patterns = cur.fetchall()
        
        print("Episode Content URL Patterns:")
        for pattern in episode_content_patterns:
            print(f"  {pattern['content_url_type']}: {pattern['count']} episodes")
        
        # Check if there are any working examples
        print(f"\n🔍 Looking for Working Examples:")
        print("-" * 40)
        
        # Check for any content with working Google Cloud Storage URLs
        cur.execute("""
            SELECT title, trailer_url, type
            FROM content 
            WHERE trailer_url LIKE 'https://storage.googleapis.com/%'
            LIMIT 5
        """)
        
        working_examples = cur.fetchall()
        
        if working_examples:
            print("✅ Working Google Cloud Storage URLs found:")
            for example in working_examples:
                print(f"  🎬 {example['title']} ({example['type']}): {example['trailer_url']}")
        else:
            print("❌ No Google Cloud Storage URLs found in trailer_url")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_trailer_urls() 