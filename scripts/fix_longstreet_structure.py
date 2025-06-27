#!/usr/bin/env python3
"""
Script to fix Longstreet series structure:
1. Ensure exactly 1 main series row
2. Add all episodes from Wurl metadata
3. Fix episode numbering and structure
"""

import pandas as pd
import psycopg2
import uuid
from datetime import datetime, timezone
import os

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
        df = pd.read_excel(file_path)
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
    
    longstreet_entries = []
    
    # Get Longstreet episodes
    longstreet_df = df[df['Series Name'].str.contains('Longstreet', case=False, na=False)]
    
    for _, row in longstreet_df.iterrows():
        episode_data = {
            'title': row.get('Title', 'Unknown'),
            'description': row.get('Description', row.get('Short Description', '')),
            'series_name': 'Longstreet',
            'season_number': row.get('Season Number', 1),
            'episode_number': row.get('Episode Number', None),
            'runtime': 60,  # Default runtime
            'genre': row.get('Genre Value', 'Crime'),
            'rating': row.get('Rating Value', 'TV14'),
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

def fix_longstreet_structure():
    """Fix Longstreet series structure with proper episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing Longstreet Series Structure")
        print("=" * 60)
        
        # Step 1: Ensure exactly 1 main series record
        cur.execute("""
            SELECT id, uuid, title, description, runtime, genre_id, rating_id, poster_url, content_url
            FROM content 
            WHERE title = 'Longstreet' AND type = 'SERIES'
        """)
        series_records = cur.fetchall()
        
        if len(series_records) == 0:
            print("❌ No main Longstreet series record found")
            return
        elif len(series_records) > 1:
            print(f"⚠️  Found {len(series_records)} main series records, keeping the first one")
            # Keep the first one, delete the rest
            for i, record in enumerate(series_records[1:], 1):
                cur.execute("DELETE FROM content WHERE id = %s", (record[0],))
                print(f"   Deleted duplicate series record {i}")
        
        series_id, series_uuid, series_title, series_desc, series_runtime, series_genre_id, series_rating_id, series_poster_url, series_content_url = series_records[0]
        print(f"✅ Main series: {series_title} (ID: {series_id})")
        
        # Step 2: Read Wurl metadata files
        wurl_files = [
            "Wurl-File-Upload-Metadata_Version-7.0.40.xlsx",
            "Wurl-File-Upload-Metadata_Version-7.0.41.xlsx"
        ]
        
        all_episodes = []
        for file_name in wurl_files:
            file_path = os.path.join("..", file_name)
            if os.path.exists(file_path):
                print(f"\n📄 Processing: {file_name}")
                df = read_wurl_metadata(file_path)
                episodes = extract_longstreet_episodes(df)
                print(f"📺 Found {len(episodes)} Longstreet episodes")
                all_episodes.extend(episodes)
        
        if not all_episodes:
            print("❌ No Longstreet episodes found in metadata files")
            return
        
        # Remove duplicates (same episode number and title)
        unique_episodes = {}
        for episode in all_episodes:
            key = (episode['episode_number'], episode['title'])
            if key not in unique_episodes:
                unique_episodes[key] = episode
        
        episodes = list(unique_episodes.values())
        print(f"\n📊 Total unique Longstreet episodes to process: {len(episodes)}")
        
        # Step 3: Clear existing episodes (but keep the main series)
        cur.execute("""
            DELETE FROM content 
            WHERE series_name = 'Longstreet' AND title != 'Longstreet'
        """)
        deleted_count = cur.rowcount
        print(f"🗑️  Deleted {deleted_count} existing episode records")
        
        # Step 4: Add all episodes
        for i, episode_data in enumerate(episodes, 1):
            print(f"\n🎬 Processing Episode {i}: {episode_data['title']}")
            # Get or create genre and rating
            genre_id, rating_id = get_or_create_genre_rating(conn, episode_data['genre'], episode_data['rating'])
            # Create episode record
            cur.execute("""
                INSERT INTO content (
                    uuid, title, description, type, runtime, genre_id, rating_id,
                    series_name, episode_number, season_number, poster_url, trailer_url, content_url, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
                'https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png',  # Default poster
                '',  # trailer_url (empty string for now)
                '',  # content_url (empty string for now)
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            episode_id, episode_uuid = cur.fetchone()
            print(f"✅ Created episode: {episode_data['title']} (ID: {episode_id}, Episode {episode_data['episode_number']})")
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
                'https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png',
                episode_data['release_date'],
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            print(f"✅ Created episodes table entry for: {episode_data['title']}")
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Successfully processed {len(episodes)} Longstreet episodes!")
        
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
        
        # Verify structure
        cur.execute("""
            SELECT COUNT(*) as main_series,
                   (SELECT COUNT(*) FROM content WHERE series_name = 'Longstreet' AND title != 'Longstreet') as episodes
            FROM content 
            WHERE title = 'Longstreet' AND type = 'SERIES'
        """)
        
        result = cur.fetchone()
        main_series_count, episode_count = result
        print(f"\n📊 Structure Verification:")
        print(f"   Main Series Records: {main_series_count}")
        print(f"   Episode Records: {episode_count}")
        
        if main_series_count == 1 and episode_count > 0:
            print("✅ Longstreet structure is correct!")
        else:
            print("❌ Longstreet structure needs attention")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to fix Longstreet structure."""
    print("🎬 Longstreet Series Structure Fix")
    print("=" * 60)
    
    # Check for Wurl metadata files
    wurl_files = [
        "Wurl-File-Upload-Metadata_Version-7.0.40.xlsx",
        "Wurl-File-Upload-Metadata_Version-7.0.41.xlsx"
    ]
    
    found_files = []
    for file_name in wurl_files:
        file_path = os.path.join("..", file_name)
        if os.path.exists(file_path):
            found_files.append(file_path)
            print(f"✅ Found: {file_name}")
    
    if not found_files:
        print("❌ No Wurl metadata files found!")
        return
    
    # Confirm before proceeding
    print(f"\n📋 Found {len(found_files)} Wurl metadata file(s)")
    response = input("Do you want to proceed with fixing Longstreet structure? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        fix_longstreet_structure()
    else:
        print("❌ Update cancelled")

if __name__ == "__main__":
    main() 