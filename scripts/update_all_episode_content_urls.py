#!/usr/bin/env python3
"""
Script to update content_url for all episodes in the episodes table where it is null or empty,
using the 'video filename' field from all Wurl metadata files in the Dropbox folder.
"""

import os
import pandas as pd
import glob
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

# Step 1: Build a lookup from all Wurl metadata files
print("📖 Scanning Wurl metadata files for all video filenames...")
lookup = {}

excel_files = glob.glob("Wurl*.xlsx")
csv_files = glob.glob("Wurl*.csv")

for file in excel_files:
    try:
        df = pd.read_excel(file)
        if 'Series Name' in df.columns:
            df['Series Name'] = df['Series Name'].astype(str).fillna('')
            for _, row in df.iterrows():
                series = str(row.get('Series Name', '')).strip().lower()
                title = str(row.get('Title', '')).strip()
                video_filename = str(row.get('Video Filename', '')).strip()
                season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                if video_filename and video_filename != 'nan':
                    key = (series, season, episode)
                    lookup[key] = video_filename
    except Exception as e:
        print(f"  ❌ Error reading {file}: {e}")

for file in csv_files:
    try:
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(file, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            print(f"  ❌ Could not read {file} with any encoding")
            continue
        if 'Series Name' in df.columns:
            df['Series Name'] = df['Series Name'].astype(str).fillna('')
            for _, row in df.iterrows():
                series = str(row.get('Series Name', '')).strip().lower()
                title = str(row.get('Title', '')).strip()
                video_filename = str(row.get('Video Filename', '')).strip()
                try:
                    season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                except (ValueError, TypeError):
                    season = 1
                try:
                    episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                except (ValueError, TypeError):
                    episode = 1
                if video_filename and video_filename != 'nan':
                    key = (series, season, episode)
                    lookup[key] = video_filename
    except Exception as e:
        print(f"  ❌ Error reading {file}: {e}")

print(f"✅ Built lookup for {len(lookup)} episodes from metadata files.")

# Step 2: Update episodes in the database
conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()
try:
    print("\n🔎 Checking episodes in the database with missing content_url...")
    cur.execute("""
        SELECT e.id, e.title, e.season_number, e.episode_number, c.title as series_title
        FROM episodes e
        JOIN content c ON e.series_id = c.id
        WHERE e.content_url IS NULL OR e.content_url = ''
    """)
    missing_episodes = cur.fetchall()
    print(f"Found {len(missing_episodes)} episodes with missing content_url.")
    updated = 0
    for ep_id, ep_title, season, episode, series_title in missing_episodes:
        key = (series_title.strip().lower(), season, episode)
        video_filename = lookup.get(key)
        if video_filename:
            content_url = f"https://storage.googleapis.com/pecantv_features/{video_filename}"
            cur.execute(
                "UPDATE episodes SET content_url = %s, updated_at = %s WHERE id = %s",
                (content_url, datetime.now(timezone.utc), ep_id)
            )
            print(f"  ✅ Updated: {series_title} S{season:02d}E{episode:02d} - {ep_title}")
            print(f"     URL: {content_url}")
            updated += 1
        else:
            print(f"  ❌ No video filename found for: {series_title} S{season:02d}E{episode:02d} - {ep_title}")
    conn.commit()
    print(f"\n✅ Updated {updated} episodes with new content URLs.")
finally:
    cur.close()
    conn.close() 