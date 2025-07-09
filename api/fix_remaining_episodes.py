#!/usr/bin/env python3
"""
Fix remaining episode categorization issues by moving episodes from content table 
to episodes table and fixing content types.
"""

import psycopg2
from datetime import datetime, timezone
import uuid

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_remaining_episodes():
    """Fix remaining episode categorization issues"""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔧 Fixing Remaining Episode Categorization Issues")
        print("=" * 55)
        
        # 1. Get series IDs
        print("\n1. 🔍 Getting series IDs...")
        
        series_mapping = {
            'Longstreet': 'Longstreet',
            'CMC': 'The Count of Monte Cristo', 
            'GS': 'Ghost Squad'
        }
        
        series_ids = {}
        for prefix, series_name in series_mapping.items():
            cur.execute("SELECT id, uuid FROM content WHERE title = %s AND type = 'SERIES'", (series_name,))
            series_record = cur.fetchone()
            if series_record:
                series_ids[prefix] = {'id': series_record[0], 'uuid': series_record[1]}
                print(f"   ✅ {series_name} (ID: {series_record[0]})")
            else:
                print(f"   ❌ {series_name} not found!")
        
        # 2. Get episodes that need to be moved
        print("\n2. 🔍 Finding episodes to move...")
        
        episodes_to_move = [
            'Anatomy of a Mayday',
            'Survival Times Two', 
            'The Barefoot Empress',
            'The Dubarry Affair',
            'The Tallyrand Affair',
            'Ticket for Blackmail',
            'Please Leave the Wreck for Others to Enjoy',
            'Lichtenburg'
        ]
        
        placeholders = ','.join(['%s'] * len(episodes_to_move))
        cur.execute(f"""
            SELECT id, title, content_url, poster_url, description, runtime, 
                   genre_id, rating_id, release_date, created_at, updated_at, uuid
            FROM content 
            WHERE title IN ({placeholders}) AND type = 'SERIES'
            ORDER BY title
        """, episodes_to_move)
        
        episodes_data = cur.fetchall()
        print(f"   Found {len(episodes_data)} episodes to move")
        
        # 3. Categorize episodes by series
        print("\n3. 📂 Categorizing episodes by series...")
        
        episodes_by_series = {
            'Longstreet': [],
            'CMC': [],
            'GS': [],
            'Unknown': []
        }
        
        for episode_data in episodes_data:
            content_id, title, content_url, poster_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at, content_uuid = episode_data
            
            # Determine series based on content URL
            if 'Longstreet-' in content_url:
                episodes_by_series['Longstreet'].append(episode_data)
            elif 'CMC' in content_url:
                episodes_by_series['CMC'].append(episode_data)
            elif 'GS-' in content_url:
                episodes_by_series['GS'].append(episode_data)
            else:
                episodes_by_series['Unknown'].append(episode_data)
                print(f"   ⚠️  Unknown series for '{title}'")
        
        # 4. Move episodes to episodes table
        print("\n4. 📦 Moving episodes to episodes table...")
        
        total_moved = 0
        episodes_to_delete = []
        
        for series_prefix, episodes in episodes_by_series.items():
            if series_prefix == 'Unknown':
                print(f"\n   ⚠️  Skipping {len(episodes)} episodes with unknown series")
                for episode_data in episodes:
                    episodes_to_delete.append(episode_data[0])  # content_id
                continue
            
            if not episodes:
                continue
                
            series_info = series_ids.get(series_prefix)
            if not series_info:
                print(f"   ❌ Series info not found for {series_prefix}")
                continue
            
            series_id = series_info['id']
            series_uuid = series_info['uuid']
            
            print(f"\n   🎬 Processing {series_prefix} episodes ({len(episodes)} episodes)")
            
            # Get current max episode number for this series
            cur.execute("SELECT MAX(episode_number) FROM episodes WHERE series_id = %s AND season_number = 1", (series_id,))
            max_episode = cur.fetchone()[0] or 0
            next_episode = max_episode + 1
            
            for episode_data in episodes:
                content_id, title, content_url, poster_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at, content_uuid = episode_data
                
                # Generate new episode UUID
                episode_uuid = str(uuid.uuid4())
                
                # Insert into episodes table
                cur.execute("""
                    INSERT INTO episodes (
                        uuid, title, description, season_number, episode_number, 
                        runtime, content_url, poster_url, series_id, content_uuid,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    episode_uuid, title, description, 1, next_episode,
                    runtime, content_url, poster_url, series_id, content_uuid,
                    created_at, updated_at
                ))
                
                episodes_to_delete.append(content_id)
                total_moved += 1
                print(f"      ✅ Moved '{title}' (episode {next_episode})")
                next_episode += 1
        
        # 5. Delete episodes from content table
        print(f"\n5. 🗑️  Removing {len(episodes_to_delete)} episodes from content table...")
        
        if episodes_to_delete:
            placeholders = ','.join(['%s'] * len(episodes_to_delete))
            cur.execute(f"DELETE FROM content WHERE id IN ({placeholders})", episodes_to_delete)
            deleted_count = cur.rowcount
            print(f"   ✅ Deleted {deleted_count} episodes from content table")
        else:
            deleted_count = 0
            print("   ℹ️  No episodes to delete from content table")
        
        # 6. Fix content types for films
        print("\n6. 🎬 Fixing content types for films...")
        
        films_to_fix = [
            'Beyond Christmas',
            'Cosmos'
        ]
        
        for film_title in films_to_fix:
            cur.execute("""
                UPDATE content 
                SET type = 'FILM' 
                WHERE title = %s AND type = 'SERIES'
            """, (film_title,))
            
            if cur.rowcount > 0:
                print(f"   ✅ Fixed '{film_title}' type to FILM")
            else:
                print(f"   ℹ️  '{film_title}' already has correct type or not found")
        
        # 7. Commit all changes
        conn.commit()
        
        print(f"\n✅ Successfully fixed remaining episode categorization!")
        print(f"   📦 Episodes moved to episodes table: {total_moved}")
        print(f"   🗑️  Episodes removed from content table: {deleted_count}")
        
        # 8. Verify the fix
        print("\n7. 🔍 Verifying the fix...")
        
        # Check content table for remaining issues
        placeholders = ','.join(['%s'] * len(episodes_to_move))
        cur.execute(f"""
            SELECT title, type FROM content 
            WHERE title IN ({placeholders})
        """, episodes_to_move)
        
        remaining_issues = cur.fetchall()
        if remaining_issues:
            print("   ⚠️  Remaining issues found:")
            for title, content_type in remaining_issues:
                print(f"      - {title} (type: {content_type})")
        else:
            print("   ✅ No remaining categorization issues found!")
        
        # Check episodes table
        cur.execute(f"""
            SELECT title, series_id FROM episodes 
            WHERE title IN ({placeholders})
            ORDER BY series_id, episode_number
        """, episodes_to_move)
        
        episodes_in_table = cur.fetchall()
        print(f"   📊 Episodes now in episodes table: {len(episodes_in_table)}")
        
        # Group by series
        episodes_by_series_id = {}
        for title, series_id in episodes_in_table:
            if series_id not in episodes_by_series_id:
                episodes_by_series_id[series_id] = []
            episodes_by_series_id[series_id].append(title)
        
        for series_id, titles in episodes_by_series_id.items():
            series_name = "Unknown"
            for prefix, info in series_ids.items():
                if info['id'] == series_id:
                    series_name = series_mapping[prefix]
                    break
            print(f"      📺 {series_name}: {len(titles)} episodes")
            for title in titles:
                print(f"         - {title}")
        
        # Check film types
        print("\n   🎬 Film content types:")
        for film_title in films_to_fix:
            cur.execute("SELECT title, type FROM content WHERE title = %s", (film_title,))
            result = cur.fetchone()
            if result:
                print(f"      - {result[0]} (type: {result[1]})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_remaining_episodes() 