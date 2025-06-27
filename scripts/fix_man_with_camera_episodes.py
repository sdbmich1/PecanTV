#!/usr/bin/env python3
"""
Script to check and fix Man with a Camera episodes using Video Filename and Artwork Filename from Wurl metadata.
"""

import psycopg2
import pandas as pd

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def load_wurl_data():
    """Load data from the Wurl metadata file."""
    file_path = "Wurl-File-Upload-Metadata_Version-7.0.4.1.xlsx"
    df = pd.read_excel(file_path)
    return df

def check_and_fix_man_with_camera():
    """Check and fix Man with a Camera episodes."""
    print("🔧 Checking and fixing Man with a Camera episodes")
    print("=" * 60)
    
    # Load Wurl data
    df = load_wurl_data()
    print(f"✅ Loaded Wurl file with {len(df)} rows")
    
    # Filter for Man with a Camera episodes
    man_with_camera_data = df[df['Series Name'] == 'Man with a Camera']
    print(f"📺 Found {len(man_with_camera_data)} Man with a Camera episodes in Wurl data")
    
    if man_with_camera_data.empty:
        print("❌ No Man with a Camera data found in Wurl file")
        return
    
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
        
        # Get current episodes in database
        cur.execute("""
            SELECT id, episode_number, title, content_url, poster_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        db_episodes = cur.fetchall()
        print(f"📺 Found {len(db_episodes)} episodes in database")
        
        updated_count = 0
        
        # Process each episode by episode number
        for _, row in man_with_camera_data.iterrows():
            episode_number = int(row.get('Episode Number', 1))
            episode_title = row['Title']
            video_filename = row.get('Video Filename', '')
            artwork_filename = row.get('Artwork Filename', '')
            
            print(f"\n🔍 Processing Episode {episode_number}: {episode_title}")
            print(f"  Video: {video_filename}")
            print(f"  Artwork: {artwork_filename}")
            
            # Find the episode in the database by episode number
            cur.execute("""
                SELECT id FROM episodes 
                WHERE series_id = %s AND episode_number = %s
            """, (series_id, episode_number))
            
            episode_result = cur.fetchone()
            if not episode_result:
                print(f"  ⚠️  Episode {episode_number} not found in database")
                continue
            
            episode_id = episode_result[0]
            
            # Update the episode with correct content URL and poster URL
            content_url = f"pecantv_series/man_with_camera/{video_filename}" if video_filename else ''
            poster_url = f"pecantv_series/man_with_camera/{artwork_filename}" if artwork_filename else ''
            
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, poster_url = %s 
                WHERE id = %s
            """, (content_url, poster_url, episode_id))
            
            print(f"  ✅ Updated episode (ID: {episode_id})")
            print(f"     Content URL: {content_url}")
            print(f"     Poster URL: {poster_url}")
            updated_count += 1
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} Man with a Camera episodes!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_and_fix_man_with_camera() 