#!/usr/bin/env python3
"""
Script to update Bonanza episodes 5-13 with video filenames from Wurl metadata.
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
    """Load data from multiple Wurl metadata files."""
    all_bonanza_data = []
    
    # Files that contain Bonanza Animated Series data
    files_to_try = [
        "Wurl - File Upload Metadata_Version 7.0.15.csv",
        "Wurl - File Upload Metadata_Version 7.0.19.csv"
    ]
    
    for file_path in files_to_try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Filter for Bonanza Animated Series
            bonanza_data = df[df['Series Name'] == 'Bonanza Animated Series']
            if not bonanza_data.empty:
                print(f"✅ Found {len(bonanza_data)} Bonanza Animated Series episodes in {file_path}")
                all_bonanza_data.append(bonanza_data)
        except Exception as e:
            print(f"❌ Could not read {file_path}: {e}")
            continue
    
    if all_bonanza_data:
        # Combine all data
        combined_data = pd.concat(all_bonanza_data, ignore_index=True)
        # Remove duplicates based on episode number
        combined_data = combined_data.drop_duplicates(subset=['Episode Number'])
        return combined_data
    
    return pd.DataFrame()

def update_bonanza_episodes():
    """Update Bonanza episodes 5-13 with video filenames from Wurl metadata."""
    print("🔧 Updating Bonanza episodes 5-13 with Wurl metadata")
    print("=" * 60)
    
    # Load Wurl data
    bonanza_data = load_wurl_data()
    if bonanza_data.empty:
        print("❌ No Bonanza Animated Series data found in Wurl files")
        return
    
    print(f"📺 Found {len(bonanza_data)} total Bonanza Animated Series episodes in Wurl data")
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Bonanza series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Bonanza' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Bonanza series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Bonanza series (ID: {series_id})")
        
        updated_count = 0
        
        # Process each episode by episode number
        for _, row in bonanza_data.iterrows():
            episode_number = int(row.get('Episode Number', 1))
            episode_title = row['Title']
            video_filename = row.get('Video Filename', '')
            artwork_filename = row.get('Artwork Filename', '')
            
            # Only process episodes 5-13 (the ones still missing URLs)
            if episode_number < 5 or episode_number > 13:
                continue
            
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
            content_url = f"pecantv_series/bonanza/{video_filename}" if video_filename else ''
            poster_url = f"pecantv_series/bonanza/{artwork_filename}" if artwork_filename else ''
            
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
        print(f"\n🎉 Successfully updated {updated_count} Bonanza episodes!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_bonanza_episodes() 