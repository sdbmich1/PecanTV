#!/usr/bin/env python3
"""
Script to check the video filename field in the content table for Petrocelli episodes.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_petrocelli_video_filenames():
    """Check the video filename field in the content table for Petrocelli episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking Petrocelli video filenames in content table...")
        print("=" * 70)
        
        # First, let's see what columns are available in the content table
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'content' 
            AND column_name ILIKE '%filename%' OR column_name ILIKE '%video%'
            ORDER BY column_name
        """)
        
        filename_columns = cur.fetchall()
        print(f"📋 Filename-related columns found: {len(filename_columns)}")
        for col in filename_columns:
            print(f"  - {col['column_name']} ({col['data_type']})")
        
        # Let's also check for any columns that might contain filenames
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'content' 
            ORDER BY column_name
        """)
        
        all_columns = cur.fetchall()
        print(f"\n📋 All columns in content table:")
        for col in all_columns:
            print(f"  - {col['column_name']} ({col['data_type']})")
        
        # Now let's get all Petrocelli-related entries and see what filename info we have
        cur.execute("""
            SELECT id, title, type, content_url, poster_url, trailer_url, description,
                   series_name, episode_number, season_number
            FROM content 
            WHERE (title ILIKE '%petrocelli%' OR series_name ILIKE '%petrocelli%')
            ORDER BY title
        """)
        
        petrocelli_entries = cur.fetchall()
        print(f"\n📺 Found {len(petrocelli_entries)} Petrocelli-related entries in content table:")
        print("=" * 70)
        
        for entry in petrocelli_entries:
            print(f"\nID: {entry['id']}")
            print(f"Title: {entry['title']}")
            print(f"Type: {entry['type']}")
            print(f"Series Name: {entry['series_name']}")
            print(f"Episode Number: {entry['episode_number']}")
            print(f"Season Number: {entry['season_number']}")
            print(f"Content URL: {entry['content_url']}")
            print(f"Poster URL: {entry['poster_url']}")
            print(f"Trailer URL: {entry['trailer_url']}")
            print(f"Description: {entry['description'][:100] if entry['description'] else 'None'}...")
            
            # Extract filename from content_url if available
            if entry['content_url']:
                filename = entry['content_url'].split('/')[-1]
                print(f"Extracted Filename: {filename}")
            print("-" * 50)
        
        # Let's also check the episodes table for Petrocelli
        print(f"\n🔍 Checking episodes table for Petrocelli...")
        print("=" * 50)
        
        # Get Petrocelli series ID first
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        
        if series_result:
            series_id = series_result['id']
            cur.execute("""
                SELECT id, title, episode_number, season_number, content_url, poster_url
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number
            """, (series_id,))
            
            episodes = cur.fetchall()
            print(f"📺 Found {len(episodes)} Petrocelli episodes in episodes table:")
            
            for ep in episodes:
                print(f"\nEpisode {ep['episode_number']}: {ep['title']}")
                print(f"  Content URL: {ep['content_url']}")
                print(f"  Poster URL: {ep['poster_url']}")
                
                # Extract filename from content_url
                if ep['content_url']:
                    filename = ep['content_url'].split('/')[-1]
                    print(f"  Extracted Filename: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_petrocelli_video_filenames() 