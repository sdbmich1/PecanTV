#!/usr/bin/env python3
"""
Script to update Petrocelli episodes with actual video files from content table.
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

def update_petrocelli_with_actual_files():
    """Update Petrocelli episodes with actual video files from content table."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Updating Petrocelli episodes with actual video files")
        print("=" * 70)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Get all Petrocelli episode files from content table
        cur.execute("""
            SELECT id, title, content_url, poster_url, description
            FROM content 
            WHERE series_name = 'Petrocelli' 
            AND type = 'SERIES'
            AND content_url IS NOT NULL
            AND content_url != ''
            ORDER BY title
        """)
        
        content_files = cur.fetchall()
        
        if not content_files:
            print("❌ No Petrocelli content files found")
            return
        
        print(f"📺 Found {len(content_files)} Petrocelli content files:")
        for file in content_files:
            filename = file['content_url'].split('/')[-1] if file['content_url'] else 'No URL'
            print(f"  {file['title']} -> {filename}")
        
        # Get all episodes that need updating
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
        
        print(f"\n📋 Found {len(episodes)} episodes to update")
        
        # Map episodes to content files
        # We'll map episodes 1-7 to the available content files
        episode_to_content_mapping = {}
        
        for i, content_file in enumerate(content_files):
            if i < len(episodes):
                episode_to_content_mapping[episodes[i]['episode_number']] = content_file
        
        updated_count = 0
        
        for ep in episodes:
            episode_num = ep['episode_number']
            
            if episode_num in episode_to_content_mapping:
                content_file = episode_to_content_mapping[episode_num]
                
                # Update episode with actual content file
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
                
                filename = content_file['content_url'].split('/')[-1] if content_file['content_url'] else 'No URL'
                print(f"✅ Updated Episode {episode_num} with: {filename}")
                updated_count += 1
            else:
                # For episodes beyond available content files, mark as not available
                placeholder_url = "https://storage.googleapis.com/pecantv_series/placeholder/not_available.mp4"
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, updated_at = %s
                    WHERE id = %s
                """, (placeholder_url, datetime.now(timezone.utc), ep['id']))
                
                print(f"⚠️  Episode {episode_num} marked as not available (no content file)")
                updated_count += 1
        
        conn.commit()
        print(f"\n✅ Updated {updated_count} episodes")
        print(f"📝 Note: Episodes 1-{len(content_files)} now have actual video files.")
        print(f"   Episodes {len(content_files)+1}-{len(episodes)} are marked as not available.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_petrocelli_with_actual_files() 