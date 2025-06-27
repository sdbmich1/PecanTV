#!/usr/bin/env python3
"""
Script to fix Petrocelli episodes 8-22 with actual discovered files.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
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

# Base URL for Petrocelli files in GCS
BASE_URL = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

# Mapping of discovered files to episode numbers
# Based on the discovery script, we found these files:
DISCOVERED_FILES = {
    8: "Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4",
    11: "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4"
}

def verify_files_exist():
    """Verify that the discovered files actually exist in GCS."""
    print("🔍 Verifying discovered files exist in GCS...")
    print("=" * 60)
    
    verified_files = {}
    for episode_num, filename in DISCOVERED_FILES.items():
        test_url = BASE_URL + filename
        try:
            response = requests.head(test_url, timeout=10)
            if response.status_code == 200:
                verified_files[episode_num] = filename
                print(f"✅ Episode {episode_num}: {filename}")
            else:
                print(f"❌ Episode {episode_num}: {filename} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Episode {episode_num}: {filename} - Error: {e}")
    
    return verified_files

def fix_petrocelli_episodes_8_22():
    """Fix Petrocelli episodes 8-22 with actual discovered files."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("\n🔧 Fixing Petrocelli episodes 8-22 with discovered files")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Verify files exist
        verified_files = verify_files_exist()
        
        if not verified_files:
            print("❌ No verified files found, aborting update")
            return
        
        # Get episodes that need updating (episodes 8-22 with placeholder URLs)
        query = (
            "SELECT id, episode_number, title, content_url "
            "FROM episodes "
            "WHERE series_id = %s "
            "AND episode_number >= 8 "
            "AND episode_number <= 22 "
            "AND content_url LIKE '%%placeholder%%' "
            "ORDER BY episode_number"
        )
        print(f"\n[DEBUG] Query: {query}")
        print(f"[DEBUG] Params: (series_id={series_id},)")
        cur.execute(query, (series_id,))
        
        episodes_to_update = cur.fetchall()
        print(f"\n📺 Found {len(episodes_to_update)} episodes that need updating (8-22)")
        
        if not episodes_to_update:
            print("❌ No episodes found that need updating")
            return
        
        updated_count = 0
        for ep in episodes_to_update:
            try:
                episode_num = ep['episode_number']
                if episode_num in verified_files:
                    filename = verified_files[episode_num]
                    new_content_url = BASE_URL + filename
                    
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (new_content_url, datetime.now(timezone.utc), ep['id']))
                    
                    print(f"✅ Updated Episode {episode_num}: {ep['title']}")
                    print(f"   Old URL: {ep['content_url']}")
                    print(f"   New URL: {new_content_url}")
                    updated_count += 1
                else:
                    print(f"⚠️  No file mapping found for Episode {episode_num}: {ep['title']}")
            except Exception as e:
                print(f"❌ Error updating episode {ep.get('episode_number', 'unknown')}: {e}")
                continue
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} episodes")
        
        # Show summary of what was updated
        print(f"\n📋 Summary of updates:")
        print("-" * 40)
        for episode_num, filename in verified_files.items():
            print(f"Episode {episode_num}: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_petrocelli_episodes_8_22() 