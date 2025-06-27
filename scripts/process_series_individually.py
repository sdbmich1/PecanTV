#!/usr/bin/env python3
"""
Script to process each series individually to avoid transaction conflicts.
"""

import psycopg2
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

# Priority series to process
PRIORITY_SERIES = [
    'Lone Ranger',
    'Man with a Camera', 
    'Ghost Squad',
    'Bonanza',
    'Count of Monte Cristo'
]

def process_single_series(series_name):
    """Process a single series with its own database connection."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print(f"\n🎬 Processing: {series_name}")
        print("-" * 50)
        
        # Get the main series record
        cur.execute("""
            SELECT id, uuid FROM content 
            WHERE type = 'SERIES' AND title = %s
        """, (series_name,))
        series_record = cur.fetchone()
        
        if not series_record:
            print(f"❌ Main series record not found for {series_name}")
            return 0, 0
        
        series_id, series_uuid = series_record
        print(f"✅ Found main series: {series_name} (ID: {series_id})")
        
        # Get episode records
        cur.execute("""
            SELECT id, uuid, title, description, runtime, content_url, poster_url, 
                   episode_number, season_number, genre_id, rating_id
            FROM content 
            WHERE series_name = %s AND title != %s AND type = 'SERIES'
            ORDER BY season_number, episode_number, title
        """, (series_name, series_name))
        
        episode_records = cur.fetchall()
        print(f"📺 Found {len(episode_records)} episode records")
        
        if not episode_records:
            print(f"  ℹ️  No episode records to process")
            return 0, 0
        
        moved_count = 0
        skipped_count = 0
        
        for episode in episode_records:
            episode_id, episode_uuid, title, description, runtime, content_url, poster_url, episode_number, season_number, genre_id, rating_id = episode
            
            # Check if episode already exists in episodes table by title
            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (title, series_id))
            if cur.fetchone():
                print(f"  ⚠️  Episode already exists by title, skipping: {title}")
                skipped_count += 1
                continue
            
            # Check if episode already exists by season/episode number
            if episode_number and season_number:
                cur.execute("SELECT id FROM episodes WHERE series_id = %s AND season_number = %s AND episode_number = %s", 
                           (series_id, season_number, episode_number))
                if cur.fetchone():
                    print(f"  ⚠️  Episode already exists by season/episode number, skipping: S{season_number}E{episode_number} - {title}")
                    skipped_count += 1
                    continue
            
            # Try to insert with unique constraint handling
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
                    title,
                    description or '',
                    season_number or 1,
                    episode_number or 1,
                    runtime or 60,
                    content_url or '',
                    poster_url or '',
                    None,  # air_date
                    series_id,
                    str(series_uuid),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                print(f"  ✅ Moved episode: {title}")
                moved_count += 1
                
            except psycopg2.IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    print(f"  ⚠️  Duplicate constraint violation, skipping: {title}")
                    skipped_count += 1
                else:
                    print(f"  ❌ Integrity error for {title}: {e}")
                    skipped_count += 1
            except Exception as e:
                print(f"  ❌ Error inserting {title}: {e}")
                skipped_count += 1
        
        # Commit changes for this series
        conn.commit()
        
        print(f"\n📊 Summary for {series_name}:")
        print(f"  Episodes moved: {moved_count}")
        print(f"  Episodes skipped: {skipped_count}")
        
        return moved_count, skipped_count
        
    except Exception as e:
        print(f"❌ Error processing {series_name}: {e}")
        conn.rollback()
        return 0, 0
    finally:
        cur.close()
        conn.close()

def get_all_series_with_episodes():
    """Get all series that have episode records."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT DISTINCT series_name 
            FROM content 
            WHERE series_name IS NOT NULL 
            AND series_name != '' 
            AND EXISTS (
                SELECT 1 FROM content c2 
                WHERE c2.series_name = content.series_name 
                AND c2.title != content.series_name 
                AND c2.type = 'SERIES'
            )
            ORDER BY series_name
        """)
        
        series_list = [row[0] for row in cur.fetchall()]
        return series_list
        
    except Exception as e:
        print(f"❌ Error getting series list: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to process all series individually."""
    print("🎬 Processing All Series Individually")
    print("=" * 60)
    
    # Get all series with episodes
    all_series = get_all_series_with_episodes()
    
    if not all_series:
        print("❌ No series with episodes found")
        return
    
    print(f"📺 Found {len(all_series)} series with episodes:")
    for series in all_series:
        print(f"  • {series}")
    
    # Process priority series first
    priority_series = [s for s in PRIORITY_SERIES if s in all_series]
    other_series = [s for s in all_series if s not in PRIORITY_SERIES]
    
    total_moved = 0
    total_skipped = 0
    
    # Process priority series
    if priority_series:
        print(f"\n🎯 Processing Priority Series:")
        for series in priority_series:
            moved, skipped = process_single_series(series)
            total_moved += moved
            total_skipped += skipped
    
    # Process other series
    if other_series:
        print(f"\n📺 Processing Other Series:")
        for series in other_series:
            moved, skipped = process_single_series(series)
            total_moved += moved
            total_skipped += skipped
    
    print(f"\n🎉 Final Summary:")
    print("=" * 40)
    print(f"Total episodes moved: {total_moved}")
    print(f"Total episodes skipped: {total_skipped}")
    print(f"Total series processed: {len(all_series)}")
    
    if total_moved > 0:
        print(f"\n✅ Successfully moved {total_moved} episodes to the episodes table!")

if __name__ == "__main__":
    main() 