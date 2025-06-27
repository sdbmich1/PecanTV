#!/usr/bin/env python3
"""
Script to fix double folder names in episode URLs.
"""

import psycopg2
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

def fix_double_folder_urls():
    """Fix URLs that have double folder names like dragnet/dragnet/."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        print("🔧 Fixing Double Folder Names in URLs")
        print("=" * 50)
        
        # Get all episodes with content_url that contains double folder names
        cur.execute("""
            SELECT id, title, content_url, poster_url 
            FROM episodes 
            WHERE content_url LIKE '%/%/%'
            ORDER BY series_id, episode_number
        """)
        episodes = cur.fetchall()
        
        updated = 0
        for episode_id, episode_title, content_url, poster_url in episodes:
            # Fix content URL
            if content_url and '/%/' in content_url:
                # Split by '/' and remove duplicate folder names
                parts = content_url.split('/')
                # Find the pattern: bucket/folder/folder/filename
                if len(parts) >= 5 and parts[3] == parts[4]:  # Double folder
                    # Remove the duplicate folder
                    parts.pop(4)
                    new_content_url = '/'.join(parts)
                else:
                    new_content_url = content_url
            else:
                new_content_url = content_url
            
            # Fix poster URL
            if poster_url and '/%/' in poster_url:
                parts = poster_url.split('/')
                if len(parts) >= 5 and parts[3] == parts[4]:  # Double folder
                    parts.pop(4)
                    new_poster_url = '/'.join(parts)
                else:
                    new_poster_url = poster_url
            else:
                new_poster_url = poster_url
            
            # Update if URLs changed
            if new_content_url != content_url or new_poster_url != poster_url:
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, poster_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode_id))
                
                print(f"  ✅ Fixed: {episode_title}")
                if new_content_url != content_url:
                    print(f"     Content: {content_url} → {new_content_url}")
                if new_poster_url != poster_url:
                    print(f"     Poster: {poster_url} → {new_poster_url}")
                
                updated += 1
        
        conn.commit()
        print(f"\n✅ Fixed {updated} episodes with double folder names.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_double_folder_urls() 