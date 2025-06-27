#!/usr/bin/env python3
"""
Script to fix Lone Ranger episodes with content URLs and poster URLs from the pecantv_series/lone_ranger folder.
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

def update_lone_ranger_episodes():
    """Update Lone Ranger episodes using Wurl metadata."""
    print("🔧 Fixing Lone Ranger episodes using Wurl metadata")
    print("=" * 60)
    
    # Load Wurl data
    df = load_wurl_data()
    print(f"✅ Loaded Wurl file with {len(df)} rows")
    
    # Filter for Lone Ranger episodes
    lone_ranger_data = df[df['Series Name'] == 'The Lone Ranger']
    print(f"📺 Found {len(lone_ranger_data)} Lone Ranger episodes in Wurl data")
    
    if lone_ranger_data.empty:
        print("❌ No Lone Ranger data found in Wurl file")
        return
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Lone Ranger series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Lone Ranger' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Lone Ranger series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Lone Ranger series (ID: {series_id})")
        
        updated_count = 0
        
        for _, row in lone_ranger_data.iterrows():
            episode_title = row['Title']
            video_filename = row.get('Video Filename', '')
            artwork_filename = row.get('Artwork Filename', '')
            
            print(f"\n🔍 Processing: {episode_title}")
            print(f"  Video: {video_filename}")
            print(f"  Artwork: {artwork_filename}")
            
            # Find the episode in the database
            cur.execute("""
                SELECT id FROM episodes 
                WHERE series_id = %s AND title = %s
            """, (series_id, episode_title))
            
            episode_result = cur.fetchone()
            if not episode_result:
                print(f"  ⚠️  Episode not found in database: {episode_title}")
                continue
            
            episode_id = episode_result[0]
            
            # Update the episode with the correct URLs
            content_url = f"pecantv_series/lone_ranger/{video_filename}" if video_filename else ''
            poster_url = f"pecantv_series/lone_ranger/{artwork_filename}" if artwork_filename else ''
            
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
        print(f"\n🎉 Successfully updated {updated_count} Lone Ranger episodes!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_lone_ranger_episodes() 