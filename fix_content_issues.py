#!/usr/bin/env python3
"""
Script to fix content issues:
1. Remove Sherlock Holmes 1, 2, 3
2. Fix Beginnings to be Longstreet episode
3. Fix Dragnet Animated episodes to be Dragnet episodes
"""

import psycopg2
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

def remove_sherlock_holmes_duplicates():
    """Remove Sherlock Holmes 1, 2, 3 from content."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🗑️  Removing Sherlock Holmes 1, 2, 3")
        print("=" * 50)
        
        # Check for Sherlock Holmes 1, 2, 3
        cur.execute("""
            SELECT id, title, type FROM content 
            WHERE title IN ('Sherlock Holmes 1', 'Sherlock Holmes 2', 'Sherlock Holmes 3')
            ORDER BY title
        """)
        
        sherlock_items = cur.fetchall()
        print(f"Found {len(sherlock_items)} Sherlock Holmes items to remove:")
        
        for item_id, title, content_type in sherlock_items:
            print(f"  • {title} (ID: {item_id}, Type: {content_type})")
        
        # Remove these items
        if sherlock_items:
            cur.execute("""
                DELETE FROM content 
                WHERE title IN ('Sherlock Holmes 1', 'Sherlock Holmes 2', 'Sherlock Holmes 3')
            """)
            
            deleted_count = cur.rowcount
            print(f"✅ Removed {deleted_count} Sherlock Holmes items")
        else:
            print("✅ No Sherlock Holmes 1, 2, 3 items found")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fix_beginnings_episode():
    """Fix Beginnings to be an episode of Longstreet series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔧 Fixing Beginnings Episode")
        print("=" * 50)
        
        # Get the Longstreet series record
        cur.execute("""
            SELECT id, uuid, title FROM content 
            WHERE series_name = 'Longstreet' AND type = 'SERIES' AND title = 'Longstreet'
        """)
        
        longstreet_series = cur.fetchone()
        if not longstreet_series:
            print("❌ Longstreet series record not found")
            return
            
        series_id, series_uuid, series_title = longstreet_series
        print(f"✅ Found Longstreet series: {series_title} (ID: {series_id})")
        
        # Update Beginnings to be an episode
        cur.execute("""
            UPDATE content 
            SET type = 'SERIES', 
                series_name = 'Longstreet',
                episode_number = 2,
                season_number = 1
            WHERE title = 'Beginnings'
        """)
        
        updated_count = cur.rowcount
        if updated_count > 0:
            print("✅ Updated Beginnings to be Longstreet episode")
            
            # Get the updated record
            cur.execute("""
                SELECT id, title, type, series_name, episode_number, season_number
                FROM content 
                WHERE title = 'Beginnings'
            """)
            
            record = cur.fetchone()
            if record:
                content_id, title, content_type, series_name, episode_number, season_number = record
                print(f"  • {title} (ID: {content_id})")
                print(f"  • Type: {content_type}")
                print(f"  • Series: {series_name}")
                print(f"  • Episode: {episode_number}, Season: {season_number}")
        else:
            print("⚠️  Beginnings not found or already updated")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fix_dragnet_animated_episodes():
    """Fix Dragnet Animated episodes to be under Dragnet series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔧 Fixing Dragnet Animated Episodes")
        print("=" * 50)
        
        # Get the Dragnet series record
        cur.execute("""
            SELECT id, uuid, title FROM content 
            WHERE series_name = 'Dragnet' AND type = 'SERIES' AND title = 'Dragnet'
        """)
        
        dragnet_series = cur.fetchone()
        if not dragnet_series:
            print("❌ Dragnet series record not found")
            return
            
        series_id, series_uuid, series_title = dragnet_series
        print(f"✅ Found Dragnet series: {series_title} (ID: {series_id})")
        
        # Get all Dragnet Animated episodes
        cur.execute("""
            SELECT id, title FROM content 
            WHERE title LIKE 'Dragnet Animated%'
            ORDER BY title
        """)
        
        animated_episodes = cur.fetchall()
        print(f"Found {len(animated_episodes)} Dragnet Animated episodes")
        
        # Update each episode
        for episode_id, episode_title in animated_episodes:
            # Extract episode number from title
            episode_number = None
            if "Episode One" in episode_title:
                episode_number = 1
            elif "Episode Two" in episode_title:
                episode_number = 2
            elif "Episode Three" in episode_title:
                episode_number = 3
            elif "Episode Four" in episode_title:
                episode_number = 4
            elif "Episode Five" in episode_title:
                episode_number = 5
            elif "Episode Six" in episode_title:
                episode_number = 6
            elif "Episode Seven" in episode_title:
                episode_number = 7
            elif "Episode Eight" in episode_title:
                episode_number = 8
            elif "Episode Nine" in episode_title:
                episode_number = 9
            elif "Episode Ten" in episode_title:
                episode_number = 10
            
            if episode_number:
                cur.execute("""
                    UPDATE content 
                    SET series_name = 'Dragnet',
                        episode_number = %s,
                        season_number = 1
                    WHERE id = %s
                """, (episode_number, episode_id))
                
                print(f"✅ Updated {episode_title} -> Episode {episode_number}")
            else:
                print(f"⚠️  Could not determine episode number for: {episode_title}")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def verify_fixes():
    """Verify all fixes were applied correctly."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔍 Verifying Fixes")
        print("=" * 50)
        
        # Check if Sherlock Holmes 1, 2, 3 still exist
        cur.execute("""
            SELECT COUNT(*) FROM content 
            WHERE title IN ('Sherlock Holmes 1', 'Sherlock Holmes 2', 'Sherlock Holmes 3')
        """)
        
        sherlock_count = cur.fetchone()[0]
        print(f"Sherlock Holmes 1,2,3 remaining: {sherlock_count}")
        
        # Check Beginnings
        cur.execute("""
            SELECT title, type, series_name, episode_number 
            FROM content WHERE title = 'Beginnings'
        """)
        
        beginnings = cur.fetchone()
        if beginnings:
            title, content_type, series_name, episode_number = beginnings
            print(f"Beginnings: {title} -> {content_type}, Series: {series_name}, Episode: {episode_number}")
        else:
            print("Beginnings not found")
        
        # Check Dragnet Animated episodes
        cur.execute("""
            SELECT title, series_name, episode_number 
            FROM content 
            WHERE title LIKE 'Dragnet Animated%'
            ORDER BY episode_number
        """)
        
        dragnet_episodes = cur.fetchall()
        print(f"Dragnet Animated episodes: {len(dragnet_episodes)}")
        for title, series_name, episode_number in dragnet_episodes[:5]:  # Show first 5
            print(f"  • {title} -> Series: {series_name}, Episode: {episode_number}")
        
        # Count series vs films
        cur.execute("""
            SELECT type, COUNT(*) 
            FROM content 
            GROUP BY type
        """)
        
        type_counts = cur.fetchall()
        print(f"\nContent type distribution:")
        for content_type, count in type_counts:
            print(f"  • {content_type}: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    remove_sherlock_holmes_duplicates()
    fix_beginnings_episode()
    fix_dragnet_animated_episodes()
    verify_fixes() 