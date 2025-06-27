#!/usr/bin/env python3
"""
Script to load episodes from organized subfolders into the episodes table.
"""

import os
import pandas as pd
import psycopg2
import uuid
from datetime import datetime, timezone
import glob

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# Series to process (folders with underscores instead of spaces)
SERIES_FOLDERS = [
    'lone_ranger',
    'man_with_a_camera', 
    'ghost_squad',
    'bonanza',
    'count_of_monte_cristo',
    'mike_hammer'
]

BASE_FOLDER = '../pecantv_series'

def get_series_folders():
    """Get all series folders that exist."""
    if not os.path.exists(BASE_FOLDER):
        print(f"❌ Series base folder not found: {BASE_FOLDER}")
        return {}
    
    series_folders = {}
    for folder_name in os.listdir(BASE_FOLDER):
        folder_path = os.path.join(BASE_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            # Check if this folder maps to a known series
            if folder_name in SERIES_FOLDERS:
                series_name = folder_name.replace('_', ' ')
                series_folders[folder_name] = {
                    'folder_path': folder_path,
                    'series_name': series_name
                }
            else:
                print(f"⚠️  Unknown series folder: {folder_name}")
    
    return series_folders

def find_episode_files(folder_path):
    """Find episode files in a series folder."""
    episode_files = []
    
    # Look for common episode file formats
    file_patterns = [
        '*.xlsx',
        '*.xls', 
        '*.csv',
        '*.json'
    ]
    
    for pattern in file_patterns:
        files = glob.glob(os.path.join(folder_path, pattern))
        episode_files.extend(files)
    
    return episode_files

def load_episodes_from_file(file_path, series_name):
    """Load episodes from a file (Excel, CSV, or JSON)."""
    episodes = []
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext in ['.xlsx', '.xls']:
            # Load Excel file
            df = pd.read_excel(file_path)
            print(f"  📊 Loaded {len(df)} rows from Excel file")
            
        elif file_ext == '.csv':
            # Load CSV file
            df = pd.read_csv(file_path)
            print(f"  📊 Loaded {len(df)} rows from CSV file")
            
        elif file_ext == '.json':
            # Load JSON file
            df = pd.read_json(file_path)
            print(f"  📊 Loaded {len(df)} rows from JSON file")
            
        else:
            print(f"  ⚠️  Unsupported file format: {file_ext}")
            return episodes
        
        # Process each row
        for _, row in df.iterrows():
            episode = {
                'title': row.get('Title', row.get('title', '')),
                'description': row.get('Description', row.get('description', '')),
                'season_number': int(row.get('Season Number', row.get('season_number', 1))),
                'episode_number': int(row.get('Episode Number', row.get('episode_number', 1))),
                'runtime': int(row.get('Runtime', row.get('runtime', 60))),
                'content_url': row.get('Content URL', row.get('content_url', '')),
                'poster_url': row.get('Poster URL', row.get('poster_url', '')),
                'air_date': row.get('Air Date', row.get('air_date', None)),
                'genre': row.get('Genre', row.get('genre', 'Drama')),
                'rating': row.get('Rating', row.get('rating', 'NR'))
            }
            
            if episode['title']:  # Only add if title exists
                episodes.append(episode)
        
        print(f"  ✅ Extracted {len(episodes)} episodes from {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"  ❌ Error loading {file_path}: {e}")
    
    return episodes

def get_series_id(series_name):
    """Get the series ID from the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, uuid FROM content 
            WHERE type = 'SERIES' AND title = %s
        """, (series_name,))
        
        result = cur.fetchone()
        if result:
            return {'id': result[0], 'uuid': str(result[1])}
        else:
            print(f"  ❌ Series not found in database: {series_name}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error getting series ID: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def insert_episodes_to_database(episodes, series_info):
    """Insert episodes into the database."""
    if not episodes:
        return 0, 0
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        inserted_count = 0
        skipped_count = 0
        
        for episode in episodes:
            # Check if episode already exists by title
            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", 
                       (episode['title'], series_info['id']))
            if cur.fetchone():
                print(f"    ⚠️  Episode already exists by title, skipping: {episode['title']}")
                skipped_count += 1
                continue
            
            # Check if episode already exists by season/episode number
            cur.execute("SELECT id FROM episodes WHERE series_id = %s AND season_number = %s AND episode_number = %s", 
                       (series_info['id'], episode['season_number'], episode['episode_number']))
            if cur.fetchone():
                print(f"    ⚠️  Episode already exists by season/episode number, skipping: S{episode['season_number']}E{episode['episode_number']} - {episode['title']}")
                skipped_count += 1
                continue
            
            # Insert episode
            try:
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
                    series_info['id'],
                    series_info['uuid'],
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                print(f"    ✅ Inserted episode: {episode['title']}")
                inserted_count += 1
                
            except psycopg2.IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    print(f"    ⚠️  Duplicate constraint violation, skipping: {episode['title']}")
                    skipped_count += 1
                else:
                    print(f"    ❌ Integrity error for {episode['title']}: {e}")
                    skipped_count += 1
            except Exception as e:
                print(f"    ❌ Error inserting {episode['title']}: {e}")
                skipped_count += 1
        
        conn.commit()
        return inserted_count, skipped_count
        
    except Exception as e:
        print(f"  ❌ Error inserting episodes: {e}")
        conn.rollback()
        return 0, 0
    finally:
        cur.close()
        conn.close()

def process_series_folder(folder_name, folder_info):
    """Process a single series folder."""
    series_name = folder_info['series_name']
    folder_path = folder_info['folder_path']
    
    print(f"\n🎬 Processing: {series_name} (folder: {folder_name})")
    print("-" * 60)
    
    # Get series ID from database
    series_info = get_series_id(series_name)
    if not series_info:
        return 0, 0
    
    # Find episode files
    episode_files = find_episode_files(folder_path)
    if not episode_files:
        print(f"  ℹ️  No episode files found in {folder_path}")
        return 0, 0
    
    print(f"  📁 Found {len(episode_files)} episode files:")
    for file_path in episode_files:
        print(f"    • {os.path.basename(file_path)}")
    
    # Load episodes from all files
    all_episodes = []
    for file_path in episode_files:
        episodes = load_episodes_from_file(file_path, series_name)
        all_episodes.extend(episodes)
    
    if not all_episodes:
        print(f"  ℹ️  No episodes extracted from files")
        return 0, 0
    
    print(f"  📺 Total episodes extracted: {len(all_episodes)}")
    
    # Insert episodes into database
    inserted, skipped = insert_episodes_to_database(all_episodes, series_info)
    
    print(f"\n📊 Summary for {series_name}:")
    print(f"  Episodes inserted: {inserted}")
    print(f"  Episodes skipped: {skipped}")
    
    return inserted, skipped

def load_episodes_from_folders():
    """Load episodes from organized subfolders into the episodes table."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Loading Episodes from Organized Folders")
        print("=" * 50)
        
        total_inserted = 0
        
        for series_folder in SERIES_FOLDERS:
            folder_path = os.path.join(BASE_FOLDER, series_folder)
            if not os.path.exists(folder_path):
                print(f"⚠️  Folder not found: {folder_path}")
                continue
                
            print(f"\n📁 Processing series folder: {series_folder}")
            
            # Get the main series record
            series_name = series_folder.replace('_', ' ')
            cur.execute("""
                SELECT id, uuid, title FROM content 
                WHERE type = 'SERIES' AND title = %s
            """, (series_name,))
            series_record = cur.fetchone()
            
            if not series_record:
                print(f"❌ Main {series_name} series record not found")
                continue
                
            series_id, series_uuid, series_title = series_record
            print(f"✅ Found main series: {series_title} (ID: {series_id})")
            
            # Process episode files in the folder
            episode_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.mov', '.avi', '.mkv'))]
            
            if not episode_files:
                print(f"⚠️  No episode files found in {folder_path}")
                continue
                
            print(f"📹 Found {len(episode_files)} episode files")
            
            inserted = 0
            for episode_file in episode_files:
                # Extract episode info from filename
                episode_title = os.path.splitext(episode_file)[0]
                
                # Try to extract season/episode numbers from filename
                season_number = 1
                episode_number = 1
                
                # Check if episode already exists
                cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (episode_title, series_id))
                if cur.fetchone():
                    print(f"  ⚠️  Episode already exists, skipping: {episode_title}")
                    continue
                
                # Insert episode record
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
                    episode_title,
                    f"Episode of {series_title}",
                    season_number,
                    episode_number,
                    60,  # Default runtime
                    f"/content/{series_folder}/{episode_file}",  # Content URL
                    f"/posters/{series_folder}/default.jpg",  # Default poster URL
                    None,  # Air date
                    series_id,
                    str(series_uuid),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                print(f"  ✅ Inserted episode: {episode_title}")
                inserted += 1
                
            total_inserted += inserted
            print(f"📊 Inserted {inserted} episodes for {series_name}")
            
        conn.commit()
        print(f"\n🎉 Successfully inserted {total_inserted} total episodes into the episodes table.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_episodes_from_folders() 