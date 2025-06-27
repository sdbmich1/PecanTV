#!/usr/bin/env python3
"""
Script to get the actual filenames from the content table for Petrocelli episodes.
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

def get_actual_petrocelli_filenames():
    """Get the actual filenames from the content table for Petrocelli episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Getting actual Petrocelli filenames from content table...")
        print("=" * 60)
        
        # Get all Petrocelli episodes with their content URLs
        cur.execute("""
            SELECT id, title, episode_number, content_url, poster_url
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES')
            ORDER BY episode_number
        """)
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} Petrocelli episodes")
        
        actual_filenames = []
        
        for ep in episodes:
            episode_num = ep['episode_number']
            content_url = ep['content_url']
            
            if content_url and 'placeholder' not in content_url:
                # Extract filename from URL
                filename = content_url.split('/')[-1]
                actual_filenames.append({
                    'episode': episode_num,
                    'title': ep['title'],
                    'filename': filename,
                    'url': content_url
                })
                print(f"Episode {episode_num}: {filename}")
        
        print(f"\n📋 All actual filenames from database:")
        print("=" * 50)
        for file in actual_filenames:
            print(f"Episode {file['episode']}: {file['filename']}")
        
        # Now test which of these actually exist in GCS
        print(f"\n🔍 Testing which files actually exist in GCS...")
        print("=" * 50)
        
        import requests
        
        def test_file_exists(url):
            try:
                response = requests.head(url, timeout=10)
                return response.status_code == 200
            except Exception as e:
                return False
        
        existing_files = []
        missing_files = []
        
        for file in actual_filenames:
            if test_file_exists(file['url']):
                existing_files.append(file)
                print(f"✅ Episode {file['episode']}: {file['filename']} - EXISTS")
            else:
                missing_files.append(file)
                print(f"❌ Episode {file['episode']}: {file['filename']} - MISSING")
        
        print(f"\n📊 SUMMARY:")
        print("=" * 30)
        print(f"Total files in database: {len(actual_filenames)}")
        print(f"Files that exist in GCS: {len(existing_files)}")
        print(f"Files missing from GCS: {len(missing_files)}")
        
        if missing_files:
            print(f"\n❌ MISSING FILES:")
            for file in missing_files:
                print(f"  Episode {file['episode']}: {file['filename']}")
        
        return actual_filenames, existing_files, missing_files
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    get_actual_petrocelli_filenames() 