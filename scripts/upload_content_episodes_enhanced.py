#!/usr/bin/env python3
"""
Enhanced Excel/CSV Data Upload Script for PecanTV
Uploads film and episode data from Excel or CSV files with duplicate detection and data validation.
Handles both XLSX and CSV files, with options to skip duplicates or update existing records.
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys
from datetime import datetime
import argparse
from pathlib import Path
import glob
import re

# Neon database connection
NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_to_neon():
    """Connect to Neon database."""
    try:
        conn = psycopg2.connect(NEON_CONNECTION_STRING)
        print("✅ Connected to Neon database successfully!")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None

def read_data_file(file_path, sheet_name=None):
    """Read Excel or CSV file and return DataFrame."""
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.xlsx', '.xls']:
            # Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                # Read all sheets
                excel_file = pd.ExcelFile(file_path)
                sheets = {}
                for sheet in excel_file.sheet_names:
                    sheets[sheet] = pd.read_excel(file_path, sheet_name=sheet)
                return sheets
        elif file_ext == '.csv':
            # CSV file - try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    print(f"✅ Read {len(df)} rows from {file_path} using {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print(f"❌ Could not read {file_path} with any encoding")
                return None
                
            if sheet_name:
                print("⚠️  Warning: Sheet name specified but reading CSV file. Ignoring sheet parameter.")
        else:
            print(f"❌ Unsupported file format: {file_ext}")
            print("Supported formats: .xlsx, .xls, .csv")
            return None
        
        return df
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def get_id_maps(conn):
    """Get maps of names to IDs for genres and ratings."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM genres")
        genre_map = {row[1].lower(): row[0] for row in cur.fetchall()}
        
        cur.execute("SELECT id, code FROM ratings")
        rating_map = {row[1].lower(): row[0] for row in cur.fetchall()}
    
    return genre_map, rating_map

def get_existing_content(conn):
    """Get existing content titles to check for duplicates."""
    with conn.cursor() as cur:
        cur.execute("SELECT title FROM content")
        existing_titles = {row[0].lower() for row in cur.fetchall()}
    return existing_titles

def clean_text(text):
    """Clean and normalize text data."""
    if pd.isna(text):
        return None
    return str(text).strip()

def validate_content_data(row, actual_columns, filename, genre_map, rating_map):
    """Validate content data and return cleaned values."""
    try:
        # Extract values with fallbacks
        title = clean_text(row.get(actual_columns.get('title', 'title'), ''))
        if not title:
            return None  # Skip rows without title
            
        poster_url = clean_text(row.get(actual_columns.get('poster_url', 'poster_url'), ''))
        trailer_url = clean_text(row.get(actual_columns.get('trailer_url', 'trailer_url'), ''))
        content_url = clean_text(row.get(actual_columns.get('content_url', 'content_url'), ''))
        description = clean_text(row.get(actual_columns.get('description', 'description'), ''))
        
        # Handle required fields - skip if poster_url is missing
        if not poster_url:
            print(f"⚠️  Skipping row with missing poster_url: {title}")
            return None
        
        # Construct proper URLs with correct folder paths
        if poster_url and not poster_url.startswith('http'):
            poster_url = f"https://storage.googleapis.com/pecantv_title_images/{poster_url}"
        
        if content_url and not content_url.startswith('http'):
            content_url = f"https://storage.googleapis.com/pecantv_features/{content_url}"
        
        if trailer_url and not trailer_url.startswith('http'):
            trailer_url = f"https://storage.googleapis.com/pecantv_trailers/{trailer_url}"
        
        # Handle content type (robust mapping)
        content_type = clean_text(row.get(actual_columns.get('type', 'type'), 'FILM'))
        if content_type:
            content_type = content_type.upper()
            if content_type == 'MOVIE':
                content_type = 'FILM'
            if content_type not in ['FILM', 'SERIES']:
                content_type = 'FILM'  # Default
        else:
            content_type = 'FILM'
        
        # Handle runtime
        runtime = row.get(actual_columns.get('runtime', 'runtime'), 0)
        try:
            runtime = int(runtime) if pd.notna(runtime) else 0
        except:
            runtime = 0
        
        # Handle genre
        genre_name = clean_text(row.get(actual_columns.get('genre', 'genre'), ''))
        genre_id = None
        if genre_name:
            genre_id = genre_map.get(genre_name.lower())
        
        # Handle rating
        rating_code = clean_text(row.get(actual_columns.get('rating', 'rating'), ''))
        rating_id = None
        if rating_code:
            rating_id = rating_map.get(rating_code.lower())
        
        # Handle release date
        release_date = row.get(actual_columns.get('release_date', 'release_date'))
        if pd.notna(release_date):
            try:
                if isinstance(release_date, str):
                    release_date = pd.to_datetime(release_date).date()
                else:
                    release_date = pd.to_datetime(release_date).date()
            except:
                release_date = None
        else:
            release_date = None
        
        return {
            'title': title,
            'poster_url': poster_url,
            'trailer_url': trailer_url,
            'content_url': content_url,
            'description': description,
            'content_type': content_type,
            'runtime': runtime,
            'genre_id': genre_id,
            'rating_id': rating_id,
            'release_date': release_date
        }
        
    except Exception as e:
        print(f"⚠️  Error processing row in {filename}: {e}")
        return None

