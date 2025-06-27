#!/usr/bin/env python3
"""
Script to check the content table for Petrocelli entries and find actual video filenames.
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

def check_petrocelli_content():
    """Check the content table for Petrocelli entries."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking content table for Petrocelli entries...")
        print("=" * 70)
        
        # Get all Petrocelli entries from content table
        cur.execute("""
            SELECT id, title, type, content_url, poster_url, description, series_name
            FROM content 
            WHERE title ILIKE '%petrocelli%' OR series_name ILIKE '%petrocelli%'
            ORDER BY title
        """)
        
        content_entries = cur.fetchall()
        
        if not content_entries:
            print("❌ No Petrocelli entries found in content table")
            return
        
        print(f"📺 Found {len(content_entries)} Petrocelli entries in content table")
        print("=" * 70)
        
        for entry in content_entries:
            print(f"\n🎬 {entry['title']} (Type: {entry['type']})")
            print(f"  ID: {entry['id']}")
            print(f"  Series Name: {entry['series_name']}")
            print(f"  Content URL: {entry['content_url']}")
            print(f"  Poster URL: {entry['poster_url']}")
            print(f"  Description: {entry['description'][:100]}...")
            
            # Extract filename from content_url
            if entry['content_url']:
                filename = entry['content_url'].split('/')[-1]
                print(f"  Filename: {filename}")
        
        # Now let's see if we can match these to episodes
        print("\n" + "=" * 70)
        print("🔍 Checking if content entries match episode data...")
        
        # Get episodes that don't have proper content_urls
        cur.execute("""
            SELECT id, episode_number, title, content_url
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES')
            AND content_url LIKE '%placeholder%' OR content_url LIKE '%not_available%'
            ORDER BY episode_number
        """)
        
        missing_episodes = cur.fetchall()
        
        if missing_episodes:
            print(f"⚠️  Found {len(missing_episodes)} episodes with placeholder URLs:")
            for ep in missing_episodes:
                print(f"  Episode {ep['episode_number']}: {ep['title']}")
        
        # Let's also check if there are any content entries that could be episodes
        cur.execute("""
            SELECT id, title, content_url, series_name
            FROM content 
            WHERE (title ILIKE '%petrocelli%' OR series_name ILIKE '%petrocelli%')
            AND type != 'SERIES'
            AND content_url IS NOT NULL
            ORDER BY title
        """)
        
        potential_episodes = cur.fetchall()
        
        if potential_episodes:
            print(f"\n🎯 Found {len(potential_episodes)} potential episode files:")
            for item in potential_episodes:
                filename = item['content_url'].split('/')[-1] if item['content_url'] else 'No URL'
                print(f"  {item['title']} -> {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_petrocelli_content() 