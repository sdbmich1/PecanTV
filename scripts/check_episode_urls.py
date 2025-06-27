#!/usr/bin/env python3
"""
Script to check all episode rows in the database and verify contentURL and posterURL fields.
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

def check_episode_urls():
    """Check all episode rows and their URL fields."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking Episode URL Fields in Database")
        print("=" * 60)
        
        # Get all episodes with their series information
        cur.execute("""
            SELECT 
                e.id,
                e.title,
                e.content_url,
                e.poster_url,
                c.title as series_title,
                c.type as series_type
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            ORDER BY c.title, e.season_number, e.episode_number
        """)
        
        episodes = cur.fetchall()
        
        print(f"Found {len(episodes)} episodes in database")
        print()
        
        # Group by series
        series_episodes = {}
        for ep in episodes:
            series_name = ep['series_title']
            if series_name not in series_episodes:
                series_episodes[series_name] = []
            series_episodes[series_name].append(ep)
        
        for series_name, eps in series_episodes.items():
            print(f"📺 {series_name} ({len(eps)} episodes)")
            print("-" * 40)
            
            for ep in eps:
                content_url = ep['content_url'] or "NULL"
                poster_url = ep['poster_url'] or "NULL"
                
                print(f"  Episode {ep['id']}: {ep['title']}")
                print(f"    contentURL: {content_url}")
                print(f"    posterURL:  {poster_url}")
                
                # Check if URLs are relative paths (should be for local files)
                if content_url and not content_url.startswith('http'):
                    print(f"    ✅ contentURL is relative path")
                elif content_url and content_url.startswith('http'):
                    print(f"    🌐 contentURL is external URL")
                else:
                    print(f"    ❌ contentURL is NULL or empty")
                
                if poster_url and not poster_url.startswith('http'):
                    print(f"    ✅ posterURL is relative path")
                elif poster_url and poster_url.startswith('http'):
                    print(f"    🌐 posterURL is external URL")
                else:
                    print(f"    ❌ posterURL is NULL or empty")
                
                print()
            
            print()
        
        # Summary statistics
        print("📊 SUMMARY")
        print("=" * 40)
        
        content_urls = [ep['content_url'] for ep in episodes if ep['content_url']]
        poster_urls = [ep['poster_url'] for ep in episodes if ep['poster_url']]
        
        relative_content = [url for url in content_urls if not url.startswith('http')]
        external_content = [url for url in content_urls if url.startswith('http')]
        
        relative_posters = [url for url in poster_urls if not url.startswith('http')]
        external_posters = [url for url in poster_urls if url.startswith('http')]
        
        print(f"Total episodes: {len(episodes)}")
        print(f"Episodes with contentURL: {len(content_urls)}")
        print(f"  - Relative paths: {len(relative_content)}")
        print(f"  - External URLs: {len(external_content)}")
        print(f"Episodes with posterURL: {len(poster_urls)}")
        print(f"  - Relative paths: {len(relative_posters)}")
        print(f"  - External URLs: {len(external_posters)}")
        
        # Check for potential issues
        print("\n🔍 POTENTIAL ISSUES:")
        print("-" * 30)
        
        issues_found = False
        
        for ep in episodes:
            if not ep['content_url']:
                print(f"❌ Episode {ep['id']} ({ep['title']}) has no contentURL")
                issues_found = True
            
            if ep['content_url'] and ep['content_url'].startswith('http'):
                print(f"⚠️  Episode {ep['id']} ({ep['title']}) has external contentURL: {ep['content_url']}")
                issues_found = True
            
            if ep['poster_url'] and not ep['poster_url'].startswith('http'):
                print(f"⚠️  Episode {ep['id']} ({ep['title']}) has relative posterURL: {ep['poster_url']}")
                issues_found = True
        
        if not issues_found:
            print("✅ No obvious issues found with URL fields")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_episode_urls() 