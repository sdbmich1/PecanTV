#!/usr/bin/env python3
"""
Script to fix Ghost Squad episode URLs to use correct path structure.
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

def fix_ghost_squad_urls():
    """Fix Ghost Squad episode URLs to use correct path structure."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing Ghost Squad Episode URLs")
        print("=" * 40)
        
        # Get Ghost Squad episodes
        cur.execute("""
            SELECT e.id, e.title, e.content_url, e.poster_url
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE c.title = 'Ghost Squad'
            ORDER BY e.episode_number
        """)
        
        episodes = cur.fetchall()
        print(f"Found {len(episodes)} Ghost Squad episodes")
        
        updated = 0
        for episode in episodes:
            old_content_url = episode['content_url']
            old_poster_url = episode['poster_url']
            
            # Fix content URL
            if '/the/' in old_content_url:
                new_content_url = old_content_url.replace('/the/', '/ghost_squad/')
            elif '/ticket/' in old_content_url:
                new_content_url = old_content_url.replace('/ticket/', '/ghost_squad/')
            else:
                new_content_url = old_content_url
            
            # Fix poster URL
            if '/the/' in old_poster_url:
                new_poster_url = old_poster_url.replace('/the/', '/ghost_squad/')
            elif '/ticket/' in old_poster_url:
                new_poster_url = old_poster_url.replace('/ticket/', '/ghost_squad/')
            else:
                new_poster_url = old_poster_url
            
            # Update if URLs changed
            if new_content_url != old_content_url or new_poster_url != old_poster_url:
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, poster_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode['id']))
                
                print(f"  ✅ Updated: {episode['title']}")
                print(f"     Content: {old_content_url} → {new_content_url}")
                print(f"     Poster: {old_poster_url} → {new_poster_url}")
                updated += 1
            else:
                print(f"  ⚠️  No change needed: {episode['title']}")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Ghost Squad episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_ghost_squad_urls() 