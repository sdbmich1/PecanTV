#!/usr/bin/env python3
"""
Script to check the original file names stored in the database for Petrocelli episodes.
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

def check_original_petrocelli_filenames():
    """Check the original file names stored in the database for Petrocelli episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking original Petrocelli file names in database...")
        print("=" * 70)
        
        # Check episodes table first
        print("\n📺 EPISODES TABLE:")
        print("-" * 50)
        
        cur.execute("""
            SELECT id, episode_number, title, content_url, poster_url
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES')
            ORDER BY episode_number
        """)
        
        episodes = cur.fetchall()
        print(f"Found {len(episodes)} episodes in episodes table")
        
        episode_filenames = []
        for ep in episodes:
            content_url = ep['content_url']
            poster_url = ep['poster_url']
            
            content_filename = content_url.split('/')[-1] if content_url else 'No URL'
            poster_filename = poster_url.split('/')[-1] if poster_url else 'No URL'
            
            episode_filenames.append({
                'episode': ep['episode_number'],
                'title': ep['title'],
                'content_filename': content_filename,
                'poster_filename': poster_filename,
                'content_url': content_url,
                'poster_url': poster_url
            })
            
            print(f"Episode {ep['episode_number']}: {ep['title']}")
            print(f"  Content: {content_filename}")
            print(f"  Poster:  {poster_filename}")
            print()
        
        # Check content table for Petrocelli entries
        print("\n🎬 CONTENT TABLE:")
        print("-" * 50)
        
        cur.execute("""
            SELECT id, title, type, content_url, poster_url, description, series_name
            FROM content 
            WHERE (title ILIKE '%petrocelli%' OR series_name ILIKE '%petrocelli%')
            ORDER BY title
        """)
        
        content_entries = cur.fetchall()
        print(f"Found {len(content_entries)} Petrocelli entries in content table")
        
        content_filenames = []
        for entry in content_entries:
            content_url = entry['content_url']
            poster_url = entry['poster_url']
            
            content_filename = content_url.split('/')[-1] if content_url else 'No URL'
            poster_filename = poster_url.split('/')[-1] if poster_url else 'No URL'
            
            content_filenames.append({
                'id': entry['id'],
                'title': entry['title'],
                'type': entry['type'],
                'content_filename': content_filename,
                'poster_filename': poster_filename,
                'content_url': content_url,
                'poster_url': poster_url
            })
            
            print(f"{entry['title']} (Type: {entry['type']})")
            print(f"  Content: {content_filename}")
            print(f"  Poster:  {poster_filename}")
            print()
        
        # Summary
        print("\n📋 SUMMARY:")
        print("=" * 50)
        print("Original file names from episodes table:")
        for ep in episode_filenames:
            if 'placeholder' not in ep['content_filename']:
                print(f"  Episode {ep['episode']}: {ep['content_filename']}")
        
        print("\nOriginal file names from content table:")
        for entry in content_filenames:
            if entry['content_filename'] != 'No URL' and 'placeholder' not in entry['content_filename']:
                print(f"  {entry['title']}: {entry['content_filename']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_original_petrocelli_filenames() 