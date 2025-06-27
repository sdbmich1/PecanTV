#!/usr/bin/env python3
"""
Script to update Petrocelli episodes to reflect the current reality.
Currently only one episode file is available in GCS.
"""

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

def update_petrocelli_episodes():
    """Update Petrocelli episodes to reflect available files."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Updating Petrocelli episodes to reflect available files")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Get all episodes
        cur.execute("""
            SELECT id, episode_number, title, content_url
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        if not episodes:
            print("❌ No episodes found")
            return
        
        print(f"📺 Found {len(episodes)} episodes in database")
        
        # Currently available file
        available_file = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4"
        
        updated_count = 0
        
        for ep in episodes:
            current_url = ep['content_url']
            
            # Check if this episode currently points to a non-existent file
            if "Petrocelli" in current_url and not current_url.endswith("Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4"):
                # This episode points to a non-existent file
                print(f"⚠️  Episode {ep['episode_number']} points to non-existent file: {current_url}")
                
                # For now, let's update episodes 2-5 to also point to the available file
                # This is a temporary solution until more files are uploaded
                if ep['episode_number'] <= 5:
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (available_file, datetime.now(timezone.utc), ep['id']))
                    
                    print(f"  ✅ Updated Episode {ep['episode_number']} to use available file")
                    updated_count += 1
                else:
                    # For episodes 6+, we'll set a placeholder URL that indicates the file is not available
                    placeholder_url = "https://storage.googleapis.com/pecantv_series/placeholder/not_available.mp4"
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (placeholder_url, datetime.now(timezone.utc), ep['id']))
                    
                    print(f"  ⚠️  Episode {ep['episode_number']} marked as not available")
                    updated_count += 1
        
        conn.commit()
        print(f"\n✅ Updated {updated_count} episodes")
        print("\n📝 Note: Only episodes 1-5 are currently pointing to the available file.")
        print("   Episodes 6+ are marked as not available until more files are uploaded to GCS.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_petrocelli_episodes() 