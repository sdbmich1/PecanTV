#!/usr/bin/env python3
"""
Fix carousel categorization issues by moving episodes to episodes table
and updating content types properly - Version 3 with proper foreign key handling.
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

def fix_carousel_categorization():
    """Fix all carousel categorization issues"""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔧 Fixing Carousel Categorization Issues - Version 3")
        print("=" * 60)
        
        # 1. Check what episodes already exist in episodes table
        print("\n1. 🔍 Checking existing episodes...")
        
        cur.execute("SELECT title, series_id, season_number, episode_number FROM episodes ORDER BY series_id, season_number, episode_number")
        existing_episodes = cur.fetchall()
        
        print(f"   Found {len(existing_episodes)} existing episodes")
        
        # 2. Get series IDs
        print("\n2. 🔍 Getting series IDs...")
        
        cur.execute("SELECT id, uuid FROM content WHERE title = 'Bonanza' AND type = 'SERIES'")
        bonanza_series = cur.fetchone()
        if not bonanza_series:
            print("   ❌ Bonanza series not found!")
            return
        
        cur.execute("SELECT id, uuid FROM content WHERE title = 'Man with a Camera' AND type = 'SERIES'")
        man_with_camera_series = cur.fetchone()
        if not man_with_camera_series:
            print("   ❌ Man with a Camera series not found!")
            return
        
        bonanza_series_id = bonanza_series[0]
        bonanza_content_uuid = bonanza_series[1]
        man_with_camera_series_id = man_with_camera_series[0]
        man_with_camera_content_uuid = man_with_camera_series[1]
        
        print(f"   ✅ Bonanza series ID: {bonanza_series_id}")
        print(f"   ✅ Man with a Camera series ID: {man_with_camera_series_id}")
        
        # 3. Find episodes in content table that need to be moved
        print("\n3. 🔍 Finding episodes in content table...")
        
        episodes_to_check = [
            "The Fear Merchants",
            "The Gunmen", 
            "The Last Trophy",
            "The Killer",
            "So, Who's Fred Hornbeck?",
            "Spell Legacy Like Death"
        ]
        
        placeholders = ','.join(['%s'] * len(episodes_to_check))
        cur.execute(f"""
            SELECT id, title, type, series_name, poster_url, content_url, description, 
                   runtime, genre_id, rating_id, release_date, created_at, updated_at, uuid
            FROM content 
            WHERE title IN ({placeholders})
        """, episodes_to_check)
        
        episodes_in_content = cur.fetchall()
        print(f"   Found {len(episodes_in_content)} episodes in content table")
        
        # 4. Check which episodes already exist in episodes table
        existing_titles = [ep[0] for ep in existing_episodes]
        
        episodes_to_move = []
        episodes_to_delete = []
        
        for episode_data in episodes_in_content:
            content_id, title, content_type, series_name, poster_url, content_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at, content_uuid = episode_data
            
            if title in existing_titles:
                print(f"   ⚠️  '{title}' already exists in episodes table - will delete from content table")
                episodes_to_delete.append(content_id)
            else:
                print(f"   📦 '{title}' needs to be moved to episodes table")
                episodes_to_move.append(episode_data)
        
        # 5. Move new episodes to episodes table
        print(f"\n4. 📦 Moving {len(episodes_to_move)} new episodes to episodes table...")
        
        episodes_moved = 0
        for episode_data in episodes_to_move:
            content_id, title, content_type, series_name, poster_url, content_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at, content_uuid = episode_data
            
            # Determine which series this episode belongs to
            if title in ["The Fear Merchants", "The Gunmen", "The Last Trophy", "The Killer"]:
                series_id = bonanza_series_id
                content_uuid_to_use = bonanza_content_uuid
                # Find next available episode number for Bonanza
                cur.execute("SELECT MAX(episode_number) FROM episodes WHERE series_id = %s AND season_number = 1", (bonanza_series_id,))
                max_episode = cur.fetchone()[0] or 0
                episode_number = max_episode + 1
            elif title in ["So, Who's Fred Hornbeck?"]:
                series_id = man_with_camera_series_id
                content_uuid_to_use = man_with_camera_content_uuid
                # Find next available episode number for Man with a Camera
                cur.execute("SELECT MAX(episode_number) FROM episodes WHERE series_id = %s AND season_number = 1", (man_with_camera_series_id,))
                max_episode = cur.fetchone()[0] or 0
                episode_number = max_episode + 1
            elif title == "Spell Legacy Like Death":
                # This might be a standalone episode or belong to a different series
                # For now, let's skip it and just delete it from content table
                print(f"   ⚠️  Skipping '{title}' - needs manual categorization")
                episodes_to_delete.append(content_id)
                continue
            
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
                episode_uuid, title, description, 1, episode_number,
                runtime, content_url, poster_url, series_id, content_uuid_to_use,
                created_at, updated_at
            ))
            
            episodes_moved += 1
            print(f"   ✅ Moved '{title}' to episodes table (episode {episode_number})")
        
        # 6. Delete episodes from content table
        print(f"\n5. 🗑️  Removing {len(episodes_to_delete)} episodes from content table...")
        
        if episodes_to_delete:
            placeholders = ','.join(['%s'] * len(episodes_to_delete))
            cur.execute(f"DELETE FROM content WHERE id IN ({placeholders})", episodes_to_delete)
            deleted_count = cur.rowcount
            print(f"   ✅ Deleted {deleted_count} episodes from content table")
        else:
            deleted_count = 0
            print("   ℹ️  No episodes to delete from content table")
        
        # 7. Commit all changes
        conn.commit()
        
        print(f"\n✅ Successfully fixed carousel categorization!")
        print(f"   📦 Episodes moved to episodes table: {episodes_moved}")
        print(f"   🗑️  Episodes removed from content table: {deleted_count}")
        
        # 8. Verify the fix
        print("\n6. 🔍 Verifying the fix...")
        
        # Check content table for remaining issues
        cur.execute("""
            SELECT title, type FROM content 
            WHERE title IN ('The Fear Merchants', 'The Gunmen', 'The Last Trophy', 
                           'The Killer', 'So, Who\'s Fred Hornbeck?', 'Spell Legacy Like Death')
        """)
        remaining_issues = cur.fetchall()
        
        if remaining_issues:
            print("   ⚠️  Remaining issues found:")
            for title, content_type in remaining_issues:
                print(f"      - {title} (type: {content_type})")
        else:
            print("   ✅ No remaining categorization issues found!")
        
        # Check episodes table
        cur.execute("""
            SELECT title, series_id FROM episodes 
            WHERE title IN ('The Fear Merchants', 'The Gunmen', 'The Last Trophy', 
                           'The Killer', 'So, Who\'s Fred Hornbeck?', 'Spell Legacy Like Death')
        """)
        episodes_in_table = cur.fetchall()
        
        print(f"   📊 Episodes now in episodes table: {len(episodes_in_table)}")
        for title, series_id in episodes_in_table:
            series_name = "Bonanza" if series_id == bonanza_series_id else "Man with a Camera"
            print(f"      - {title} (series: {series_name})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_carousel_categorization() 