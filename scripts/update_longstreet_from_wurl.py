#!/usr/bin/env python3
"""
Script to update Longstreet series episodes from Wurl File Upload Metadata files.
This script will:
1. Read Wurl metadata files (versions 7.0.40 and 7.0.41)
2. Extract Longstreet episodes from the 'Longstreet' folder
3. Update the database with new episode information
4. Create episodes table entries
"""

import pandas as pd
import psycopg2
import uuid
from datetime import datetime, timezone
import os
import sys

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def read_wurl_metadata(file_path):
    """Read Wurl metadata file and return DataFrame."""
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        print(f"✅ Successfully read {file_path}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Total rows: {len(df)}")
        return df
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def extract_longstreet_episodes(df):
    """Extract Longstreet episodes from the metadata DataFrame."""
    if df is None:
        return []
    
    # Look for Longstreet content - check multiple possible column names
    longstreet_entries = []
    
    # Check different possible column names for series/folder information
    series_columns = ['Series Name', 'SeriesName', 'Folder', 'Category', 'Keywords']
    title_columns = ['Title', 'Internal Title', 'InternalTitle']
    
    for _, row in df.iterrows():
        is_longstreet = False
        
        # Check if it's in the Longstreet series/folder
        for col in series_columns:
            if col in df.columns and pd.notna(row[col]):
                if 'longstreet' in str(row[col]).lower():
                    is_longstreet = True
                    break
        
        # Check if title contains Longstreet
        for col in title_columns:
            if col in df.columns and pd.notna(row[col]):
                if 'longstreet' in str(row[col]).lower():
                    is_longstreet = True
                    break
        
        if is_longstreet:
            episode_data = {
                'title': row.get('Title', row.get('Internal Title', 'Unknown')),
                'description': row.get('Description', row.get('Short Description', '')),
                'series_name': row.get('Series Name', 'Longstreet'),
                'season_number': row.get('Season Number', 1),
                'episode_number': row.get('Episode Number', None),
                'runtime': row.get('Runtime', 60),
                'genre': row.get('Genre Value', 'Drama'),
                'rating': row.get('Rating Value', 'TV-PG'),
                'video_filename': row.get('Video Filename', ''),
                'artwork_filename': row.get('Artwork Filename', ''),
                'release_date': row.get('Release Date', None),
                'external_id': row.get('External ID', ''),
                'entry_type': row.get('Entry Type', 'Episode')
            }
            longstreet_entries.append(episode_data)
    
    return longstreet_entries

def get_or_create_genre_rating(conn, genre_name, rating_code):
    """Get or create genre and rating records."""
    with conn.cursor() as cur:
        # Get or create genre
        cur.execute("SELECT id FROM genres WHERE name = %s", (genre_name,))
        genre_result = cur.fetchone()
        if genre_result:
            genre_id = genre_result[0]
        else:
            cur.execute("INSERT INTO genres (name, description) VALUES (%s, %s) RETURNING id", 
                       (genre_name, f"Genre for {genre_name}"))
            genre_id = cur.fetchone()[0]
            print(f"✅ Created new genre: {genre_name} (ID: {genre_id})")
        
        # Get or create rating
        cur.execute("SELECT id FROM ratings WHERE code = %s", (rating_code,))
        rating_result = cur.fetchone()
        if rating_result:
            rating_id = rating_result[0]
        else:
            cur.execute("INSERT INTO ratings (code, description) VALUES (%s, %s) RETURNING id", 
                       (rating_code, f"Rating: {rating_code}"))
            rating_id = cur.fetchone()[0]
            print(f"✅ Created new rating: {rating_code} (ID: {rating_id})")
        
        return genre_id, rating_id

