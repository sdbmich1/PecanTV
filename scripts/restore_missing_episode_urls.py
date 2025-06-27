#!/usr/bin/env python3
"""
Script to restore missing content URLs for Longstreet and Petrocelli episodes from Wurl metadata files.
"""

import os
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

# Paths to the Wurl metadata files
WURL_FILES = [
    'Wurl-File-Upload-Metadata_Version-7.0.40.xlsx',
    'Wurl-File-Upload-Metadata_Version-7.0.41.xlsx'
]

def load_episode_data_from_wurl():
    """Load episode data from Wurl metadata files."""
    episodes_data = {}
    
    for file in WURL_FILES:
        if not os.path.exists(file):
            print(f"❌ File not found: {file}")
            continue
            
        print(f"📖 Reading {file}...")
        df = pd.read_excel(file)
        
        # Filter for Longstreet and Petrocelli episodes
        for series_name in ['Longstreet', 'Petrocelli']:
            df_series = df[df['Series Name'].str.strip().str.lower() == series_name.lower()]
            
            if series_name not in episodes_data:
                episodes_data[series_name] = []
                
            for _, row in df_series.iterrows():
                video_filename = row.get('Video Filename', '')
                if video_filename and video_filename.strip():
                    episodes_data[series_name].append({
                        'title': row['Title'],
                        'video_filename': video_filename.strip(),
                        'season_number': int(row.get('Season Number', 1)),
                        'episode_number': int(row.get('Episode Number', 1))
                    })
    
    return episodes_data

def restore_missing_episode_urls():
    """Restore missing content URLs for episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Restoring Missing Episode Content URLs")
        print("=" * 50)
        
        # Load episode data from Wurl files
        wurl_episodes = load_episode_data_from_wurl()
        
        for series_name, episodes in wurl_episodes.items():
            print(f"\n📺 Processing {series_name} episodes...")
            print("-" * 40)
            
            # Get series ID
            cur.execute("SELECT id FROM content WHERE title = %s AND type = 'SERIES'", (series_name,))
            series_result = cur.fetchone()
            if not series_result:
                print(f"❌ Series '{series_name}' not found")
                continue
                
            series_id = series_result[0]
            updated_count = 0
            
            for ep_data in episodes:
                title = ep_data['title']
                video_filename = ep_data['video_filename']
                season = ep_data['season_number']
                episode = ep_data['episode_number']
                
                # Check if episode exists and has empty content_url
                cur.execute("""
                    SELECT id, content_url FROM episodes 
                    WHERE series_id = %s AND title = %s
                """, (series_id, title))
                
                episode_result = cur.fetchone()
                if episode_result:
                    ep_id, current_url = episode_result
                    
                    if not current_url or current_url.strip() == '':
                        # Construct the content URL
                        content_url = f"https://storage.googleapis.com/pecantv_features/{video_filename}"
                        
                        # Update the episode
                        cur.execute("""
                            UPDATE episodes 
                            SET content_url = %s, updated_at = %s
                            WHERE id = %s
                        """, (content_url, datetime.now(timezone.utc), ep_id))
                        
                        print(f"  ✅ Updated S{season:02d}E{episode:02d} - {title}")
                        print(f"     URL: {content_url}")
                        updated_count += 1
                    else:
                        print(f"  ⚠️  S{season:02d}E{episode:02d} - {title} already has URL")
                else:
                    print(f"  ❌ Episode not found: {title}")
            
            print(f"\n📊 {series_name} Summary: Updated {updated_count} episodes")
        
        conn.commit()
        print(f"\n✅ Successfully restored missing content URLs!")
        
        # Show final status
        print("\n📊 Final Status Check:")
        print("-" * 30)
        for series_name in ['Longstreet', 'Petrocelli']:
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN e.content_url IS NULL OR e.content_url = '' THEN 1 END) as missing,
                    COUNT(CASE WHEN e.content_url IS NOT NULL AND e.content_url != '' THEN 1 END) as valid
                FROM episodes e
                JOIN content c ON e.series_id = c.id
                WHERE c.title = %s
            """, (series_name,))
            
            total, missing, valid = cur.fetchone()
            print(f"  {series_name}: {valid}/{total} episodes have valid URLs")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    restore_missing_episode_urls() 