#!/usr/bin/env python3
"""
Script to load episodes for missing series from Wurl metadata files.
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

# Series to process with their expected episode counts
SERIES_TO_PROCESS = {
    'Bonanza': 82,
    'Ghost Squad': 13,
    'Commando Cody': 24,
    'Man with a Camera': 3,
    'Mike Hammer': 4,
    'Count of Monte Cristo': 78
}

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

def load_episodes_from_wurl_files(series_name):
    """Load episodes for a specific series from Wurl files."""
    episodes = []
    wurl_files = glob.glob('../*.xlsx') + glob.glob('../*.csv')
    
    for file_path in wurl_files:
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # Check for series name in different possible columns
            series_columns = ['Series Name', 'series_name', 'Series', 'Show', 'Title']
            series_col = None
            for col in series_columns:
                if col in df.columns:
                    series_col = col
                    break
            
            if series_col:
                # Check for exact and partial matches
                matches = df[df[series_col].str.contains(series_name, case=False, na=False)]
                if not matches.empty:
                    for _, row in matches.iterrows():
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
                            
        except Exception as e:
            # Skip files with errors
            continue
    
    return episodes

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
                
                print(f"    ✅ Inserted: S{episode['season_number']}E{episode['episode_number']} - {episode['title']}")
                inserted_count += 1
                
            except Exception as e:
                print(f"    ❌ Error inserting episode {episode['title']}: {e}")
                skipped_count += 1
        
        conn.commit()
        return inserted_count, skipped_count
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        conn.rollback()
        return 0, 0
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to load episodes for missing series."""
    print("🎬 Loading Episodes for Missing Series")
    print("=" * 50)
    
    total_inserted = 0
    total_skipped = 0
    
    for series_name, expected_count in SERIES_TO_PROCESS.items():
        print(f"\n📺 Processing {series_name} (expected: {expected_count} episodes)")
        
        # Get series info from database
        series_info = get_series_id(series_name)
        if not series_info:
            print(f"  ❌ Skipping {series_name} - series not found in database")
            continue
        
        print(f"  ✅ Found series: {series_name} (ID: {series_info['id']})")
        
        # Load episodes from Wurl files
        episodes = load_episodes_from_wurl_files(series_name)
        print(f"  📋 Found {len(episodes)} episodes in Wurl files")
        
        if episodes:
            # Insert episodes into database
            inserted, skipped = insert_episodes_to_database(episodes, series_info)
            total_inserted += inserted
            total_skipped += skipped
            
            print(f"  📊 {series_name}: {inserted} inserted, {skipped} skipped")
        else:
            print(f"  ⚠️  No episodes found for {series_name}")
    
    print(f"\n🎉 Final Summary:")
    print(f"  • Total episodes inserted: {total_inserted}")
    print(f"  • Total episodes skipped: {total_skipped}")
    
    # Show final episode counts
    print(f"\n📊 Final Episode Counts by Series:")
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    for series_name in SERIES_TO_PROCESS.keys():
        series_info = get_series_id(series_name)
        if series_info:
            cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_info['id'],))
            episode_count = cur.fetchone()[0]
            print(f"  • {series_name}: {episode_count} episodes")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main() 