def insert_content(conn, content_df, genre_map, rating_map, filename, update_existing=True, skip_duplicates=False):
    """Insert content into the database with duplicate handling."""
    print(f"📝 Processing {len(content_df)} content items from {filename}...")
    
    # Get existing content titles
    existing_titles = get_existing_content(conn)
    
    # Expected columns mapping
    column_mapping = {
        'title': ['title', 'name', 'Title', 'Name', 'Internal Title'],
        'poster_url': ['poster_url', 'poster', 'image_url', 'Poster URL', 'Artwork Filename'],
        'trailer_url': ['trailer_url', 'trailer', 'video_url', 'Trailer URL'],
        'content_url': ['content_url', 'content', 'stream_url', 'Content URL', 'Video Filename'],
        'description': ['description', 'desc', 'plot', 'Description', 'Short Description'],
        'type': ['type', 'content_type', 'Type', 'Entry Type'],
        'runtime': ['runtime', 'duration', 'length', 'Runtime'],
        'genre': ['genre', 'genres', 'category', 'Genre', 'Genre Value'],
        'rating': ['rating', 'age_rating', 'Rating', 'Rating Value'],
        'release_date': ['release_date', 'date', 'year', 'Release Date']
    }
    
    # Find actual columns in the DataFrame
    actual_columns = {}
    for expected_col, possible_names in column_mapping.items():
        for possible_name in possible_names:
            if possible_name in content_df.columns:
                actual_columns[expected_col] = possible_name
                break
    
    print(f"🔍 Found columns: {actual_columns}")
    
    # Prepare data for insertion
    data_to_insert = []
    skipped_count = 0
    duplicate_count = 0
    
    for _, row in content_df.iterrows():
        # Validate and clean data
        content_data = validate_content_data(row, actual_columns, filename, genre_map, rating_map)
        if not content_data:
            continue
        
        # Check for duplicates
        if content_data['title'].lower() in existing_titles:
            duplicate_count += 1
            if skip_duplicates:
                print(f"⏭️  Skipping duplicate: {content_data['title']}")
                continue
            else:
                print(f"🔄 Updating existing: {content_data['title']}")
        
        data_to_insert.append((
            content_data['title'], content_data['poster_url'], content_data['trailer_url'],
            content_data['content_url'], content_data['description'], content_data['content_type'],
            content_data['runtime'], content_data['genre_id'], content_data['rating_id'],
            content_data['release_date']
        ))
    
    if not data_to_insert:
        print(f"❌ No valid data to insert from {filename}")
        return 0, skipped_count, duplicate_count
    
    # Insert data with appropriate conflict handling
    with conn.cursor() as cur:
        if update_existing:
            # Update existing records
            execute_values(
                cur,
                """
                INSERT INTO content (
                    title, poster_url, trailer_url, content_url,
                    description, type, runtime, genre_id, rating_id,
                    release_date
                )
                VALUES %s
                ON CONFLICT (title) DO UPDATE
                SET poster_url = EXCLUDED.poster_url,
                    trailer_url = EXCLUDED.trailer_url,
                    content_url = EXCLUDED.content_url,
                    description = EXCLUDED.description,
                    type = EXCLUDED.type,
                    runtime = EXCLUDED.runtime,
                    genre_id = EXCLUDED.genre_id,
                    rating_id = EXCLUDED.rating_id,
                    release_date = EXCLUDED.release_date
                """,
                data_to_insert
            )
        else:
            # Skip duplicates
            execute_values(
                cur,
                """
                INSERT INTO content (
                    title, poster_url, trailer_url, content_url,
                    description, type, runtime, genre_id, rating_id,
                    release_date
                )
                VALUES %s
                ON CONFLICT (title) DO NOTHING
                """,
                data_to_insert
            )
    
    conn.commit()
    print(f"✅ Inserted {len(data_to_insert)} content items from {filename}")
    print(f"   Skipped: {skipped_count}, Duplicates: {duplicate_count}")
    return len(data_to_insert), skipped_count, duplicate_count

