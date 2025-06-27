#!/usr/bin/env python3
"""
Script to check the actual Petrocelli episode titles in the database and find corresponding files.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

BASE_URL = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

def test_file_exists(filename):
    """Test if a file exists in GCS."""
    url = BASE_URL + filename
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def check_petrocelli_episode_titles():
    """Check the actual episode titles in the database and find corresponding files."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking Petrocelli episode titles in database...")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        
        # Get all episodes with their titles
        cur.execute("""
            SELECT id, episode_number, title, content_url
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} episodes in database")
        print("\nEpisode titles from database:")
        print("=" * 50)
        
        found_files = []
        missing_files = []
        
        for ep in episodes:
            episode_num = ep['episode_number']
            title = ep['title']
            
            print(f"Episode {episode_num}: {title}")
            
            # Try to find the corresponding file
            # Convert title to filename format
            title_for_filename = title.replace(" ", "-").replace("'", "").replace('"', "").replace(":", "").replace("?", "").replace("!", "").replace(".", "")
            
            # Test different filename patterns
            possible_filenames = [
                f"Petrocelli-{title_for_filename}_2p-1080-wCredits.mp4",
                f"Petrocelli-{title_for_filename}_2p-1080-full-credits.mp4",
                f"Petrocelli-{title_for_filename}_2p-1080.mp4",
                f"Petrocelli-{title_for_filename}.mp4",
                f"Petrocelli{episode_num}.mp4",
                f"Petrocelli-{episode_num}.mp4",
                f"Petrocelli-Episode-{episode_num}.mp4",
                f"Petrocelli-Episode{episode_num}.mp4"
            ]
            
            file_found = False
            for filename in possible_filenames:
                if test_file_exists(filename):
                    found_files.append({
                        'episode': episode_num,
                        'title': title,
                        'filename': filename
                    })
                    print(f"  ✅ Found: {filename}")
                    file_found = True
                    break
            
            if not file_found:
                missing_files.append({
                    'episode': episode_num,
                    'title': title
                })
                print(f"  ❌ Not found")
        
        print(f"\n📊 SUMMARY:")
        print("=" * 40)
        print(f"Total episodes: {len(episodes)}")
        print(f"Files found: {len(found_files)}")
        print(f"Files missing: {len(missing_files)}")
        
        if found_files:
            print(f"\n✅ FOUND FILES:")
            for file in found_files:
                print(f"  Episode {file['episode']}: {file['filename']}")
        
        if missing_files:
            print(f"\n❌ MISSING FILES:")
            for file in missing_files:
                print(f"  Episode {file['episode']}: {file['title']}")
        
        return found_files, missing_files
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    found_files, missing_files = check_petrocelli_episode_titles() 