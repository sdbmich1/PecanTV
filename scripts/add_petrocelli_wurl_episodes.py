#!/usr/bin/env python3
"""
Script to add the 5 additional Petrocelli episodes from Wurl metadata.
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
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

# The Wurl file with Petrocelli data
WURL_FILE = '../Wurl-File-Upload-Metadata_Version-7.0.19.xlsx'

def load_petrocelli_from_wurl():
    """Load Petrocelli episodes from the specific Wurl file."""
    if not os.path.exists(WURL_FILE):
        print(f"❌ File not found: {WURL_FILE}")
        return []
    
    print(f"📖 Loading from: {WURL_FILE}")
    df = pd.read_excel(WURL_FILE)
    
    # Filter for Petrocelli Animated Series
    df_petrocelli = df[df['Series Name'].str.strip().str.lower() == 'petrocelli animated series']
    
    print(f"Found {len(df_petrocelli)} Petrocelli Animated Series entries")
    
    episodes = []
    for _, row in df_petrocelli.iterrows():
        video_filename = row.get('Video Filename', '')
        if video_filename and video_filename.strip():
            episodes.append({
                'title': row['Title'],
                'description': row.get('Description', ''),
                'season_number': int(row.get('Season Number', 1)),
                'episode_number': int(row.get('Episode Number', 1)),
                'runtime': 60,  # Default runtime
                'video_filename': video_filename.strip(),
                'genre': 'Drama',
                'rating': 'NR'
            })
    
    return episodes

def add_petrocelli_wurl_episodes():
    """Add the Petrocelli episodes from Wurl metadata."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🎬 ADDING PETROCELLI EPISODES FROM WURL METADATA")
        print("=" * 60)
        
        # Get the main series record
        cur.execute("SELECT id, uuid FROM content WHERE type = 'SERIES' AND title = 'Petrocelli'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Petrocelli series not found")
            return
        
        series_id, series_uuid = series_record['id'], series_record['uuid']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Load episodes from Wurl metadata
        episodes = load_petrocelli_from_wurl()
        
        if not episodes:
            print("❌ No episodes found in Wurl metadata")
            return
        
        # Add the episodes
        inserted = 0
        for ep in episodes:
            episode_num = ep['episode_number']
            title = ep['title']
            video_filename = ep['video_filename']
            
            # Check if episode already exists
            cur.execute("SELECT id FROM episodes WHERE series_id = %s AND episode_number = %s", (series_id, episode_num))
            if cur.fetchone():
                print(f"  ⚠️  Episode {episode_num} already exists, skipping: {title}")
                continue
            
            # Build the content URL
            content_url = f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{video_filename}"
            
            # Insert the episode
            cur.execute("""
                INSERT INTO episodes (
                    uuid, title, description, season_number, episode_number, runtime,
                    content_url, series_id, content_uuid, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                str(uuid.uuid4()),
                title,
                ep['description'],
                ep['season_number'],
                episode_num,
                ep['runtime'],
                content_url,
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            
            print(f"  ✅ Added Episode {episode_num}: {title}")
            print(f"     File: {video_filename}")
            inserted += 1
        
        conn.commit()
        print(f"\n✅ Successfully added {inserted} Petrocelli episodes from Wurl metadata")
        print("🎬 These episodes complement the existing 9 episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_petrocelli_wurl_episodes() 