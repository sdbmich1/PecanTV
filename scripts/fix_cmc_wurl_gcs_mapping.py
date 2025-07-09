#!/usr/bin/env python3
"""
Script to properly marry Wurl data with GCS URLs for Count of Monte Cristo episodes.
This fixes the filename mismatches that are causing episodes 2 & 3 to not play.
"""

import psycopg2
import pandas as pd
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

def load_wurl_data():
    """Load data from the Wurl metadata file."""
    file_path = "Wurl - File Upload Metadata_Version 7.0.43.xlsx"
    df = pd.read_excel(file_path)
    return df

def fix_cmc_wurl_gcs_mapping():
    """Fix Count of Monte Cristo episodes by marrying Wurl data with correct GCS URLs."""
    print("🔧 Fixing Count of Monte Cristo episodes with Wurl data")
    print("=" * 60)
    
    # Load Wurl data
    df = load_wurl_data()
    print(f"✅ Loaded Wurl file with {len(df)} rows")
    
    # Filter for Count of Monte Cristo episodes
    count_of_monte_cristo_data = df[df['Series Name'] == 'The Count of Monte Cristo']
    print(f"📺 Found {len(count_of_monte_cristo_data)} Count of Monte Cristo episodes in Wurl data")
    
    if count_of_monte_cristo_data.empty:
        print("❌ No Count of Monte Cristo data found in Wurl file")
        return
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Count of Monte Cristo series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'The Count of Monte Cristo' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Count of Monte Cristo series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Count of Monte Cristo series (ID: {series_id})")
        
        updated_count = 0
        
        # Process each episode by episode number
        for _, row in count_of_monte_cristo_data.iterrows():
            episode_number = int(row.get('Episode Number', 1))
            episode_title = row['Title']
            video_filename = row.get('Video Filename', '')
            artwork_filename = row.get('Artwork Filename', '')
            
            print(f"\n🔍 Processing Episode {episode_number}: {episode_title}")
            print(f"  Video: {video_filename}")
            print(f"  Artwork: {artwork_filename}")
            
            # Find the episode in the database by episode number
            cur.execute("""
                SELECT id, content_url, poster_url FROM episodes 
                WHERE series_id = %s AND episode_number = %s
            """, (series_id, episode_number))
            
            episode_result = cur.fetchone()
            if not episode_result:
                print(f"  ⚠️  Episode {episode_number} not found in database")
                continue
            
            episode_id, current_content_url, current_poster_url = episode_result
            
            # Construct correct GCS URLs from Wurl data
            if video_filename:
                new_content_url = f"https://storage.googleapis.com/pecantv_series/count_of_monte_cristo/{video_filename}"
            else:
                new_content_url = current_content_url
                
            if artwork_filename:
                new_poster_url = f"https://storage.googleapis.com/pecantv_series/count_of_monte_cristo/{artwork_filename}"
            else:
                new_poster_url = current_poster_url
            
            # Check if URLs have changed
            content_changed = new_content_url != current_content_url
            poster_changed = new_poster_url != current_poster_url
            
            if content_changed or poster_changed:
                print(f"  🔄 Updating episode (ID: {episode_id})")
                if content_changed:
                    print(f"     Content URL: {current_content_url} → {new_content_url}")
                if poster_changed:
                    print(f"     Poster URL: {current_poster_url} → {new_poster_url}")
                
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, poster_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode_id))
                
                updated_count += 1
            else:
                print(f"  ✅ No changes needed")
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} Count of Monte Cristo episodes!")
        
        # Verify the fixes
        print("\n📋 Verification:")
        print("=" * 30)
        
        # Check episodes 2 & 3 specifically
        for episode_num in [2, 3]:
            cur.execute("""
                SELECT episode_number, title, content_url 
                FROM episodes 
                WHERE series_id = %s AND episode_number = %s
            """, (series_id, episode_num))
            
            episode = cur.fetchone()
            if episode:
                ep_num, title, content_url = episode
                filename = content_url.split('/')[-1] if content_url else "No URL"
                print(f"  Episode {ep_num}: {title}")
                print(f"    URL: {content_url}")
                print(f"    Filename: {filename}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_cmc_wurl_gcs_mapping() 