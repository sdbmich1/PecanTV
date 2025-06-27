#!/usr/bin/env python3
"""
Script to load Bonanza episodes from Wurl metadata files using correct field names.
"""

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

# Bonanza files to process
BONANZA_FILES = [
    'Wurl - File Upload Metadata_Version 7.0.28.xlsx',
    'Wurl - File Upload Metadata_Version 7.0.28.csv',
    'Wurl - File Upload Metadata_Version 7.0.29.csv',
    'Wurl - File Upload Metadata_Version 7.0.30.csv'
]

def load_bonanza_episodes_from_wurl():
    """Load Bonanza episodes from Wurl metadata files using correct field names."""
    print("🎬 Loading Bonanza Episodes from Wurl Metadata Files")
    print("=" * 60)
    
    all_episodes = []
    
    for file in BONANZA_FILES:
        try:
            print(f"\n📖 Reading {file}...")
            
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                # Try different encodings for CSV
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"  ❌ Could not read {file} with any encoding")
                    continue
            
            print(f"  📊 Loaded {len(df)} rows from {file}")
            
            # Filter for Bonanza episodes
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                bonanza_df = df[df['Series Name'].str.strip().str.lower() == 'bonanza']
                
                print(f"  🎬 Found {len(bonanza_df)} Bonanza episodes in {file}")
                
                for _, row in bonanza_df.iterrows():
                    title = str(row.get('Title', '')).strip()
                    video_filename = str(row.get('Video Filename', '')).strip()
                    artwork_filename = str(row.get('Artwork Filename', '')).strip()
                    
                    # Handle season and episode numbers
                    try:
                        season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                    except (ValueError, TypeError):
                        season = 1
                    
                    try:
                        episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                    except (ValueError, TypeError):
                        episode = 1
                    
                    # Construct content URL from video filename
                    content_url = ""
                    if video_filename and video_filename != 'nan':
                        content_url = f"https://storage.googleapis.com/pecantv_features/{video_filename}"
                    
                    # Construct poster URL from artwork filename
                    poster_url = ""
                    if artwork_filename and artwork_filename != 'nan':
                        poster_url = f"https://storage.googleapis.com/pecantv_features/{artwork_filename}"
                    
                    episode_data = {
                        'title': title,
                        'description': str(row.get('Description', '')).strip(),
                        'season_number': season,
                        'episode_number': episode,
                        'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60,
                        'content_url': content_url,
                        'poster_url': poster_url,
                        'air_date': row.get('Air Date', None),
                        'genre': str(row.get('Genre Value', 'Drama')).strip(),
                        'rating': str(row.get('Rating Value', 'NR')).strip(),
                        'source_file': file
                    }
                    
                    if title and video_filename and video_filename != 'nan':
                        all_episodes.append(episode_data)
                        print(f"    ✅ Found: S{season:02d}E{episode:02d} - {title}")
                        print(f"       Video: {video_filename}")
                        if artwork_filename and artwork_filename != 'nan':
                            print(f"       Artwork: {artwork_filename}")
        
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    # Remove duplicates based on season/episode number
    unique_episodes = {}
    for episode in all_episodes:
        key = (episode['season_number'], episode['episode_number'])
        if key not in unique_episodes:
            unique_episodes[key] = episode
    
    print(f"\n📊 Found {len(unique_episodes)} unique Bonanza episodes from metadata files")
    return list(unique_episodes.values())

def get_bonanza_series_id():
    """Get the Bonanza series ID from the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, uuid FROM content 
            WHERE type = 'SERIES' AND title = 'Bonanza'
        """)
        
        result = cur.fetchone()
        if result:
            return {'id': result[0], 'uuid': str(result[1])}
        else:
            print("❌ Bonanza series not found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error getting Bonanza series ID: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def update_bonanza_episodes(episodes):
    """Update or insert Bonanza episodes in the database."""
    if not episodes:
        print("❌ No episodes to process")
        return
    
    series_info = get_bonanza_series_id()
    if not series_info:
        return
    
    print(f"✅ Found Bonanza series (ID: {series_info['id']})")
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        updated_count = 0
        inserted_count = 0
        skipped_count = 0
        
        for episode in episodes:
            # Check if episode already exists by season/episode number
            cur.execute("""
                SELECT id, content_url, poster_url FROM episodes 
                WHERE series_id = %s AND season_number = %s AND episode_number = %s
            """, (series_info['id'], episode['season_number'], episode['episode_number']))
            
            existing = cur.fetchone()
            
            if existing:
                ep_id, current_content_url, current_poster_url = existing
                
                # Update existing episode if content_url is missing
                if not current_content_url or not current_content_url.strip():
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, poster_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (episode['content_url'], episode['poster_url'], datetime.now(timezone.utc), ep_id))
                    
                    print(f"  ✅ Updated: S{episode['season_number']:02d}E{episode['episode_number']:02d} - {episode['title']}")
                    print(f"     Content URL: {episode['content_url']}")
                    if episode['poster_url']:
                        print(f"     Poster URL: {episode['poster_url']}")
                    updated_count += 1
                else:
                    print(f"  ⚠️  Skipped (already has content URL): S{episode['season_number']:02d}E{episode['episode_number']:02d} - {episode['title']}")
                    skipped_count += 1
            else:
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
                    series_info['id'],
                    series_info['uuid'],
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                print(f"  ✅ Inserted: S{episode['season_number']:02d}E{episode['episode_number']:02d} - {episode['title']}")
                print(f"     Content URL: {episode['content_url']}")
                if episode['poster_url']:
                    print(f"     Poster URL: {episode['poster_url']}")
                inserted_count += 1
        
        conn.commit()
        print(f"\n📊 Summary:")
        print(f"  Updated: {updated_count} episodes")
        print(f"  Inserted: {inserted_count} episodes")
        print(f"  Skipped: {skipped_count} episodes")
        print(f"  Total processed: {updated_count + inserted_count + skipped_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to load Bonanza episodes."""
    # Load episodes from Wurl metadata files
    episodes = load_bonanza_episodes_from_wurl()
    
    if episodes:
        # Update database with episodes
        update_bonanza_episodes(episodes)
        
        # Verify final status
        print("\n🔍 Verifying final status...")
        verify_script = "python scripts/verify_bonanza_content_urls.py"
        import subprocess
        subprocess.run(verify_script, shell=True)
    else:
        print("❌ No Bonanza episodes found in metadata files")

if __name__ == "__main__":
    main() 