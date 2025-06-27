#!/usr/bin/env python3
"""
Script to fix Commando Cody episodes using video filenames and artwork filenames from the Wurl metadata file.
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

def update_commando_cody_from_wurl():
    """Update Commando Cody episodes using Wurl metadata."""
    print("🔧 Fixing Commando Cody episodes using Wurl metadata")
    print("=" * 60)
    
    # Load Wurl data
    df = load_wurl_data()
    print(f"✅ Loaded Wurl file with {len(df)} rows")
    
    # Filter for Commando Cody episodes
    commando_cody_data = df[df['Series Name'] == 'Commando Cody - Sky Marshal of the Universe']
    print(f"📺 Found {len(commando_cody_data)} Commando Cody episodes in Wurl data")
    
    if commando_cody_data.empty:
        print("❌ No Commando Cody data found in Wurl file")
        return
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Commando Cody series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Commando Cody - Sky Marshal of the Universe' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Commando Cody series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Commando Cody series (ID: {series_id})")
        
        updated_count = 0
        
        for _, row in commando_cody_data.iterrows():
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
            content_url = f"pecantv_series/commando_cody/{video_filename}" if video_filename else ''
            poster_url = f"pecantv_series/commando_cody/{artwork_filename}" if artwork_filename else ''
            
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
        print(f"\n🎉 Successfully updated {updated_count} Commando Cody episodes!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_commando_cody_from_wurl() 