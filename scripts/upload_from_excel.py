#!/usr/bin/env python3
"""
Excel/CSV Data Upload Script for PecanTV
Uploads film and episode data from Excel or CSV files on Dropbox to Neon database.
Based on the previous Google Sheets episode script logic.
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys
from datetime import datetime
import argparse
from pathlib import Path

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
            # CSV file
            df = pd.read_csv(file_path)
            if sheet_name:
                print("⚠️  Warning: Sheet name specified but reading CSV file. Ignoring sheet parameter.")
        else:
            print(f"❌ Unsupported file format: {file_ext}")
            print("Supported formats: .xlsx, .xls, .csv")
            return None
        
        print(f"✅ Read {len(df)} rows from {file_path}")
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

def clean_text(text):
    """Clean and normalize text data."""
    if pd.isna(text):
        return None
    return str(text).strip()

def insert_content(conn, content_df, genre_map, rating_map):
    """Insert content into the database using the same logic as Google Sheets script."""
    print(f"📝 Processing {len(content_df)} content items...")
    
    # Expected columns mapping (based on Google Sheets structure and Wurl Excel format)
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
    
    # Prepare data for insertion (same logic as Google Sheets script)
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
                # If it's just a filename, construct the full URL
                poster_url = f"https://storage.googleapis.com/pecantv_title_images/{poster_url}"
            
            if content_url and not content_url.startswith('http'):
                # If it's just a filename, construct the full URL
                content_url = f"https://storage.googleapis.com/pecantv_features/{content_url}"
            
            if trailer_url and not trailer_url.startswith('http'):
                # If it's just a filename, construct the full URL
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
            
            # Handle runtime (same as Google Sheets)
            runtime = row.get(actual_columns.get('runtime', 'runtime'), 0)
            try:
                runtime = int(runtime) if pd.notna(runtime) else 0
            except:
                runtime = 0
            
            # Handle genre (same as Google Sheets)
            genre_name = clean_text(row.get(actual_columns.get('genre', 'genre'), ''))
            genre_id = None
            if genre_name:
                genre_id = genre_map.get(genre_name.lower())
            
            # Handle rating (same as Google Sheets)
            rating_code = clean_text(row.get(actual_columns.get('rating', 'rating'), ''))
            rating_id = None
            if rating_code:
                rating_id = rating_map.get(rating_code.lower())
            
            # Handle release date (same as Google Sheets)
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
            print(f"⚠️  Error processing row: {e}")
            continue
    
    if not data_to_insert:
        print("❌ No valid data to insert")
        return
    
    # Insert data (same SQL as Google Sheets script)
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
    print(f"✅ Inserted {len(data_to_insert)} content items")

def insert_episodes(conn, episodes_df):
    """Insert episodes into the database using the same logic as Google Sheets script."""
    print(f"📝 Processing {len(episodes_df)} episodes...")
    
    # Expected columns mapping for episodes (based on Google Sheets structure)
    column_mapping = {
        'series_title': ['series_title', 'show_title', 'series', 'Series Title', 'series_name'],
        'episode_number': ['episode_number', 'episode', 'number', 'Episode Number', 'episode_num'],
        'season_number': ['season_number', 'season', 'Season Number', 'season_num'],
        'title': ['title', 'episode_title', 'name', 'Title', 'episode_name'],
        'description': ['description', 'desc', 'plot', 'Description'],
        'runtime': ['runtime', 'duration', 'length', 'Runtime'],
        'content_url': ['content_url', 'video_url', 'stream_url', 'Content URL'],
        'thumbnail_url': ['thumbnail_url', 'thumbnail', 'image_url', 'Thumbnail URL']
    }
    
    # Find actual columns
    actual_columns = {}
    for expected_col, possible_names in column_mapping.items():
        for possible_name in possible_names:
            if possible_name in episodes_df.columns:
                actual_columns[expected_col] = possible_name
                break
    
    print(f"🔍 Found episode columns: {actual_columns}")
    
    # Get content map for series lookup (same as Google Sheets script)
    with conn.cursor() as cur:
        cur.execute("SELECT id, title FROM content WHERE type = 'SERIES'")
        content_map = {row[1].lower(): row[0] for row in cur.fetchall()}
    
    print(f"📺 Found {len(content_map)} series in database")
    
    # Prepare data for insertion (same logic as Google Sheets script)
    data_to_insert = []
    for _, row in episodes_df.iterrows():
        try:
            series_title = clean_text(row.get(actual_columns.get('series_title', 'series_title'), ''))
            episode_title = clean_text(row.get(actual_columns.get('title', 'title'), ''))
            
            if not series_title or not episode_title:
                continue
            
            # Find the series content_id (same as Google Sheets script)
            series_id = content_map.get(series_title.lower())
            if not series_id:
                print(f"⚠️  Series '{series_title}' not found in content table")
                continue
            
            # Handle episode number (same as Google Sheets script)
            episode_number = row.get(actual_columns.get('episode_number', 'episode_number'), 1)
            try:
                episode_number = int(episode_number) if pd.notna(episode_number) else 1
            except:
                episode_number = 1
            
            # Handle season number (same as Google Sheets script)
            season_number = row.get(actual_columns.get('season_number', 'season_number'), 1)
            try:
                season_number = int(season_number) if pd.notna(season_number) else 1
            except:
                season_number = 1
            
            description = clean_text(row.get(actual_columns.get('description', 'description'), ''))
            
            # Handle runtime (same as Google Sheets script)
            runtime = row.get(actual_columns.get('runtime', 'runtime'), 0)
            try:
                runtime = int(runtime) if pd.notna(runtime) else 0
            except:
                runtime = 0
            
            content_url = clean_text(row.get(actual_columns.get('content_url', 'content_url'), ''))
            thumbnail_url = clean_text(row.get(actual_columns.get('thumbnail_url', 'thumbnail_url'), ''))
            
            data_to_insert.append((
                series_id, season_number, episode_number, episode_title,
                description, content_url, thumbnail_url, runtime
            ))
            
        except Exception as e:
            print(f"⚠️  Error processing episode row: {e}")
            continue
    
    if not data_to_insert:
        print("❌ No valid episode data to insert")
        return
    
    # Insert episodes (same SQL as Google Sheets script)
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO episodes (
                series_id, season_number, episode_number, title,
                description, content_url, thumbnail_url, runtime
            )
            VALUES %s
            ON CONFLICT (series_id, season_number, episode_number) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                content_url = EXCLUDED.content_url,
                thumbnail_url = EXCLUDED.thumbnail_url,
                runtime = EXCLUDED.runtime
            """,
            data_to_insert
        )
    conn.commit()
    print(f"✅ Inserted {len(data_to_insert)} episodes")

