#!/usr/bin/env python3
"""
Script to clean up fake Petrocelli episodes and reload actual data from Wurl metadata.
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

# Paths to the Wurl metadata files
WURL_FILES = [
    '../Wurl-File-Upload-Metadata_Version-7.0.40.xlsx',
    '../Wurl-File-Upload-Metadata_Version-7.0.41.xlsx'
]

SERIES_NAME = 'Petrocelli'

def load_petrocelli_from_wurl():
    """Load Petrocelli episodes from Wurl metadata files."""
    episodes = []
    
    for file in WURL_FILES:
        if not os.path.exists(file):
            print(f"❌ File not found: {file}")
            continue
            
        print(f"📖 Loading from: {file}")
        df = pd.read_excel(file)
        
        # Filter for Petrocelli content
        df_petrocelli = df[df['Series Name'].str.strip().str.lower() == SERIES_NAME.lower()]
        
        print(f"  Found {len(df_petrocelli)} Petrocelli entries")
        
        for _, row in df_petrocelli.iterrows():
            # Check if this is a video file (not a series)
            video_filename = row.get('Video Filename', '')
            if video_filename and video_filename.strip():
                episodes.append({
                    'title': row['Title'],
                    'description': row.get('Description', ''),
                    'season_number': int(row.get('Season Number', 1)),
                    'episode_number': int(row.get('Episode Number', 1)),
                    'runtime': int(row.get('Runtime', 60)),
                    'content_url': row.get('Content URL', ''),
                    'poster_url': row.get('Poster URL', ''),
                    'air_date': row.get('Air Date', None),
                    'genre': row.get('Genre', 'Drama'),
                    'rating': row.get('Rating', 'NR'),
                    'video_filename': video_filename.strip()
                })
    
    print(f"📺 Total Petrocelli episodes found: {len(episodes)}")
    return episodes

def clean_and_reload_petrocelli():
    """Clean up fake episodes and reload actual data."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🧹 CLEANING AND RELOADING PETROCELLI DATA")
        print("=" * 60)
        
        # Get the main series record
        cur.execute("SELECT id, uuid FROM content WHERE type = 'SERIES' AND title = %s", (SERIES_NAME,))
        series_record = cur.fetchone()
        if not series_record:
            print(f"❌ Main {SERIES_NAME} series record not found")
            return
        
        series_id, series_uuid = series_record['id'], series_record['uuid']
        print(f"✅ Found main series: {SERIES_NAME} (ID: {series_id})")
        
        # Remove all existing episodes (including the fake ones)
        cur.execute("DELETE FROM episodes WHERE series_id = %s", (series_id,))
        deleted_count = cur.rowcount
        print(f"🗑️  Deleted {deleted_count} existing episodes")
        
        # Load actual episodes from Wurl metadata
        episodes = load_petrocelli_from_wurl()
        
        if not episodes:
            print("❌ No episodes found in Wurl metadata")
            return
        
        # Insert the actual episodes
        inserted = 0
        for ep in episodes:
            # Check if episode already exists by video filename
            if ep.get('video_filename'):
                cur.execute("SELECT id FROM episodes WHERE content_url LIKE %s", (f"%{ep['video_filename']}%",))
                if cur.fetchone():
                    print(f"  ⚠️  Episode already exists, skipping: {ep['title']}")
                    continue
            
            # Check if episode already exists by title and series_id
            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (ep['title'], series_id))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists by title, skipping: {ep['title']}")
                continue
            
            # Check if episode already exists by (series_id, season_number, episode_number)
            cur.execute("SELECT id FROM episodes WHERE series_id = %s AND season_number = %s AND episode_number = %s", 
                       (series_id, ep['season_number'], ep['episode_number']))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists by season/episode number, skipping: S{ep['season_number']}E{ep['episode_number']} - {ep['title']}")
                continue
            
            # Insert the episode
            cur.execute("""
                INSERT INTO episodes (
                    uuid, title, description, season_number, episode_number, runtime,
                    content_url, poster_url, air_date, series_id, content_uuid,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                str(uuid.uuid4()),
                ep['title'],
                ep['description'],
                ep['season_number'],
                ep['episode_number'],
                ep['runtime'],
                ep['content_url'],
                ep['poster_url'],
                ep['air_date'],
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            
            print(f"  ✅ Inserted episode: {ep['title']}")
            if ep.get('video_filename'):
                print(f"     Video file: {ep['video_filename']}")
            inserted += 1
        
        conn.commit()
        print(f"\n✅ Successfully inserted {inserted} Petrocelli episodes from Wurl metadata")
        print("🎬 All fake episodes (10-22) have been removed")
        print("📺 Only actual episodes with real video files remain")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    clean_and_reload_petrocelli() 