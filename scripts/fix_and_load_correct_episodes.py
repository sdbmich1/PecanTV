#!/usr/bin/env python3
"""
Script to fix episode mix-ups and load correct episodes from the Wurl file with proper URLs.
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

def load_wurl_data():
    """Load data from the new Wurl metadata file."""
    file_path = "Wurl-File-Upload-Metadata_Version-7.0.4.1.xlsx"
    df = pd.read_excel(file_path)
    return df

def fix_series_episodes(conn, cur, series_name, series_id, series_uuid, df):
    """Fix episodes for a specific series by clearing existing ones and loading from Wurl."""
    print(f"🔧 Fixing episodes for '{series_name}'...")
    
    # Clear existing episodes
    cur.execute("DELETE FROM episodes WHERE series_id = %s", (series_id,))
    print(f"  🗑️  Cleared existing episodes")
    
    # Filter data for this series
    series_data = df[df['Series Name'] == series_name]
    
    if series_data.empty:
        print(f"  ❌ No data found for series '{series_name}' in Wurl file")
        return 0
    
    inserted = 0
    for _, row in series_data.iterrows():
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
        
        print(f"  ✅ Inserted: {row['Title']}")
        print(f"     Video: {row.get('Video Filename', 'N/A')}")
        print(f"     Artwork: {row.get('Artwork Filename', 'N/A')}")
        inserted += 1
    
    print(f"  📊 Total episodes inserted: {inserted}")
    return inserted

def main():
    print("🔧 Fixing and loading correct episodes from Wurl file")
    print("=" * 60)
    
    # Load Wurl data
    df = load_wurl_data()
    print(f"✅ Loaded Wurl file with {len(df)} rows")
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        total_episodes = 0
        
        # Process each series
        series_to_process = [
            ('The Lone Ranger', 691),
            ('The Green Hornet', 692),
            ('Commando Cody - Sky Marshal of the Universe', 699)
        ]
        
        for series_name, series_id in series_to_process:
            print(f"\n{'='*50}")
            print(f"Processing: {series_name} (ID: {series_id})")
            print(f"{'='*50}")
            
            # Get series UUID
            cur.execute("SELECT uuid FROM content WHERE id = %s", (series_id,))
            result = cur.fetchone()
            if not result:
                print(f"  ❌ Series not found")
                continue
            
            series_uuid = result[0]
            
            # Fix episodes
            episodes_count = fix_series_episodes(conn, cur, series_name, series_id, series_uuid, df)
            total_episodes += episodes_count
        
        # Create Zorro's Black Whip series and load episodes
        print(f"\n{'='*50}")
        print(f"Creating: Zorro's Black Whip")
        print(f"{'='*50}")
        
        # Check if Zorro's Black Whip already exists
        cur.execute("SELECT id, uuid FROM content WHERE title = %s", ("Zorro's Black Whip",))
        result = cur.fetchone()
        
        if result:
            series_id, series_uuid = result
            print(f"  ✅ Found existing series (ID: {series_id})")
        else:
            # Create new series
            cur.execute("""
                INSERT INTO content (
                    uuid, title, description, type, runtime, 
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id, uuid
            """, (
                str(uuid.uuid4()),
                "Zorro's Black Whip",
                "Episodes from Zorro's Black Whip",
                'SERIES',
                60,
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            series_id, series_uuid = cur.fetchone()
            print(f"  ✅ Created new series (ID: {series_id})")
        
        # Load Zorro's Black Whip episodes
        episodes_count = fix_series_episodes(conn, cur, "Zorro's Black Whip", series_id, series_uuid, df)
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