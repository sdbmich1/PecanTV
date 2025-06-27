#!/usr/bin/env python3
"""
Script to load Commando Cody, Lone Ranger, Green Hornet, and Zorro's Black Whip episodes 
from the new Wurl metadata file and clean up the content table.
"""

import psycopg2
import pandas as pd
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

# Series to process from the new Wurl file
SERIES_TO_PROCESS = [
    'The Lone Ranger',
    'The Green Hornet',
    "Zorro's Black Whip"
]

def load_wurl_data():
    """Load data from the new Wurl metadata file."""
    file_path = "Wurl-File-Upload-Metadata_Version-7.0.4.1.xlsx"
    df = pd.read_excel(file_path)
    return df

def update_series_name_and_cleanup(conn, cur, old_name, new_name):
    """Update series name and clean up duplicate rows in content table."""
    print(f"🔄 Updating series name: '{old_name}' → '{new_name}'")
    
    # Get the main series record
    cur.execute("""
        SELECT id, uuid FROM content 
        WHERE type = 'SERIES' AND title = %s
        ORDER BY id LIMIT 1
    """, (old_name,))
    series_record = cur.fetchone()
    
    if not series_record:
        print(f"  ❌ Series '{old_name}' not found in database")
        return None
    
    series_id, series_uuid = series_record
    
    # Update the series name
    cur.execute("""
        UPDATE content SET title = %s WHERE id = %s
    """, (new_name, series_id))
    
    # Delete duplicate series rows (keep only the first one)
    cur.execute("""
        DELETE FROM content 
        WHERE type = 'SERIES' AND title = %s AND id != %s
    """, (new_name, series_id))
    
    # Delete episode rows from content table (they should be in episodes table)
    cur.execute("""
        DELETE FROM content 
        WHERE type = 'EPISODE' AND series_name = %s
    """, (new_name,))
    
    print(f"  ✅ Updated series name and cleaned up duplicates")
    return series_id, series_uuid

def load_episodes_for_series(conn, cur, df, series_name, series_id, series_uuid):
    """Load episodes for a specific series from the Wurl data."""
    print(f"📺 Loading episodes for '{series_name}'...")
    
    # Filter data for this series
    series_data = df[df['Series Name'] == series_name]
    
    if series_data.empty:
        print(f"  ❌ No data found for series '{series_name}' in Wurl file")
        return 0
    
    inserted = 0
    for _, row in series_data.iterrows():
        # Check if episode already exists
        cur.execute("""
            SELECT id FROM episodes 
            WHERE series_id = %s AND title = %s
        """, (series_id, row['Title']))
        
        if cur.fetchone():
            print(f"  ⚠️  Episode already exists: {row['Title']}")
            continue
        
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
            row['Title'],
            row.get('Description', ''),
            int(row.get('Season Number', 1)),
            int(row.get('Episode Number', 1)),
            int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60,
            row.get('Video Filename', ''),  # Use Video Filename as content_url
            row.get('Artwork Filename', ''),  # Use Artwork Filename as poster_url
            row.get('Release Date', None),
            series_id,
            str(series_uuid),
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        print(f"  ✅ Inserted: {row['Title']} (Video: {row.get('Video Filename', 'N/A')})")
        inserted += 1
    
    print(f"  📊 Total episodes inserted: {inserted}")
    return inserted

def main():
    print("🎬 Loading Lone Ranger, Green Hornet, and Zorro's Black Whip from new Wurl file")
    print("=" * 80)
    
    # Load Wurl data
    df = load_wurl_data()
    print(f"✅ Loaded Wurl file with {len(df)} rows")
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        total_episodes = 0
        
        for series_name in SERIES_TO_PROCESS:
            print(f"\n{'='*60}")
            print(f"Processing: {series_name}")
            print(f"{'='*60}")
            
            # Handle different naming variations in database
            old_names = []
            if series_name == 'The Lone Ranger':
                old_names = ['Lone Ranger']
            elif series_name == 'The Green Hornet':
                old_names = ['Green Hornet']
            elif series_name == "Zorro's Black Whip":
                # This series doesn't exist in database, we'll create it
                old_names = []
            
            series_id = None
            series_uuid = None
            
            # Try to find and update the series
            for old_name in old_names:
                result = update_series_name_and_cleanup(conn, cur, old_name, series_name)
                if result:
                    series_id, series_uuid = result
                    break
            
            # If series not found and it's Zorro's Black Whip, create it
            if not series_id and series_name == "Zorro's Black Whip":
                print(f"🆕 Creating new series: {series_name}")
                cur.execute("""
                    INSERT INTO content (
                        uuid, title, description, type, runtime, 
                        created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id, uuid
                """, (
                    str(uuid.uuid4()),
                    series_name,
                    f"Episodes from {series_name}",
                    'SERIES',
                    60,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                series_id, series_uuid = cur.fetchone()
                print(f"  ✅ Created series with ID: {series_id}")
            
            if not series_id:
                print(f"  ❌ Could not find or create series '{series_name}'")
                continue
            
            # Load episodes
            episodes_count = load_episodes_for_series(conn, cur, df, series_name, series_id, series_uuid)
            total_episodes += episodes_count
        
        conn.commit()
        print(f"\n🎉 Successfully processed all series!")
        print(f"📊 Total episodes loaded: {total_episodes}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main() 