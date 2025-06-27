#!/usr/bin/env python3
"""
Script to list all files from the GCS petrocelli_final_episodes folder and map them to episodes.
"""

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
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

# GCS URL for Petrocelli files
GCS_URL = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

def list_gcs_petrocelli_files():
    """List all files from the GCS petrocelli_final_episodes folder."""
    print("🔍 Listing all files from GCS petrocelli_final_episodes folder...")
    print("=" * 70)
    
    # Since GCS doesn't provide directory listings via HTTP, we'll test common patterns
    # based on what we know exists and what we found in the database
    
    # Files we know exist from our previous testing
    known_files = [
        "Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4",
        "Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4", 
        "Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4",
        "Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4",
        "Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4",
        "Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4",
        "Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4",
        "Petrocelli-Survival_2p-1080-wCredits.mp4",
        "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4"
    ]
    
    # Additional files that might exist (based on common Petrocelli episode titles)
    additional_files = [
        "Petrocelli-Once-Upon-A-Victim_2p-1080-wCredits.mp4",  # Fix the missing one
        "Petrocelli-A-Deadly-Game_2p-1080-wCredits.mp4",
        "Petrocelli-The-Deadly-Trap_2p-1080-wCredits.mp4",
        "Petrocelli-The-Deadly-Double_2p-1080-wCredits.mp4",
        "Petrocelli-A-Deadly-Charade_2p-1080-wCredits.mp4",
        "Petrocelli-The-Deadly-Connection_2p-1080-wCredits.mp4",
        "Petrocelli-Death-of-a-Friend_2p-1080-wCredits.mp4",
        "Petrocelli-The-Deadly-Truth_2p-1080-wCredits.mp4",
        "Petrocelli-A-Deadly-Secret_2p-1080-wCredits.mp4",
        "Petrocelli-The-Deadly-Web_2p-1080-wCredits.mp4",
        "Petrocelli-Death-by-Design_2p-1080-wCredits.mp4",
        "Petrocelli-The-Deadly-Plan_2p-1080-wCredits.mp4",
        "Petrocelli-A-Deadly-Alliance_2p-1080-wCredits.mp4",
        "Petrocelli-The-Deadly-Contract_2p-1080-wCredits.mp4"
    ]
    
    all_test_files = known_files + additional_files
    
    def test_file_exists(filename):
        """Test if a file exists in GCS."""
        url = GCS_URL + filename
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            return False
    
    existing_files = []
    
    print("Testing known files...")
    for filename in known_files:
        if test_file_exists(filename):
            existing_files.append(filename)
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename}")
    
    print("\nTesting additional files...")
    for filename in additional_files:
        if test_file_exists(filename):
            existing_files.append(filename)
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename}")
    
    print(f"\n📊 SUMMARY:")
    print("=" * 40)
    print(f"Total files found: {len(existing_files)}")
    
    if existing_files:
        print(f"\n📋 All existing files:")
        for i, filename in enumerate(existing_files, 1):
            print(f"  {i:2d}. {filename}")
    
    return existing_files

def map_files_to_episodes(existing_files):
    """Map the existing files to episodes that need content."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print(f"\n🔧 Mapping {len(existing_files)} files to episodes...")
        print("=" * 50)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        
        print(f"[DEBUG] series_id: {series_id} (type: {type(series_id)})")
        # Get episodes that need content (have placeholder URLs)
        query = (
            "SELECT id, episode_number, title, content_url "
            "FROM episodes "
            "WHERE series_id = %s "
            "AND content_url LIKE '%placeholder%' "
            "ORDER BY episode_number"
        )
        print(f"[DEBUG] Query: {query}")
        cur.execute(query, (series_id,))
        
        episodes_needing_content = cur.fetchall()
        print(f"Found {len(episodes_needing_content)} episodes needing content")
        
        print(f"\n[DEBUG] Number of episodes needing content: {len(episodes_needing_content)}")
        print(f"[DEBUG] Number of existing files: {len(existing_files)}")
        if episodes_needing_content:
            print(f"[DEBUG] First episode needing content: {episodes_needing_content[0]}")
        if existing_files:
            print(f"[DEBUG] First existing file: {existing_files[0]}")
        # Map files to episodes
        mapped_count = 0
        
        for episode, filename in zip(episodes_needing_content, existing_files):
            new_url = GCS_URL + filename
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE id = %s
            """, (new_url, datetime.now(timezone.utc), episode['id']))
            print(f"✅ Mapped Episode {episode['episode_number']}: {filename}")
            mapped_count += 1
        
        conn.commit()
        print(f"\n🎉 Successfully mapped {mapped_count} files to episodes!")
        
        # Final summary
        cur.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN content_url LIKE '%placeholder%' THEN 1 END) as placeholders,
                   COUNT(CASE WHEN content_url NOT LIKE '%placeholder%' THEN 1 END) as working
            FROM episodes 
            WHERE series_id = %s
        """, (series_id,))
        
        summary = cur.fetchone()
        print(f"\n📊 Final Summary:")
        print(f"Total episodes: {summary['total']}")
        print(f"Working episodes: {summary['working']}")
        print(f"Placeholder episodes: {summary['placeholders']}")
        
        if summary['placeholders'] == 0:
            print("🎉 SUCCESS: All episodes now have working content!")
        else:
            print(f"⚠️  Still need content for {summary['placeholders']} episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    existing_files = list_gcs_petrocelli_files()
    if existing_files:
        map_files_to_episodes(existing_files) 