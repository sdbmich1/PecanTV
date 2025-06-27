#!/usr/bin/env python3
"""
Script to fix Dragnet episode URLs by updating them from Google Cloud Storage URLs to local file paths.
"""

import psycopg2

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_dragnet_episode_urls():
    """Fix Dragnet episode URLs by updating them to local file paths."""
    print("🔧 Fixing Dragnet Episode URLs")
    print("=" * 40)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Dragnet series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Dragnet' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        if not result:
            print("❌ Dragnet series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Dragnet series (ID: {series_id})")
        
        # Get all Dragnet episodes
        cur.execute("""
            SELECT id, title, content_url FROM episodes 
            WHERE series_id = %s
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} Dragnet episodes")
        
        updated_count = 0
        
        for episode_id, title, current_url in episodes:
            # Extract filename from current URL
            if current_url.startswith('https://storage.googleapis.com/pecantv_features/'):
                filename = current_url.split('/')[-1]
                new_url = f"pecantv_series/dragnet/{filename}"
                
                # Update the episode URL
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s 
                    WHERE id = %s
                """, (new_url, episode_id))
                
                print(f"  ✅ Updated: {title}")
                print(f"     Old: {current_url}")
                print(f"     New: {new_url}")
                updated_count += 1
            else:
                print(f"  ⚠️  Skipped: {title} (already has local URL)")
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} Dragnet episode URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_dragnet_episode_urls() 