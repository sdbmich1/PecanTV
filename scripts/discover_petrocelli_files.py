#!/usr/bin/env python3
"""
Script to discover actual Petrocelli file names in GCS and update the database.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
import requests
import re

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# Base URL for Petrocelli files in GCS
BASE_URL = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

def discover_petrocelli_files():
    """Discover Petrocelli files in the GCS bucket by testing common patterns."""
    print("🔍 Discovering Petrocelli files in GCS bucket...")
    print("=" * 60)
    
    discovered_files = []
    
    # Test patterns based on the known files we have (episodes 1-7)
    # From the database, we know these patterns exist:
    known_patterns = [
        "Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4",
        "Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4", 
        "Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4",
        "Petrocelli-Once-Upon-A-Victim_2p-1080-full-credits.mp4",
        "Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4",
        "Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4",
        "Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4"
    ]
    
    # Test the known patterns first
    for pattern in known_patterns:
        test_url = BASE_URL + pattern
        response = requests.head(test_url)
        if response.status_code == 200:
            discovered_files.append(pattern)
            print(f"✅ Found: {pattern}")
        else:
            print(f"❌ Not found: {pattern}")
    
    # Now let's try to discover more files by testing common naming patterns
    # Based on the pattern, let's try variations for episodes 8-22
    episode_titles = [
        "Shadow-of-a-Doubt",  # This was mentioned in previous scripts
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
    
    print(f"\n🔍 Testing potential episode titles for episodes 8-22...")
    for i, title in enumerate(episode_titles, 8):
        # Try different naming patterns
        patterns_to_test = [
            f"Petrocelli-{title}_2p-1080-wCredits.mp4",
            f"Petrocelli-{title}_2p-1080-full-credits.mp4",
            f"Petrocelli-{title}.mp4",
            f"Petrocelli-Episode-{i}-{title}.mp4",
            f"Petrocelli-{i}-{title}.mp4"
        ]
        
        for pattern in patterns_to_test:
            test_url = BASE_URL + pattern
            response = requests.head(test_url)
            if response.status_code == 200:
                discovered_files.append(pattern)
                print(f"✅ Found Episode {i}: {pattern}")
                break
        else:
            print(f"❌ Episode {i}: No file found for '{title}'")
    
    return discovered_files

def update_petrocelli_episodes_with_discovered_files():
    """Update Petrocelli episodes with discovered file names."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("\n🔧 Updating Petrocelli episodes with discovered file names")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Get episodes that need updating (episodes 8-22 with placeholder URLs)
        cur.execute("""
            SELECT id, episode_number, title
            FROM episodes 
            WHERE series_id = %s 
            AND episode_number >= 8 
            AND episode_number <= 22
            AND content_url LIKE '%placeholder%'
            ORDER BY episode_number
        """, (series_id,))
        
        episodes_to_update = cur.fetchall()
        print(f"📺 Found {len(episodes_to_update)} episodes that need updating (8-22)")
        
        # For now, let's create a mapping based on discovered files
        # This is a manual mapping - you'll need to provide the correct mapping
        episode_file_mapping = {
            # This mapping needs to be filled in based on actual discovered files
            # Format: episode_number: filename
        }
        
        updated_count = 0
        for ep in episodes_to_update:
            episode_num = ep['episode_number']
            if episode_num in episode_file_mapping:
                filename = episode_file_mapping[episode_num]
                new_content_url = BASE_URL + filename
                
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_content_url, datetime.now(timezone.utc), ep['id']))
                
                print(f"✅ Updated Episode {episode_num}: {ep['title']} -> {filename}")
                updated_count += 1
            else:
                print(f"⚠️  No file mapping found for Episode {episode_num}: {ep['title']}")
        
        conn.commit()
        print(f"\n✅ Updated {updated_count} episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    discovered_files = discover_petrocelli_files()
    print(f"\n📋 Total discovered files: {len(discovered_files)}")
    print("Discovered files:")
    for file in discovered_files:
        print(f"  - {file}")
    
    # Only update if we have discovered files
    if discovered_files:
        update_petrocelli_episodes_with_discovered_files()
    else:
        print("\n❌ No files discovered, skipping database update") 