#!/usr/bin/env python3
"""
Script to fix Ghost Squad episode poster URLs to use the correct filename from Wurl metadata.
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

def fix_ghost_squad_posters():
    """Fix Ghost Squad episode poster URLs to use the correct filename."""
    print("🔧 Fixing Ghost Squad Episode Poster URLs")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Ghost Squad series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Ghost Squad' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        if not result:
            print("❌ Ghost Squad series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Ghost Squad series (ID: {series_id})")
        
        # Get all Ghost Squad episodes
        cur.execute("""
            SELECT id, title, poster_url FROM episodes 
            WHERE series_id = %s
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} Ghost Squad episodes")
        
        updated_count = 0
        
        for episode_id, title, current_poster_url in episodes:
            # Update to use the correct poster filename
            new_poster_url = "pecantv_series/ghost_squad/Ghost-Squad_title-img.png"
            
            # Update the episode poster URL
            cur.execute("""
                UPDATE episodes 
                SET poster_url = %s 
                WHERE id = %s
            """, (new_poster_url, episode_id))
            
            print(f"  ✅ Updated: {title}")
            print(f"     Old: {current_poster_url}")
            print(f"     New: {new_poster_url}")
            updated_count += 1
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} Ghost Squad episode poster URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_ghost_squad_posters() 