def insert_episodes(conn, episodes_df, filename, update_existing=True, skip_duplicates=False):
    """Insert episodes into the database with duplicate handling."""
    print(f"📝 Processing {len(episodes_df)} episodes from {filename}...")
    
    # Get existing episodes to check for duplicates
    with conn.cursor() as cur:
        cur.execute("SELECT title, season_number, episode_number FROM episodes")
        existing_episodes = {(row[0].lower(), row[1], row[2]) for row in cur.fetchall()}
    
    # Expected columns mapping for episodes
    column_mapping = {
        'title': ['title', 'name', 'Title', 'Name', 'Episode Title'],
        'series_title': ['series_title', 'show_title', 'Series Title', 'Show Title'],
        'season_number': ['season_number', 'season', 'Season Number', 'Season'],
        'episode_number': ['episode_number', 'episode', 'Episode Number', 'Episode'],
        'description': ['description', 'desc', 'plot', 'Description'],
        'runtime': ['runtime', 'duration', 'length', 'Runtime'],
        'content_url': ['content_url', 'content', 'stream_url', 'Content URL', 'Video Filename'],
        'poster_url': ['poster_url', 'poster', 'image_url', 'Poster URL', 'Artwork Filename']
    }
    
    # Find actual columns in the DataFrame
    actual_columns = {}
    for expected_col, possible_names in column_mapping.items():
        for possible_name in possible_names:
            if possible_name in episodes_df.columns:
                actual_columns[expected_col] = possible_name
                break
    
    print(f"🔍 Found episode columns: {actual_columns}")
    
    # Prepare data for insertion
    data_to_insert = []
    skipped_count = 0
    duplicate_count = 0
    
    for _, row in episodes_df.iterrows():
        try:
            # Extract values
            title = clean_text(row.get(actual_columns.get('title', 'title'), ''))
            if not title:
                continue
            
            series_title = clean_text(row.get(actual_columns.get('series_title', 'series_title'), ''))
            if not series_title:
                continue
            
            # Handle season and episode numbers
            season_number = row.get(actual_columns.get('season_number', 'season_number'), 1)
            episode_number = row.get(actual_columns.get('episode_number', 'episode_number'), 1)
            
            try:
                season_number = int(season_number) if pd.notna(season_number) else 1
                episode_number = int(episode_number) if pd.notna(episode_number) else 1
            except:
                season_number = 1
                episode_number = 1
            
            # Check for duplicates
            episode_key = (title.lower(), season_number, episode_number)
            if episode_key in existing_episodes:
                duplicate_count += 1
                if skip_duplicates:
                    print(f"⏭️  Skipping duplicate episode: {title} S{season_number}E{episode_number}")
                    continue
                else:
                    print(f"🔄 Updating existing episode: {title} S{season_number}E{episode_number}")
            
            # Extract other fields
            description = clean_text(row.get(actual_columns.get('description', 'description'), ''))
            runtime = row.get(actual_columns.get('runtime', 'runtime'), 0)
            try:
                runtime = int(runtime) if pd.notna(runtime) else 0
            except:
                runtime = 0
            
            content_url = clean_text(row.get(actual_columns.get('content_url', 'content_url'), ''))
            poster_url = clean_text(row.get(actual_columns.get('poster_url', 'poster_url'), ''))
            
            # Construct proper URLs
            if content_url and not content_url.startswith('http'):
                content_url = f"https://storage.googleapis.com/pecantv_features/{content_url}"
            
            if poster_url and not poster_url.startswith('http'):
                poster_url = f"https://storage.googleapis.com/pecantv_title_images/{poster_url}"
            
            data_to_insert.append((
                title, series_title, season_number, episode_number,
                description, runtime, content_url, poster_url
            ))
            
        except Exception as e:
            print(f"⚠️  Error processing episode row in {filename}: {e}")
            continue
    
    if not data_to_insert:
        print(f"❌ No valid episodes to insert from {filename}")
        return 0, skipped_count, duplicate_count
    
    # Insert episodes with appropriate conflict handling
    with conn.cursor() as cur:
        if update_existing:
            # Update existing episodes
            execute_values(
                cur,
                """
                INSERT INTO episodes (
                    title, series_title, season_number, episode_number,
                    description, runtime, content_url, poster_url
                )
                VALUES %s
                ON CONFLICT (title, season_number, episode_number) DO UPDATE
                SET series_title = EXCLUDED.series_title,
                    description = EXCLUDED.description,
                    runtime = EXCLUDED.runtime,
                    content_url = EXCLUDED.content_url,
                    poster_url = EXCLUDED.poster_url
                """,
                data_to_insert
            )
        else:
            # Skip duplicates
            execute_values(
                cur,
                """
                INSERT INTO episodes (
                    title, series_title, season_number, episode_number,
                    description, runtime, content_url, poster_url
                )
                VALUES %s
                ON CONFLICT (title, season_number, episode_number) DO NOTHING
                """,
                data_to_insert
            )
    
    conn.commit()
    print(f"✅ Inserted {len(data_to_insert)} episodes from {filename}")
    print(f"   Skipped: {skipped_count}, Duplicates: {duplicate_count}")
    return len(data_to_insert), skipped_count, duplicate_count

