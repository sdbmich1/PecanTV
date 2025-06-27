#!/usr/bin/env python3
"""
Script to update Longstreet series with proper episode numbers and create episodes table entries.
"""

import os
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

# Paths to the Wurl metadata files
WURL_FILES = [
    '../Wurl-File-Upload-Metadata_Version-7.0.40.xlsx',
    '../Wurl-File-Upload-Metadata_Version-7.0.41.xlsx'
]

SERIES_NAME = 'Longstreet'

def load_longstreet_episodes_from_excel():
    """Load all Longstreet episodes from the Wurl metadata Excel files."""
    episodes = []
    for file in WURL_FILES:
        if not os.path.exists(file):
            print(f"❌ File not found: {file}")
            continue
        df = pd.read_excel(file)
        # Filter for Longstreet episodes
        df_ls = df[df['Series Name'].str.strip().str.lower() == SERIES_NAME.lower()]
        for _, row in df_ls.iterrows():
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
                'rating': row.get('Rating', 'NR')
            })
    print(f"Loaded {len(episodes)} Longstreet episodes from Excel files.")
    return episodes

def update_longstreet_episodes():
    """Update Longstreet episodes with proper episode numbers and create episodes table entries."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        print("🎬 Updating Longstreet Series from Wurl Metadata Files")
        print("=" * 50)
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
        # Load episodes from Excel
        episodes = load_longstreet_episodes_from_excel()
        inserted = 0
        for ep in episodes:
            # Check if episode already exists in episodes table by title and series_id
            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (ep['title'], series_id))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists by title, skipping: {ep['title']}")
                continue
            # Check if episode already exists by (series_id, season_number, episode_number)
            cur.execute("SELECT id FROM episodes WHERE series_id = %s AND season_number = %s AND episode_number = %s", (series_id, ep['season_number'], ep['episode_number']))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists by season/episode number, skipping: S{ep['season_number']}E{ep['episode_number']} - {ep['title']}")
                continue
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
            inserted += 1
        conn.commit()
        print(f"\n✅ Inserted {inserted} new Longstreet episodes into the episodes table.")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_longstreet_episodes() 