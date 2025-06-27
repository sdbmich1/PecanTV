#!/usr/bin/env python3
"""
Script to fix Petrocelli content URLs to point to the correct petrocelli_final_episodes folder.
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

def fix_petrocelli_content_urls():
    """Fix Petrocelli content URLs to point to the correct folder."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing Petrocelli content URLs to correct folder")
        print("=" * 70)
        
        # Get all Petrocelli content entries that need URL fixing
        cur.execute("""
            SELECT id, title, content_url, poster_url
            FROM content 
            WHERE series_name = 'Petrocelli' 
            AND type = 'SERIES'
            AND content_url LIKE '%pecantv_features%'
        """)
        
        content_entries = cur.fetchall()
        
        if not content_entries:
            print("❌ No Petrocelli content entries with incorrect URLs found")
            return
        
        print(f"📺 Found {len(content_entries)} Petrocelli content entries to fix")
        
        updated_count = 0
        
        for entry in content_entries:
            old_url = entry['content_url']
            
            # Extract filename from old URL
            filename = old_url.split('/')[-1]
            
            # Create new URL pointing to petrocelli_final_episodes folder
            new_url = f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{filename}"
            
            # Also fix poster URL if it has double URLs
            new_poster_url = entry['poster_url']
            if new_poster_url and 'https://storage.googleapis.com/pecantv_series/' in new_poster_url:
                # Extract the actual poster filename
                poster_parts = new_poster_url.split('/')
                if len(poster_parts) > 2:
                    poster_filename = poster_parts[-1]
                    new_poster_url = f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{poster_filename}"
            
            # Update the content entry
            cur.execute("""
                UPDATE content 
                SET content_url = %s, poster_url = %s, updated_at = %s
                WHERE id = %s
            """, (new_url, new_poster_url, datetime.now(timezone.utc), entry['id']))
            
            print(f"✅ Fixed {entry['title']}:")
            print(f"  Old URL: {old_url}")
            print(f"  New URL: {new_url}")
            print(f"  New Poster URL: {new_poster_url}")
            print()
            
            updated_count += 1
        
        conn.commit()
        print(f"✅ Updated {updated_count} content entries")
        
        # Now update the episodes table to use the corrected URLs
        print("\n" + "=" * 70)
        print("🔄 Updating episodes table with corrected URLs...")
        
        # Get the corrected content entries
        cur.execute("""
            SELECT id, title, content_url, poster_url, description
            FROM content 
            WHERE series_name = 'Petrocelli' 
            AND type = 'SERIES'
            AND content_url IS NOT NULL
            AND content_url != ''
            ORDER BY title
        """)
        
        corrected_content = cur.fetchall()
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        series_id = series_result['id']
        
        # Get episodes
        cur.execute("""
            SELECT id, episode_number, title
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        # Map episodes to corrected content files
        episode_updates = 0
        for i, content_file in enumerate(corrected_content):
            if i < len(episodes):
                ep = episodes[i]
                
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, poster_url = %s, description = %s, updated_at = %s
                    WHERE id = %s
                """, (
                    content_file['content_url'],
                    content_file['poster_url'],
                    content_file['description'],
                    datetime.now(timezone.utc),
                    ep['id']
                ))
                
                filename = content_file['content_url'].split('/')[-1]
                print(f"✅ Updated Episode {ep['episode_number']} with: {filename}")
                episode_updates += 1
        
        conn.commit()
        print(f"✅ Updated {episode_updates} episodes with corrected URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_petrocelli_content_urls() 