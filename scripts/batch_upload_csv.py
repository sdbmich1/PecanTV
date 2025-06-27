#!/usr/bin/env python3
"""
Batch CSV Upload Script for PecanTV
Automatically processes all CSV files in a folder, specifically for Wurl sequence files.
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

def get_id_maps(conn):
    """Get maps of names to IDs for genres and ratings."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM genres")
        genre_map = {row[1].lower(): row[0] for row in cur.fetchall()}
        
        cur.execute("SELECT id, code FROM ratings")
        rating_map = {row[1].lower(): row[0] for row in cur.fetchall()}
    
    return genre_map, rating_map

def clean_text(text):
    """Clean and normalize text data."""
    if pd.isna(text):
        return None
    return str(text).strip()

def insert_content(conn, content_df, genre_map, rating_map, filename):
    """Insert content into the database."""
    print(f"📝 Processing {len(content_df)} content items from {filename}...")
    
    # Expected columns mapping (based on Wurl CSV format)
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
    for _, row in content_df.iterrows():
        try:
            # Extract values with fallbacks
            title = clean_text(row.get(actual_columns.get('title', 'title'), ''))
            if not title:
                continue  # Skip rows without title
                
            poster_url = clean_text(row.get(actual_columns.get('poster_url', 'poster_url'), ''))
            trailer_url = clean_text(row.get(actual_columns.get('trailer_url', 'trailer_url'), ''))
            content_url = clean_text(row.get(actual_columns.get('content_url', 'content_url'), ''))
            description = clean_text(row.get(actual_columns.get('description', 'description'), ''))
            
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
            
            data_to_insert.append((
                title, poster_url, trailer_url, content_url, description,
                content_type, runtime, genre_id, rating_id, release_date
            ))
            
        except Exception as e:
            print(f"⚠️  Error processing row in {filename}: {e}")
            continue
    
    if not data_to_insert:
        print(f"❌ No valid data to insert from {filename}")
        return 0
    
    # Insert data
    with conn.cursor() as cur:
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
    conn.commit()
    print(f"✅ Inserted {len(data_to_insert)} content items from {filename}")
    return len(data_to_insert)

def find_csv_files(folder_path, pattern=None):
    """Find CSV files in the folder, optionally matching a pattern."""
    if pattern:
        # Use glob pattern for specific files
        search_pattern = os.path.join(folder_path, pattern)
        files = glob.glob(search_pattern)
    else:
        # Find all CSV files
        files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    # Sort files naturally (so 7.0.12 comes before 7.0.61)
    files.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    return files

def main():
    parser = argparse.ArgumentParser(description='Batch upload CSV files to Neon database')
    parser.add_argument('folder_path', help='Path to folder containing CSV files')
    parser.add_argument('--pattern', help='File pattern (e.g., "Wurl-File-Upload-Metadata_Version-7.0.*.csv")')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without uploading')
    
    args = parser.parse_args()
    
    print("🚀 Starting batch CSV upload...")
    print(f"📁 Folder: {args.folder_path}")
    
    # Find CSV files
    csv_files = find_csv_files(args.folder_path, args.pattern)
    
    if not csv_files:
        print("❌ No CSV files found!")
        return
    
    print(f"📋 Found {len(csv_files)} CSV files:")
    for file in csv_files:
        print(f"   - {os.path.basename(file)}")
    
    if args.dry_run:
        print("🔍 Dry run mode - no files will be uploaded")
        return
    
    # Connect to database
    conn = connect_to_neon()
    if not conn:
        return
    
    try:
        # Get ID maps
        genre_map, rating_map = get_id_maps(conn)
        
        total_processed = 0
        total_items = 0
        
        # Process each file
        for csv_file in csv_files:
            try:
                print(f"\n📄 Processing: {os.path.basename(csv_file)}")
                
                # Read CSV file
                df = pd.read_csv(csv_file)
                print(f"   📊 Read {len(df)} rows")
                
                # Upload content
                items_uploaded = insert_content(conn, df, genre_map, rating_map, os.path.basename(csv_file))
                total_items += items_uploaded
                total_processed += 1
                
            except Exception as e:
                print(f"❌ Error processing {csv_file}: {e}")
                continue
        
        print(f"\n🎉 Batch upload completed!")
        print(f"   📁 Files processed: {total_processed}/{len(csv_files)}")
        print(f"   📊 Total items uploaded: {total_items}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main() 