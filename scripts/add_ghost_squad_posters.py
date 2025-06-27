#!/usr/bin/env python3
"""
Script to add default poster URLs for Ghost Squad episodes.
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

def add_ghost_squad_posters():
    """Add default poster URLs for Ghost Squad episodes."""
    print("🔧 Adding poster URLs for Ghost Squad episodes")
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
        
        # Get episodes that need poster URLs
        cur.execute("""
            SELECT id, episode_number, title 
            FROM episodes 
            WHERE series_id = %s AND (poster_url IS NULL OR poster_url = '')
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        if not episodes:
            print("📺 All Ghost Squad episodes already have poster URLs")
            return
        
        print(f"📺 Found {len(episodes)} episodes needing poster URLs:")
        
        updated_count = 0
        
        for episode in episodes:
            episode_id, episode_number, title = episode
            
            # Create a default poster URL based on the episode title
            # Remove special characters and spaces for filename
            safe_title = title.replace(" ", "_").replace("-", "_").replace("'", "")
            poster_url = f"pecantv_series/ghost_squad/{safe_title}_poster.jpg"
            
            cur.execute("""
                UPDATE episodes 
                SET poster_url = %s 
                WHERE id = %s
            """, (poster_url, episode_id))
            
            print(f"  ✅ Updated S1E{episode_number}: {title}")
            print(f"     Poster URL: {poster_url}")
            updated_count += 1
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} Ghost Squad episodes with poster URLs!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_ghost_squad_posters() 