#!/usr/bin/env python3
"""
Script to restore content URLs for episodes from Wurl metadata files.
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

def load_wurl_episodes():
    """Load episode data from Wurl metadata files."""
    episodes = {}
    
    # Get all CSV files
    csv_files = [f for f in os.listdir('.') if f.startswith('Wurl - File Upload Metadata_Version 7.0.') and f.endswith('.csv')]
    
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            print(f"Processing {file}...")
            
            # Check if required columns exist
            required_cols = ['Series Name', 'Title', 'Video Filename']
            if not all(col in df.columns for col in required_cols):
                print(f"  Skipping {file} - missing required columns")
                continue
            
            # Filter for Ghost Squad and Commando Cody episodes
            for _, row in df.iterrows():
                series_name = str(row.get('Series Name', '')).strip()
                title = str(row.get('Title', '')).strip()
                video_filename = str(row.get('Video Filename', '')).strip()
                
                if series_name.lower() in ['ghost squad', 'commando cody'] and video_filename and video_filename != 'nan':
                    # Construct content URL from video filename
                    content_url = f"https://storage.googleapis.com/pecantv_features/{video_filename}"
                    
                    key = f"{series_name}|{title}"
                    episodes[key] = {
                        'series_name': series_name,
                        'title': title,
                        'content_url': content_url,
                        'file': file
                    }
                    
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    return episodes

def restore_episode_content_urls():
    """Restore content URLs for episodes from Wurl metadata."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Loading episode data from Wurl metadata files...")
        wurl_episodes = load_wurl_episodes()
        
        print(f"✅ Found {len(wurl_episodes)} episodes with content URLs")
        
        # Get series IDs
        cur.execute("SELECT id, title FROM content WHERE title ILIKE '%Ghost Squad%' OR title ILIKE '%Commando Cody%'")
        series_map = {row[1].lower(): row[0] for row in cur.fetchall()}
        
        updated_count = 0
        
        for key, episode_data in wurl_episodes.items():
            series_name = episode_data['series_name']
            title = episode_data['title']
            content_url = episode_data['content_url']
            
            # Find matching series
            series_id = None
            for series_title, series_id_val in series_map.items():
                if series_name.lower() in series_title or series_title in series_name.lower():
                    series_id = series_id_val
                    break
            
            if not series_id:
                print(f"❌ No matching series found for: {series_name}")
                continue
            
            # Update episode content URL
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE series_id = %s AND title = %s
            """, (content_url, datetime.now(timezone.utc), series_id, title))
            
            if cur.rowcount > 0:
                print(f"✅ Updated: {title} (Series: {series_name})")
                print(f"   Content URL: {content_url}")
                updated_count += 1
            else:
                print(f"⚠️  No episode found to update: {title} (Series: {series_name})")
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} episodes with content URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    restore_episode_content_urls() 