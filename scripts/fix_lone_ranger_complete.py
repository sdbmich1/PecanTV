#!/usr/bin/env python3
"""
Comprehensive script to fix Lone Ranger episodes by updating titles, content URLs, and poster URLs.
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

def fix_lone_ranger_complete():
    """Fix Lone Ranger episodes completely."""
    print("🔧 Comprehensive fix for Lone Ranger episodes")
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
        for _, row in lone_ranger_data.iterrows():
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
            
            # Update the episode with correct title, content URL, and poster URL
            content_url = f"pecantv_series/lone_ranger/{video_filename}" if video_filename else ''
            poster_url = f"pecantv_series/lone_ranger/{artwork_filename}" if artwork_filename else ''
            
            cur.execute("""
                UPDATE episodes 
                SET title = %s, content_url = %s, poster_url = %s 
                WHERE id = %s
            """, (episode_title, content_url, poster_url, episode_id))
            
            print(f"  ✅ Updated episode (ID: {episode_id})")
            print(f"     Title: {episode_title}")
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
    fix_lone_ranger_complete() 