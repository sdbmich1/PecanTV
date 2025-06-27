#!/usr/bin/env python3
"""
Script to update Bonanza episodes by matching titles instead of episode numbers.
"""

import pandas as pd
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

# Bonanza files to process
BONANZA_FILES = [
    'Wurl - File Upload Metadata_Version 7.0.28.xlsx',
    'Wurl - File Upload Metadata_Version 7.0.28.csv',
    'Wurl - File Upload Metadata_Version 7.0.29.csv',
    'Wurl - File Upload Metadata_Version 7.0.30.csv'
]

def load_bonanza_data_by_title():
    """Load Bonanza episode data from all files, indexed by title."""
    bonanza_episodes = {}
    
    for file in BONANZA_FILES:
        try:
            print(f"📖 Reading {file}...")
            
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                # Try different encodings for CSV
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"  ❌ Could not read {file} with any encoding")
                    continue
            
            # Filter for Bonanza episodes
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                bonanza_df = df[df['Series Name'].str.strip().str.lower() == 'bonanza']
                
                for _, row in bonanza_df.iterrows():
                    title = str(row.get('Title', '')).strip()
                    video_filename = str(row.get('Video Filename', '')).strip()
                    artwork_filename = str(row.get('Artwork Filename', '')).strip()
                    
                    if video_filename and video_filename != 'nan':
                        # Use title as key for matching
                        title_key = title.lower().strip()
                        if title_key not in bonanza_episodes:
                            bonanza_episodes[title_key] = {
                                'title': title,
                                'video_filename': video_filename,
                                'artwork_filename': artwork_filename if artwork_filename != 'nan' else '',
                                'source_file': file
                            }
                            print(f"  ✅ Found: {title}")
                            print(f"     Video: {video_filename}")
                            if artwork_filename and artwork_filename != 'nan':
                                print(f"     Artwork: {artwork_filename}")
        
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    return bonanza_episodes

def update_bonanza_episodes_by_title():
    """Update Bonanza episodes by matching titles."""
    print("🎬 Updating Bonanza Episodes by Title Matching")
    print("=" * 50)
    
    # Load Bonanza data
    bonanza_data = load_bonanza_data_by_title()
    print(f"\n📊 Found {len(bonanza_data)} unique Bonanza episodes in metadata files")
    
    # Connect to database
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Bonanza series ID
        cur.execute("SELECT id FROM content WHERE title = 'Bonanza' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Bonanza series not found")
            return
        
        series_id = series_result[0]
        print(f"✅ Found Bonanza series (ID: {series_id})")
        
        # Get episodes with missing content_url
        cur.execute("""
            SELECT id, title, season_number, episode_number, content_url, poster_url
            FROM episodes 
            WHERE series_id = %s AND (content_url IS NULL OR content_url = '')
        """, (series_id,))
        
        missing_episodes = cur.fetchall()
        print(f"Found {len(missing_episodes)} Bonanza episodes with missing content URLs")
        
        updated_count = 0
        for ep_id, ep_title, season, episode, current_content_url, current_poster_url in missing_episodes:
            # Try to match by title
            title_key = ep_title.lower().strip()
            bonanza_info = bonanza_data.get(title_key)
            
            if bonanza_info:
                # Construct content URL
                content_url = f"https://storage.googleapis.com/pecantv_features/{bonanza_info['video_filename']}"
                
                # Construct poster URL if we have artwork filename
                poster_url = current_poster_url
                if bonanza_info['artwork_filename']:
                    poster_url = f"https://storage.googleapis.com/pecantv_features/{bonanza_info['artwork_filename']}"
                
                # Update the episode
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, poster_url = %s, updated_at = %s
                    WHERE id = %s
                """, (content_url, poster_url, datetime.now(timezone.utc), ep_id))
                
                print(f"  ✅ Updated: S{season:02d}E{episode:02d} - {ep_title}")
                print(f"     Content URL: {content_url}")
                if poster_url != current_poster_url:
                    print(f"     Poster URL: {poster_url}")
                updated_count += 1
            else:
                print(f"  ❌ No metadata found for: S{season:02d}E{episode:02d} - {ep_title}")
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} Bonanza episodes!")
        
        # Show final status
        print("\n📊 Final Status Check:")
        print("-" * 30)
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN e.content_url IS NULL OR e.content_url = '' THEN 1 END) as missing,
                COUNT(CASE WHEN e.content_url IS NOT NULL AND e.content_url != '' THEN 1 END) as valid
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE c.title = 'Bonanza'
        """)
        
        total, missing, valid = cur.fetchone()
        print(f"  Bonanza: {valid}/{total} episodes have valid content URLs")
        
        if missing > 0:
            print(f"  ⚠️  {missing} episodes still missing content URLs")
        else:
            print(f"  ✅ All Bonanza episodes now have valid content URLs!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_bonanza_episodes_by_title() 