#!/usr/bin/env python3
"""
Script to add default poster URLs for Man with a Camera episodes.
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

def add_man_with_camera_posters():
    """Add default poster URLs for Man with a Camera episodes."""
    print("🔧 Adding poster URLs for Man with a Camera episodes")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Man with a Camera series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Man with a Camera' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Man with a Camera series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Man with a Camera series (ID: {series_id})")
        
        # Get episodes that need poster URLs
        cur.execute("""
            SELECT id, episode_number, title 
            FROM episodes 
            WHERE series_id = %s AND (poster_url IS NULL OR poster_url = '')
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        if not episodes:
            print("📺 All Man with a Camera episodes already have poster URLs")
            return
        
        print(f"📺 Found {len(episodes)} episodes needing poster URLs:")
        
        updated_count = 0
        
        for episode in episodes:
            episode_id, episode_number, title = episode
            
            # Create a default poster URL based on the episode title
            # Remove special characters and spaces for filename
            safe_title = title.replace(" ", "_").replace("-", "_").replace("'", "")
            poster_url = f"pecantv_series/man_with_camera/{safe_title}_poster.jpg"
            
            cur.execute("""
                UPDATE episodes 
                SET poster_url = %s 
                WHERE id = %s
            """, (poster_url, episode_id))
            
            print(f"  ✅ Updated S1E{episode_number}: {title}")
            print(f"     Poster URL: {poster_url}")
            updated_count += 1
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} Man with a Camera episodes with poster URLs!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_man_with_camera_posters() 