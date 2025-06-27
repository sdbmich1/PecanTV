#!/usr/bin/env python3
"""
Script to load Petrocelli episodes from Wurl metadata files into the episodes table.
"""

import pandas as pd
import psycopg2
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

# Files that contain Petrocelli episodes
PETROCELLI_FILES = [
    'Wurl - File Upload Metadata_Version 7.0.35.csv',
    'Wurl - File Upload Metadata_Version 7.0.36.csv',
    'Wurl - File Upload Metadata_Version 7.0.32.csv'
]

SERIES_NAME = 'Petrocelli'

def load_petrocelli_episodes_from_files():
    """Load all Petrocelli episodes from the Wurl metadata files."""
    episodes = []
    
    for file in PETROCELLI_FILES:
        try:
            print(f"📁 Processing: {file}")
            df = pd.read_csv(file)
            
            # Filter for Petrocelli episodes
            petrocelli = df[df['Series Name'].str.strip().str.lower() == SERIES_NAME.lower()]
            
            if len(petrocelli) > 0:
                print(f"  ✅ Found {len(petrocelli)} Petrocelli episodes")
                
                for _, row in petrocelli.iterrows():
                    episode_data = {
                        'title': row.get('Title', ''),
                        'description': row.get('Description', ''),
                        'season_number': int(row.get('Season Number', 1)),
                        'episode_number': int(row.get('Episode Number', 1)),
                        'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60,
                        'content_url': row.get('Content URL', ''),
                        'poster_url': row.get('Poster URL', ''),
                        'air_date': row.get('Air Date', None),
                        'genre': row.get('Genre', 'Drama'),
                        'rating': row.get('Rating', 'NR')
                    }
                    episodes.append(episode_data)
            else:
                print(f"  ❌ No Petrocelli episodes found")
                
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    # Remove duplicates based on title
    unique_episodes = {}
    for episode in episodes:
        title = episode['title']
        if title not in unique_episodes:
            unique_episodes[title] = episode
    
    print(f"\n📊 Found {len(unique_episodes)} unique Petrocelli episodes")
    return list(unique_episodes.values())

def load_petrocelli_episodes():
    """Load Petrocelli episodes into the episodes table."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Loading Petrocelli Episodes from Wurl Metadata Files")
        print("=" * 60)
        
        # Get the main series record
        cur.execute("""
            SELECT id, uuid, title FROM content 
            WHERE type = 'SERIES' AND title = %s
        """, (SERIES_NAME,))
        series_record = cur.fetchone()
        
        if not series_record:
            print(f"❌ Main {SERIES_NAME} series record not found")
            return
        
        series_id, series_uuid, series_title = series_record
        print(f"✅ Found main series: {series_title} (ID: {series_id})")
        
        # Load episodes from files
        episodes = load_petrocelli_episodes_from_files()
        
        if not episodes:
            print("❌ No episodes found to load")
            return
        
        inserted = 0
        skipped = 0
        
        for episode in episodes:
            # Check if episode already exists by title and series_id
            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", 
                       (episode['title'], series_id))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists, skipping: {episode['title']}")
                skipped += 1
                continue
            
            # Check if episode already exists by (series_id, season_number, episode_number)
            cur.execute("SELECT id FROM episodes WHERE series_id = %s AND season_number = %s AND episode_number = %s", 
                       (series_id, episode['season_number'], episode['episode_number']))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists by season/episode number, skipping: S{episode['season_number']}E{episode['episode_number']} - {episode['title']}")
                skipped += 1
                continue
            
            # Insert new episode
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
                episode['title'],
                episode['description'],
                episode['season_number'],
                episode['episode_number'],
                episode['runtime'],
                episode['content_url'],
                episode['poster_url'],
                episode['air_date'],
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            
            print(f"  ✅ Inserted episode: S{episode['season_number']}E{episode['episode_number']} - {episode['title']}")
            inserted += 1
        
        # Commit changes
        conn.commit()
        
        print(f"\n📊 Summary:")
        print("-" * 40)
        print(f"Episodes inserted: {inserted}")
        print(f"Episodes skipped: {skipped}")
        print(f"Total processed: {inserted + skipped}")
        
        if inserted > 0:
            print(f"\n✅ Successfully loaded {inserted} new Petrocelli episodes into the episodes table!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_petrocelli_episodes() 