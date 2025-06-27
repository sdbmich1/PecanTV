#!/usr/bin/env python3
"""
Script to fix the final Petrocelli issues and map all available files.
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

def test_file_exists(url):
    """Test if a file exists at the given URL."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def fix_petrocelli_final_issues():
    """Fix the final Petrocelli issues and map all available files."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing final Petrocelli issues...")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Fix Episode 7 - add missing .mp4 extension
        print("\n🔧 Fixing Episode 7 - adding missing .mp4 extension...")
        cur.execute("""
            SELECT id, content_url FROM episodes 
            WHERE series_id = %s AND episode_number = 7
        """, (series_id,))
        
        ep7 = cur.fetchone()
        if ep7 and 'Too-Many-Alibis_2p-1080-wCredits' in ep7['content_url']:
            new_url = ep7['content_url'] + '.mp4'
            if test_file_exists(new_url):
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_url, datetime.now(timezone.utc), ep7['id']))
                print(f"✅ Fixed Episode 7: {new_url}")
            else:
                print(f"❌ Episode 7 file not found: {new_url}")
        
        # Map additional files to missing episodes
        print("\n🔧 Mapping additional files to missing episodes...")
        
        # List of additional files that exist but aren't mapped
        additional_files = [
            "Petrocelli-Survival_2p-1080-wCredits.mp4"
        ]
        
        # Map them to episodes that need content (9, 10, 12-22)
        episode_mapping = {
            9: "Petrocelli-Survival_2p-1080-wCredits.mp4"  # Map Survival to Episode 9
        }
        
        for episode_num, filename in episode_mapping.items():
            # Check if episode currently has placeholder
            cur.execute("""
                SELECT id, content_url FROM episodes 
                WHERE series_id = %s AND episode_number = %s
            """, (series_id, episode_num))
            
            ep = cur.fetchone()
            if ep and 'placeholder' in ep['content_url']:
                new_url = BASE_URL + filename
                if test_file_exists(new_url):
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (new_url, datetime.now(timezone.utc), ep['id']))
                    print(f"✅ Mapped Episode {episode_num}: {filename}")
                else:
                    print(f"❌ File not found for Episode {episode_num}: {filename}")
        
        # Test for more files that might exist
        print("\n🔍 Testing for more Petrocelli files...")
        additional_titles = [
            "A-Deadly-Game",
            "The-Deadly-Trap", 
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
        
        found_files = []
        for title in additional_titles:
            filename = f"Petrocelli-{title}_2p-1080-wCredits.mp4"
            url = BASE_URL + filename
            if test_file_exists(url):
                found_files.append(filename)
                print(f"  ✅ Found: {filename}")
        
        # Map these additional files to remaining episodes
        if found_files:
            print(f"\n🔧 Mapping {len(found_files)} additional files...")
            
            # Get episodes that still need content
            cur.execute("""
                SELECT id, episode_number FROM episodes 
                WHERE series_id = %s 
                AND content_url LIKE '%placeholder%'
                ORDER BY episode_number
            """, (series_id,))
            
            episodes_needing_content = cur.fetchall()
            
            for i, (ep, filename) in enumerate(zip(episodes_needing_content, found_files)):
                new_url = BASE_URL + filename
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_url, datetime.now(timezone.utc), ep['id']))
                print(f"✅ Mapped Episode {ep['episode_number']}: {filename}")
        
        conn.commit()
        
        # Final summary
        print(f"\n📊 Final Summary:")
        print("=" * 40)
        
        cur.execute("""
            SELECT episode_number, content_url FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        all_episodes = cur.fetchall()
        
        working_episodes = 0
        placeholder_episodes = 0
        
        for ep in all_episodes:
            if 'placeholder' in ep['content_url']:
                placeholder_episodes += 1
            else:
                working_episodes += 1
        
        print(f"Working episodes: {working_episodes}")
        print(f"Placeholder episodes: {placeholder_episodes}")
        print(f"Total episodes: {len(all_episodes)}")
        
        if placeholder_episodes == 0:
            print("🎉 SUCCESS: All episodes now have working content!")
        else:
            print(f"⚠️  Still need content for {placeholder_episodes} episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_petrocelli_final_issues() 