def main():
    parser = argparse.ArgumentParser(description='Upload data from Excel files to Neon database')
    parser.add_argument('file_path', help='Path to Excel file')
    parser.add_argument('--sheet', help='Sheet name (optional, will read all sheets if not specified)')
    parser.add_argument('--type', choices=['content', 'episodes'], required=True, 
                       help='Type of data to upload')
    
    args = parser.parse_args()
    
    print("🚀 Starting Excel data upload...")
    print(f"📁 File: {args.file_path}")
    print(f"📊 Type: {args.type}")
    
    # Connect to database
    conn = connect_to_neon()
    if not conn:
        return
    
    try:
        # Read Excel file
        if args.sheet:
            df = read_data_file(args.file_path, args.sheet)
            if df is None:
                return
        else:
            sheets = read_data_file(args.file_path)
            if sheets is None:
                return
            
            # If multiple sheets, ask user which one to use
            if len(sheets) > 1:
                print("\n📋 Available sheets:")
                for i, sheet_name in enumerate(sheets.keys(), 1):
                    print(f"  {i}. {sheet_name} ({len(sheets[sheet_name])} rows)")
                
                try:
                    choice = int(input("\nSelect sheet number: ")) - 1
                    sheet_names = list(sheets.keys())
                    if 0 <= choice < len(sheet_names):
                        df = sheets[sheet_names[choice]]
                        print(f"✅ Selected sheet: {sheet_names[choice]}")
                    else:
                        print("❌ Invalid selection")
                        return
                except ValueError:
                    print("❌ Invalid input")
                    return
            else:
                df = list(sheets.values())[0]
        
        # Get ID maps for content uploads
        if args.type == 'content':
            genre_map, rating_map = get_id_maps(conn)
            insert_content(conn, df, genre_map, rating_map)
        elif args.type == 'episodes':
            insert_episodes(conn, df)
        
        print("🎉 Upload completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main() 