#!/usr/bin/env python3
"""
Script to fix series structure issues and handle duplicate constraints properly.
Version 2 with improved constraint handling.
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

def check_series_structure():
    """Check the structure of all series and identify issues."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Checking Series Structure")
        print("=" * 50)
        
        # Get all unique series names
        cur.execute("""
            SELECT DISTINCT series_name 
            FROM content 
            WHERE series_name IS NOT NULL 
            AND series_name != '' 
            ORDER BY series_name
        """)
        
        series_names = [row[0] for row in cur.fetchall()]
        
        issues = []
        
        for series_name in series_names:
            print(f"\n📺 Checking: {series_name}")
            
            # Check if main series record exists
            cur.execute("""
                SELECT id, title FROM content 
                WHERE type = 'SERIES' AND title = %s
            """, (series_name,))
            main_record = cur.fetchone()
            
            if not main_record:
                print(f"  ❌ Missing main series record")
                issues.append({
                    'series_name': series_name,
                    'issue': 'missing_main_record',
                    'action': 'create_main_record'
                })
            else:
                print(f"  ✅ Main series record exists (ID: {main_record[0]})")
            
            # Count episode records
            cur.execute("""
                SELECT COUNT(*) FROM content 
                WHERE series_name = %s AND title != %s AND type = 'SERIES'
            """, (series_name, series_name))
            episode_count = cur.fetchone()[0]
            
            print(f"  📺 Episode records in content table: {episode_count}")
            
            if episode_count > 0:
                issues.append({
                    'series_name': series_name,
                    'issue': 'has_episode_records',
                    'action': 'move_to_episodes_table',
                    'episode_count': episode_count
                })
        
        return issues
        
    except Exception as e:
        print(f"❌ Error checking series structure: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def create_missing_series_records(issues):
    """Create missing main series records."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔧 Creating Missing Series Records")
        print("=" * 40)
        
        missing_records = [issue for issue in issues if issue['action'] == 'create_main_record']
        
        if not missing_records:
            print("✅ No missing series records to create")
            return
        
        for issue in missing_records:
            series_name = issue['series_name']
            print(f"\n📺 Creating main record for: {series_name}")
            
            # Get sample episode data to use for main series
            cur.execute("""
                SELECT description, runtime, content_url, poster_url, genre_id, rating_id
                FROM content 
                WHERE series_name = %s AND title != %s AND type = 'SERIES'
                LIMIT 1
            """, (series_name, series_name))
            
            sample_data = cur.fetchone()
            if sample_data:
                description, runtime, content_url, poster_url, genre_id, rating_id = sample_data
                
                cur.execute("""
                    INSERT INTO content (
                        uuid, title, description, type, runtime, content_url, poster_url,
                        trailer_url, genre_id, rating_id, series_name, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    str(uuid.uuid4()),
                    series_name,
                    description or f"Episodes of {series_name}",
                    'SERIES',
                    runtime or 60,
                    content_url or '',
                    poster_url or '',
                    '',  # trailer_url (empty string instead of null)
                    genre_id,
                    rating_id,
                    series_name,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                print(f"  ✅ Created main series record")
            else:
                print(f"  ⚠️  No sample data found, creating basic record")
                cur.execute("""
                    INSERT INTO content (
                        uuid, title, description, type, runtime, content_url, poster_url,
                        trailer_url, genre_id, rating_id, series_name, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    str(uuid.uuid4()),
                    series_name,
                    f"Episodes of {series_name}",
                    'SERIES',
                    60,
                    '',
                    '',
                    '',  # trailer_url (empty string instead of null)
                    None,
                    None,
                    series_name,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                print(f"  ✅ Created basic main series record")
        
        conn.commit()
        print(f"\n✅ Created {len(missing_records)} missing series records")
        
    except Exception as e:
        print(f"❌ Error creating series records: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def move_episodes_safely(issues):
    """Move episodes to episodes table with better duplicate handling."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n📦 Moving Episodes to Episodes Table")
        print("=" * 45)
        
        move_issues = [issue for issue in issues if issue['action'] == 'move_to_episodes_table']
        
        if not move_issues:
            print("✅ No episodes to move")
            return
        
        total_moved = 0
        total_skipped = 0
        
        for issue in move_issues:
            series_name = issue['series_name']
            print(f"\n🎬 Processing: {series_name}")
            
            # Get the main series record
            cur.execute("""
                SELECT id, uuid FROM content 
                WHERE type = 'SERIES' AND title = %s
            """, (series_name,))
            series_record = cur.fetchone()
            
            if not series_record:
                print(f"  ❌ Main series record not found, skipping")
                continue
            
            series_id, series_uuid = series_record
            
            # Get episode records
            cur.execute("""
                SELECT id, uuid, title, description, runtime, content_url, poster_url, 
                       episode_number, season_number, genre_id, rating_id
                FROM content 
                WHERE series_name = %s AND title != %s AND type = 'SERIES'
                ORDER BY season_number, episode_number, title
            """, (series_name, series_name))
            
            episode_records = cur.fetchall()
            print(f"  📺 Found {len(episode_records)} episode records")
            
            moved_count = 0
            skipped_count = 0
            
            for episode in episode_records:
                episode_id, episode_uuid, title, description, runtime, content_url, poster_url, episode_number, season_number, genre_id, rating_id = episode
                
                # Check if episode already exists in episodes table by title
                cur.execute("SELECT id FROM episodes WHERE title = %s AND series_id = %s", (title, series_id))
                if cur.fetchone():
                    print(f"    ⚠️  Episode already exists by title, skipping: {title}")
                    skipped_count += 1
                    continue
                
                # Check if episode already exists by season/episode number
                if episode_number and season_number:
                    cur.execute("SELECT id FROM episodes WHERE series_id = %s AND season_number = %s AND episode_number = %s", 
                               (series_id, season_number, episode_number))
                    if cur.fetchone():
                        print(f"    ⚠️  Episode already exists by season/episode number, skipping: S{season_number}E{episode_number} - {title}")
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
                    
                    print(f"    ✅ Moved episode: {title}")
                    moved_count += 1
                    
                except psycopg2.IntegrityError as e:
                    if "duplicate key value violates unique constraint" in str(e):
                        print(f"    ⚠️  Duplicate constraint violation, skipping: {title}")
                        skipped_count += 1
                    else:
                        print(f"    ❌ Integrity error for {title}: {e}")
                        skipped_count += 1
                except Exception as e:
                    print(f"    ❌ Error inserting {title}: {e}")
                    skipped_count += 1
            
            print(f"  📊 Summary for {series_name}:")
            print(f"    Episodes moved: {moved_count}")
            print(f"    Episodes skipped: {skipped_count}")
            
            total_moved += moved_count
            total_skipped += skipped_count
        
        conn.commit()
        print(f"\n🎉 Final Summary:")
        print(f"Total episodes moved: {total_moved}")
        print(f"Total episodes skipped: {total_skipped}")
        
    except Exception as e:
        print(f"❌ Error moving episodes: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to fix series structure."""
    print("🔧 Fixing Series Structure (v2)")
    print("=" * 60)
    
    # Check current structure
    issues = check_series_structure()
    
    if not issues:
        print("\n✅ No issues found!")
        return
    
    # Create missing series records
    create_missing_series_records(issues)
    
    # Move episodes safely
    move_episodes_safely(issues)
    
    print("\n🎉 Series structure fix completed!")

if __name__ == "__main__":
    main() 