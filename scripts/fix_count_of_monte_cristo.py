#!/usr/bin/env python3
"""
Script to fix Count of Monte Cristo naming issue and load additional episodes from Wurl files.
"""

import psycopg2
import pandas as pd
import glob
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

def get_count_of_monte_cristo_series():
    """Get the Count of Monte Cristo series from database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, uuid, title FROM content 
            WHERE type = 'SERIES' AND title = 'Count of Monte Cristo'
        """)
        
        series_record = cur.fetchone()
        return series_record
        
    except Exception as e:
        print(f"❌ Error getting series from database: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def update_series_name(series_id, new_title):
    """Update the series name in the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE content 
            SET title = %s, updated_at = %s
            WHERE id = %s
        """, (new_title, datetime.now(timezone.utc), series_id))
        
        conn.commit()
        print(f"✅ Updated series name to: {new_title}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating series name: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def load_count_of_monte_cristo_episodes_from_wurl():
    """Load Count of Monte Cristo episodes from Wurl metadata files."""
    print("🔍 Loading Count of Monte Cristo episodes from Wurl files...")
    
    # Find all Wurl metadata files with different patterns
    excel_files = glob.glob("Wurl*.xlsx") + glob.glob("Wurl - *.xlsx") + glob.glob("Wurl-File-Upload-Metadata*.xlsx")
    csv_files = glob.glob("Wurl*.csv") + glob.glob("Wurl - *.csv") + glob.glob("Wurl-File-Upload-Metadata*.csv")
    
    episodes = []
    
    for file in excel_files + csv_files:
        try:
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
                    continue
            
            # Check for series data
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                
                # Look for The Count of Monte Cristo
                monte_cristo_mask = df['Series Name'].str.contains('The Count of Monte Cristo', case=False, na=False)
                monte_cristo_rows = df[monte_cristo_mask]
                
                for _, row in monte_cristo_rows.iterrows():
                    episodes.append({
                        'title': row['Title'],
                        'description': row.get('Description', ''),
                        'season_number': int(row.get('Season Number', 1)),
                        'episode_number': int(row.get('Episode Number', 1)),
                        'runtime': int(row.get('Runtime', 60)),
                        'content_url': row.get('Video Filename', ''),  # Use Video Filename as content_url
                        'poster_url': row.get('Artwork Filename', ''),  # Use Artwork Filename as poster_url
                        'air_date': row.get('Air Date', None),
                        'genre': row.get('Genre', 'Drama'),
                        'rating': row.get('Rating', 'NR')
                    })
        
        except Exception as e:
            print(f"  ⚠️  Error reading {file}: {e}")
    
    print(f"📺 Found {len(episodes)} Count of Monte Cristo episodes in Wurl files")
    return episodes

def insert_episodes(series_id, series_uuid, episodes):
    """Insert episodes into the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        inserted = 0
        skipped = 0
        
        for ep in episodes:
            # Check if episode already exists by title and series_id
            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (ep['title'], series_id))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists, skipping: {ep['title']}")
                skipped += 1
                continue
            
            # Check if episode already exists by (series_id, season_number, episode_number)
            cur.execute("SELECT id FROM episodes WHERE series_id = %s AND season_number = %s AND episode_number = %s", 
                       (series_id, ep['season_number'], ep['episode_number']))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists by season/episode number, skipping: S{ep['season_number']}E{ep['episode_number']} - {ep['title']}")
                skipped += 1
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
        print(f"\n✅ Inserted {inserted} new episodes, skipped {skipped} existing episodes")
        return inserted, skipped
        
    except Exception as e:
        print(f"❌ Error inserting episodes: {e}")
        conn.rollback()
        return 0, 0
    finally:
        cur.close()
        conn.close()

def fix_count_of_monte_cristo():
    """Fix Count of Monte Cristo naming and load episodes."""
    print("🎬 Fixing Count of Monte Cristo Series")
    print("=" * 50)
    
    # Get the series from database
    series_record = get_count_of_monte_cristo_series()
    if not series_record:
        print("❌ Count of Monte Cristo series not found in database")
        return
    
    series_id, series_uuid, series_title = series_record
    print(f"✅ Found series: {series_title} (ID: {series_id})")
    
    # Update series name
    new_title = "The Count of Monte Cristo"
    if update_series_name(series_id, new_title):
        print(f"✅ Updated series name from '{series_title}' to '{new_title}'")
    else:
        print("❌ Failed to update series name")
        return
    
    # Load episodes from Wurl files
    episodes = load_count_of_monte_cristo_episodes_from_wurl()
    
    if episodes:
        # Insert episodes
        inserted, skipped = insert_episodes(series_id, series_uuid, episodes)
        
        print(f"\n📊 SUMMARY:")
        print(f"  Series name updated: {series_title} → {new_title}")
        print(f"  Episodes found in Wurl files: {len(episodes)}")
        print(f"  New episodes inserted: {inserted}")
        print(f"  Episodes skipped (already exist): {skipped}")
        
        # Get final count
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        final_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        print(f"  Total episodes in database: {final_count}")
    else:
        print("❌ No episodes found in Wurl files")

if __name__ == "__main__":
    fix_count_of_monte_cristo() 