def find_data_files(folder_path, pattern=None):
    """Find Excel and CSV files in the folder, optionally matching a pattern."""
    if pattern:
        # Use glob pattern for specific files
        search_pattern = os.path.join(folder_path, pattern)
        files = glob.glob(search_pattern)
    else:
        # Find all Excel and CSV files
        files = []
        for ext in ['*.xlsx', '*.xls', '*.csv']:
            files.extend(glob.glob(os.path.join(folder_path, ext)))
    
    # Sort files naturally (so 7.0.12 comes before 7.0.61)
    files.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    return files

def main():
    parser = argparse.ArgumentParser(description='Enhanced upload script for Excel/CSV files to Neon database')
    parser.add_argument('file_path', help='Path to Excel/CSV file or folder containing files')
    parser.add_argument('--sheet', help='Sheet name for Excel files (optional)')
    parser.add_argument('--content-only', action='store_true', help='Only process content, skip episodes')
    parser.add_argument('--episodes-only', action='store_true', help='Only process episodes, skip content')
    parser.add_argument('--skip-duplicates', action='store_true', help='Skip duplicate records instead of updating')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be uploaded without actually uploading')
    parser.add_argument('--pattern', help='File pattern to match (e.g., "*.csv" or "*7.0.*")')
    
    args = parser.parse_args()
    
    # Connect to database
    conn = connect_to_neon()
    if not conn:
        sys.exit(1)
    
    try:
        # Get ID maps
        genre_map, rating_map = get_id_maps(conn)
        
        # Determine if we're processing a single file or a folder
        if os.path.isfile(args.file_path):
            files = [args.file_path]
        else:
            files = find_data_files(args.file_path, args.pattern)
        
        if not files:
            print(f"❌ No files found in {args.file_path}")
            sys.exit(1)
        
        print(f"📁 Found {len(files)} files to process")
        
        total_content_inserted = 0
        total_episodes_inserted = 0
        total_content_skipped = 0
        total_episodes_skipped = 0
        total_content_duplicates = 0
        total_episodes_duplicates = 0
        
        for file_path in files:
            print(f"\n📄 Processing: {file_path}")
            
            # Read data file
            data = read_data_file(file_path, args.sheet)
            if data is None or (isinstance(data, pd.DataFrame) and data.empty) or (isinstance(data, dict) and not data):
                continue
            
            # Handle multiple sheets or single DataFrame
            if isinstance(data, dict):
                # Multiple sheets
                for sheet_name, df in data.items():
                    print(f"📊 Processing sheet: {sheet_name}")
                    if not args.episodes_only:
                        content_inserted, content_skipped, content_duplicates = insert_content(
                            conn, df, genre_map, rating_map, f"{file_path}::{sheet_name}",
                            update_existing=not args.skip_duplicates,
                            skip_duplicates=args.skip_duplicates
                        )
                        total_content_inserted += content_inserted
                        total_content_skipped += content_skipped
                        total_content_duplicates += content_duplicates
                    
                    if not args.content_only:
                        episodes_inserted, episodes_skipped, episodes_duplicates = insert_episodes(
                            conn, df, f"{file_path}::{sheet_name}",
                            update_existing=not args.skip_duplicates,
                            skip_duplicates=args.skip_duplicates
                        )
                        total_episodes_inserted += episodes_inserted
                        total_episodes_skipped += episodes_skipped
                        total_episodes_duplicates += episodes_duplicates
            else:
                # Single DataFrame
                if not args.episodes_only:
                    content_inserted, content_skipped, content_duplicates = insert_content(
                        conn, data, genre_map, rating_map, file_path,
                        update_existing=not args.skip_duplicates,
                        skip_duplicates=args.skip_duplicates
                    )
                    total_content_inserted += content_inserted
                    total_content_skipped += content_skipped
                    total_content_duplicates += content_duplicates
                
                if not args.content_only:
                    episodes_inserted, episodes_skipped, episodes_duplicates = insert_episodes(
                        conn, data, file_path,
                        update_existing=not args.skip_duplicates,
                        skip_duplicates=args.skip_duplicates
                    )
                    total_episodes_inserted += episodes_inserted
                    total_episodes_skipped += episodes_skipped
                    total_episodes_duplicates += episodes_duplicates
        
        # Summary
        print(f"\n🎉 Upload Summary:")
        print(f"   Content: {total_content_inserted} inserted, {total_content_skipped} skipped, {total_content_duplicates} duplicates")
        print(f"   Episodes: {total_episodes_inserted} inserted, {total_episodes_skipped} skipped, {total_episodes_duplicates} duplicates")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main() 