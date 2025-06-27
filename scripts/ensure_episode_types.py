#!/usr/bin/env python3
"""
Script to ensure all episode content is properly typed as EPISODE and moved to episodes table.
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

def ensure_episode_types():
    """Ensure all episode content is properly typed and organized."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Ensuring Episode Types and Organization")
        print("=" * 50)
        
        # 1. Check for any content records that should be episodes
        cur.execute("""
            SELECT id, title, type, description, runtime, content_url, poster_url, genre_id, rating_id
            FROM content 
            WHERE type != 'SERIES' AND type != 'MOVIE' AND type != 'EPISODE'
            OR title LIKE '%Episode%'
            OR title LIKE '%S%' AND title LIKE '%E%'
        """)
        
        potential_episodes = cur.fetchall()
        
        if potential_episodes:
            print(f"📋 Found {len(potential_episodes)} potential episode records:")
            for record in potential_episodes:
                print(f"  • {record[1]} (Type: {record[2]})")
            
            # Ask user if they want to process these
            response = input("\nDo you want to process these as episodes? (y/n): ").lower().strip()
            
            if response == 'y':
                processed = 0
                for record in potential_episodes:
                    content_id, title, content_type, description, runtime, content_url, poster_url, genre_id, rating_id = record
                    
                    # Try to determine series from title
                    series_name = None
                    if ' - ' in title:
                        series_name = title.split(' - ')[0].strip()
                    elif ' Episode' in title:
                        series_name = title.split(' Episode')[0].strip()
                    
                    if series_name:
                        # Check if series exists
                        cur.execute("SELECT id, uuid FROM content WHERE type = 'SERIES' AND title = %s", (series_name,))
                        series_record = cur.fetchone()
                        
                        if series_record:
                            series_id, series_uuid = series_record
                            
                            # Extract episode number from title
                            episode_number = 1
                            if 'Episode' in title:
                                try:
                                    ep_num_str = title.split('Episode')[-1].strip()
                                    episode_number = int(''.join(filter(str.isdigit, ep_num_str)))
                                except:
                                    episode_number = 1
                            
                            # Check if episode already exists in episodes table
                            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (title, series_id))
                            if not cur.fetchone():
                                # Insert into episodes table
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
                                    description or f"Episode of {series_name}",
                                    1,  # Default season
                                    episode_number,
                                    runtime or 60,
                                    content_url or '',
                                    poster_url or '',
                                    None,  # Air date
                                    series_id,
                                    str(series_uuid),
                                    datetime.now(timezone.utc),
                                    datetime.now(timezone.utc)
                                ))
                                
                                # Update content record type to EPISODE
                                cur.execute("UPDATE content SET type = 'EPISODE' WHERE id = %s", (content_id,))
                                
                                print(f"  ✅ Processed: {title} -> {series_name} Episode {episode_number}")
                                processed += 1
                            else:
                                print(f"  ⚠️  Episode already exists: {title}")
                        else:
                            print(f"  ❌ Series not found: {series_name} for {title}")
                    else:
                        print(f"  ❌ Could not determine series for: {title}")
                
                print(f"\n📊 Processed {processed} episodes")
        
        # 2. Check for any content records with type EPISODE that should be in episodes table
        cur.execute("""
            SELECT id, title, description, runtime, content_url, poster_url, genre_id, rating_id
            FROM content 
            WHERE type = 'EPISODE'
        """)
        
        episode_content = cur.fetchall()
        
        if episode_content:
            print(f"\n📋 Found {len(episode_content)} content records with type EPISODE:")
            for record in episode_content:
                print(f"  • {record[1]}")
            
            response = input("\nDo you want to move these to episodes table? (y/n): ").lower().strip()
            
            if response == 'y':
                moved = 0
                for record in episode_content:
                    content_id, title, description, runtime, content_url, poster_url, genre_id, rating_id = record
                    
                    # Try to determine series from title
                    series_name = None
                    if ' - ' in title:
                        series_name = title.split(' - ')[0].strip()
                    elif ' Episode' in title:
                        series_name = title.split(' Episode')[0].strip()
                    
                    if series_name:
                        # Check if series exists
                        cur.execute("SELECT id, uuid FROM content WHERE type = 'SERIES' AND title = %s", (series_name,))
                        series_record = cur.fetchone()
                        
                        if series_record:
                            series_id, series_uuid = series_record
                            
                            # Check if episode already exists in episodes table
                            cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (title, series_id))
                            if not cur.fetchone():
                                # Insert into episodes table
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
                                    description or f"Episode of {series_name}",
                                    1,  # Default season
                                    1,  # Default episode number
                                    runtime or 60,
                                    content_url or '',
                                    poster_url or '',
                                    None,  # Air date
                                    series_id,
                                    str(series_uuid),
                                    datetime.now(timezone.utc),
                                    datetime.now(timezone.utc)
                                ))
                                
                                print(f"  ✅ Moved to episodes: {title}")
                                moved += 1
                            else:
                                print(f"  ⚠️  Episode already exists: {title}")
                        else:
                            print(f"  ❌ Series not found: {series_name} for {title}")
                    else:
                        print(f"  ❌ Could not determine series for: {title}")
                
                print(f"\n📊 Moved {moved} episodes to episodes table")
        
        # 3. Final summary
        cur.execute("SELECT COUNT(*) FROM content WHERE type = 'EPISODE'")
        episode_content_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM episodes")
        episodes_table_count = cur.fetchone()[0]
        
        print(f"\n📊 Final Summary:")
        print(f"  • Content table episodes: {episode_content_count}")
        print(f"  • Episodes table records: {episodes_table_count}")
        
        conn.commit()
        print("\n✅ Episode type organization completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    ensure_episode_types() 