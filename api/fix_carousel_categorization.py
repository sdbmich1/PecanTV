#!/usr/bin/env python3
"""
Fix carousel categorization issues by moving episodes to episodes table
and updating content types properly.
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
        print("🔧 Fixing Carousel Categorization Issues")
        print("=" * 50)
        
        # 1. Identify episodes that are incorrectly categorized as FILM
        print("\n1. 🔍 Finding episodes incorrectly categorized as FILM...")
        
        # Bonanza episodes
        bonanza_episodes = [
            "The Fear Merchants",
            "The Gunmen", 
            "The Last Trophy",
            "The Killer"
        ]
        
        # A Man with a Camera episodes
        man_with_camera_episodes = [
            "So, Who's Fred Hornbeck?"
        ]
        
        # Spell Legacy Like Death (should be an episode, not a series)
        spell_legacy = "Spell Legacy Like Death"
        
        all_episode_titles = bonanza_episodes + man_with_camera_episodes + [spell_legacy]
        
        # Find these episodes in the content table
        placeholders = ','.join(['%s'] * len(all_episode_titles))
        cur.execute(f"""
            SELECT id, title, type, series_name, poster_url, content_url, description, 
                   runtime, genre_id, rating_id, release_date, created_at, updated_at
            FROM content 
            WHERE title IN ({placeholders})
        """, all_episode_titles)
        
        episodes_to_move = cur.fetchall()
        print(f"   Found {len(episodes_to_move)} episodes to move to episodes table")
        
        # 2. Get series IDs for Bonanza and Man with a Camera
        print("\n2. 🔍 Getting series IDs...")
        
        cur.execute("SELECT id FROM content WHERE title = 'Bonanza' AND type = 'SERIES'")
        bonanza_series = cur.fetchone()
        if not bonanza_series:
            print("   ❌ Bonanza series not found!")
            return
        
        cur.execute("SELECT id FROM content WHERE title = 'Man with a Camera' AND type = 'SERIES'")
        man_with_camera_series = cur.fetchone()
        if not man_with_camera_series:
            print("   ❌ Man with a Camera series not found!")
            return
        
        bonanza_series_id = bonanza_series[0]
        man_with_camera_series_id = man_with_camera_series[0]
        
        print(f"   ✅ Bonanza series ID: {bonanza_series_id}")
        print(f"   ✅ Man with a Camera series ID: {man_with_camera_series_id}")
        
        # 3. Move episodes to episodes table
        print("\n3. 📦 Moving episodes to episodes table...")
        
        episodes_moved = 0
        for episode_data in episodes_to_move:
            content_id, title, content_type, series_name, poster_url, content_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at = episode_data
            
            # Determine which series this episode belongs to
            if title in bonanza_episodes:
                series_id = bonanza_series_id
                episode_number = bonanza_episodes.index(title) + 1
            elif title in man_with_camera_episodes:
                series_id = man_with_camera_series_id
                episode_number = man_with_camera_episodes.index(title) + 1
            elif title == spell_legacy:
                # Spell Legacy Like Death - need to determine which series it belongs to
                # For now, let's assume it's a standalone episode or belongs to a series
                series_id = bonanza_series_id  # Placeholder - you may need to adjust this
                episode_number = 1
            
            # Generate new UUIDs
            episode_uuid = str(uuid.uuid4())
            content_uuid = str(uuid.uuid4())
            
            # Insert into episodes table
            cur.execute("""
                INSERT INTO episodes (
                    uuid, title, description, season_number, episode_number, 
                    runtime, content_url, poster_url, series_id, content_uuid,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                episode_uuid, title, description, 1, episode_number,
                runtime, content_url, poster_url, series_id, content_uuid,
                created_at, updated_at
            ))
            
            episodes_moved += 1
            print(f"   ✅ Moved '{title}' to episodes table (episode {episode_number})")
        
        # 4. Delete episodes from content table
        print("\n4. 🗑️  Removing episodes from content table...")
        
        content_ids = [ep[0] for ep in episodes_to_move]
        placeholders = ','.join(['%s'] * len(content_ids))
        cur.execute(f"DELETE FROM content WHERE id IN ({placeholders})", content_ids)
        
        deleted_count = cur.rowcount
        print(f"   ✅ Deleted {deleted_count} episodes from content table")
        
        # 5. Update any remaining content categorization issues
        print("\n5. 🔄 Updating remaining content categorization...")
        
        # Check for any remaining episodes in content table
        cur.execute("SELECT COUNT(*) FROM content WHERE type = 'EPISODE'")
        remaining_episodes = cur.fetchone()[0]
        print(f"   📊 Remaining episodes in content table: {remaining_episodes}")
        
        # Commit all changes
        conn.commit()
        
        print(f"\n✅ Successfully fixed carousel categorization!")
        print(f"   📦 Episodes moved to episodes table: {episodes_moved}")
        print(f"   🗑️  Episodes removed from content table: {deleted_count}")
        
        # 6. Verify the fix
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
            print(f"      - {title} (series_id: {series_id})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_carousel_categorization() 