def update_longstreet_episodes_from_wurl(wurl_files):
    """Update Longstreet episodes from Wurl metadata files."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Updating Longstreet Series from Wurl Metadata")
        print("=" * 60)
        
        # Get the main series record
        cur.execute("""
            SELECT id, uuid, title, description, runtime, genre_id, rating_id, poster_url, content_url
            FROM content 
            WHERE series_name = 'Longstreet' AND type = 'SERIES' AND title = 'Longstreet'
        """)
        series_record = cur.fetchone()
        
        if not series_record:
            print("❌ Main Longstreet series record not found")
            return
            
        series_id, series_uuid, series_title, series_desc, series_runtime, series_genre_id, series_rating_id, series_poster_url, series_content_url = series_record
        print(f"✅ Found main series: {series_title} (ID: {series_id})")
        
        all_episodes = []
        
        # Process each Wurl metadata file
        for file_path in wurl_files:
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue
                
            print(f"\n📄 Processing: {file_path}")
            df = read_wurl_metadata(file_path)
            episodes = extract_longstreet_episodes(df)
            
            print(f"📺 Found {len(episodes)} Longstreet episodes in {file_path}")
            all_episodes.extend(episodes)
        
        if not all_episodes:
            print("❌ No Longstreet episodes found in metadata files")
            return
        
        print(f"\n📊 Total Longstreet episodes to process: {len(all_episodes)}")
        
        # Process each episode
        for i, episode_data in enumerate(all_episodes, 1):
            print(f"\n🎬 Processing Episode {i}: {episode_data['title']}")
            
            # Get or create genre and rating
            genre_id, rating_id = get_or_create_genre_rating(conn, episode_data['genre'], episode_data['rating'])
            
            # Check if episode already exists
            cur.execute("""
                SELECT id FROM content 
                WHERE title = %s AND series_name = 'Longstreet'
            """, (episode_data['title'],))
            
            existing_episode = cur.fetchone()
            
            if existing_episode:
                # Update existing episode
                cur.execute("""
                    UPDATE content 
                    SET description = %s, episode_number = %s, season_number = %s,
                        genre_id = %s, rating_id = %s, runtime = %s,
                        updated_at = %s
                    WHERE id = %s
                """, (
                    episode_data['description'],
                    episode_data['episode_number'],
                    episode_data['season_number'],
                    genre_id,
                    rating_id,
                    episode_data['runtime'],
                    datetime.now(timezone.utc),
                    existing_episode[0]
                ))
                print(f"✅ Updated existing episode: {episode_data['title']}")
            else:
                # Create new episode
                cur.execute("""
                    INSERT INTO content (
                        uuid, title, description, type, runtime, genre_id, rating_id,
                        series_name, episode_number, season_number, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id, uuid
                """, (
                    str(uuid.uuid4()),
                    episode_data['title'],
                    episode_data['description'],
                    'SERIES',  # Type for episodes
                    episode_data['runtime'],
                    genre_id,
                    rating_id,
                    'Longstreet',
                    episode_data['episode_number'],
                    episode_data['season_number'],
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                episode_id, episode_uuid = cur.fetchone()
                print(f"✅ Created new episode: {episode_data['title']} (ID: {episode_id})")
                
                # Create episodes table entry
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
                    episode_data['title'],
                    episode_data['description'],
                    episode_data['season_number'],
                    episode_data['episode_number'],
                    episode_data['runtime'],
                    '',  # content_url (to be updated later)
                    '',  # poster_url (to be updated later)
                    episode_data['release_date'],
                    series_id,
                    str(series_uuid),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                print(f"✅ Created episodes table entry for: {episode_data['title']}")
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Successfully processed {len(all_episodes)} Longstreet episodes!")
        
        # Show summary
        cur.execute("""
            SELECT title, episode_number, season_number 
            FROM content 
            WHERE series_name = 'Longstreet' AND title != 'Longstreet'
            ORDER BY episode_number
        """)
        
        episodes = cur.fetchall()
        print(f"\n📺 Current Longstreet Episodes ({len(episodes)} total):")
        for title, episode_num, season_num in episodes:
            print(f"   Episode {episode_num}: {title}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to update Longstreet episodes."""
    print("🎬 Longstreet Episode Update from Wurl Metadata")
    print("=" * 60)
    
    # Check for Wurl metadata files
    wurl_files = []
    
    # Look for version 7.0.40 and 7.0.41 files
    possible_files = [
        "Wurl-File-Upload-Metadata_Version-7.0.40.xlsx",
        "Wurl-File-Upload-Metadata_Version-7.0.40.csv",
        "Wurl-File-Upload-Metadata_Version-7.0.41.xlsx",
        "Wurl-File-Upload-Metadata_Version-7.0.41.csv"
    ]
    
    for file_name in possible_files:
        file_path = os.path.join("..", file_name)
        if os.path.exists(file_path):
            wurl_files.append(file_path)
            print(f"✅ Found: {file_name}")
    
    if not wurl_files:
        print("❌ No Wurl metadata files found!")
        print("Please download the following files from Dropbox and place them in the project root:")
        print("   - Wurl-File-Upload-Metadata_Version-7.0.40.xlsx/csv")
        print("   - Wurl-File-Upload-Metadata_Version-7.0.41.xlsx/csv")
        return
    
    # Confirm before proceeding
    print(f"\n📋 Found {len(wurl_files)} Wurl metadata file(s)")
    response = input("Do you want to proceed with updating Longstreet episodes? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        update_longstreet_episodes_from_wurl(wurl_files)
    else:
        print("❌ Update cancelled")

if __name__ == "__main__":
    main() 