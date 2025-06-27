#!/usr/bin/env python3
"""
Script to verify that all Petrocelli files referenced in the database actually exist in GCS.
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

def test_file_exists(url):
    """Test if a file exists at the given URL."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def verify_petrocelli_database_files():
    """Verify that all Petrocelli files referenced in the database actually exist in GCS."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Verifying Petrocelli files referenced in database exist in GCS...")
        print("=" * 70)
        
        # Get all Petrocelli episodes from the episodes table
        cur.execute("""
            SELECT id, title, episode_number, content_url, poster_url
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES')
            ORDER BY episode_number
        """)
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} Petrocelli episodes in database")
        
        existing_files = []
        missing_files = []
        placeholder_files = []
        
        for ep in episodes:
            episode_num = ep['episode_number']
            content_url = ep['content_url']
            poster_url = ep['poster_url']
            
            print(f"\nEpisode {episode_num}: {ep['title']}")
            print(f"  Content URL: {content_url}")
            print(f"  Poster URL: {poster_url}")
            
            # Check if it's a placeholder
            if 'placeholder' in content_url:
                placeholder_files.append({
                    'episode': episode_num,
                    'title': ep['title'],
                    'url': content_url
                })
                print(f"  ❌ Placeholder file (not_available.mp4)")
                continue
            
            # Test if the content file exists
            if content_url:
                content_exists = test_file_exists(content_url)
                if content_exists:
                    existing_files.append({
                        'episode': episode_num,
                        'title': ep['title'],
                        'url': content_url,
                        'filename': content_url.split('/')[-1]
                    })
                    print(f"  ✅ Content file exists: {content_url.split('/')[-1]}")
                else:
                    missing_files.append({
                        'episode': episode_num,
                        'title': ep['title'],
                        'url': content_url,
                        'filename': content_url.split('/')[-1]
                    })
                    print(f"  ❌ Content file missing: {content_url.split('/')[-1]}")
            
            # Test if the poster file exists
            if poster_url and 'placeholder' not in poster_url:
                poster_exists = test_file_exists(poster_url)
                if poster_exists:
                    print(f"  ✅ Poster file exists: {poster_url.split('/')[-1]}")
                else:
                    print(f"  ❌ Poster file missing: {poster_url.split('/')[-1]}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("=" * 50)
        print(f"Total episodes: {len(episodes)}")
        print(f"Existing content files: {len(existing_files)}")
        print(f"Missing content files: {len(missing_files)}")
        print(f"Placeholder files: {len(placeholder_files)}")
        
        if existing_files:
            print(f"\n✅ EXISTING FILES:")
            for file in existing_files:
                print(f"  Episode {file['episode']}: {file['filename']}")
        
        if missing_files:
            print(f"\n❌ MISSING FILES:")
            for file in missing_files:
                print(f"  Episode {file['episode']}: {file['filename']}")
        
        if placeholder_files:
            print(f"\n⚠️  PLACEHOLDER FILES (need actual content):")
            for file in placeholder_files:
                print(f"  Episode {file['episode']}: {file['title']}")
        
        # Now let's test some additional files that might exist but aren't in the database
        print(f"\n🔍 Testing additional Petrocelli files that might exist...")
        print("=" * 50)
        
        # Test some additional episode titles that might exist
        additional_titles = [
            "Survival",  # You mentioned this one
            "A-Deadly-Game",
            "The-Deadly-Trap", 
            "Death-in-Small-Doses",
            "The-Deadly-Double",
            "A-Deadly-Charade",
            "The-Deadly-Connection",
            "Death-of-a-Friend",
            "The-Deadly-Truth",
            "A-Deadly-Secret",
            "The-Deadly-Web",
            "Death-by-Design",
            "The-Deadly-Plan",
            "A-Deadly-Alliance",
            "The-Deadly-Contract"
        ]
        
        base_url = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"
        additional_files = []
        
        for title in additional_titles:
            filename = f"Petrocelli-{title}_2p-1080-wCredits.mp4"
            url = base_url + filename
            if test_file_exists(url):
                additional_files.append(filename)
                print(f"  ✅ Found: {filename}")
        
        if additional_files:
            print(f"\n🎉 Found {len(additional_files)} additional files not in database:")
            for file in additional_files:
                print(f"  - {file}")
        
        total_available = len(existing_files) + len(additional_files)
        print(f"\n📈 Total available Petrocelli files: {total_available}")
        
        if total_available >= 22:
            print("🎉 SUCCESS: We have enough files for all 22 episodes!")
        else:
            print(f"⚠️  Still need {22 - total_available} more files for all episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    verify_petrocelli_database_files() 