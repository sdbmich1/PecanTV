#!/usr/bin/env python3
"""
Script to fix final issues:
1. Remove non-existent Sherlock Holmes 1,2,3 from favorites
2. Fix The Man Below to be a series episode from Man with a Camera
3. Check favorites functionality
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

def remove_nonexistent_sherlock_favorites():
    """Remove favorites for non-existent Sherlock Holmes 1, 2, 3."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Removing non-existent Sherlock Holmes favorites")
        print("=" * 50)
        
        # Check current favorites
        cur.execute("""
            SELECT f.id, f.user_id, c.title, c.id as content_id
            FROM favorites f 
            JOIN content c ON f.content_id = c.id 
            WHERE f.user_id = 1 AND c.title IN ('Sherlock Holmes 1', 'Sherlock Holmes 2', 'Sherlock Holmes 3')
        """)
        
        sherlock_favorites = cur.fetchall()
        print(f"Found {len(sherlock_favorites)} Sherlock Holmes favorites to remove:")
        
        for fav_id, user_id, title, content_id in sherlock_favorites:
            print(f"  • {title} (Content ID: {content_id}, Favorite ID: {fav_id})")
        
        # Remove these favorites
        if sherlock_favorites:
            cur.execute("""
                DELETE FROM favorites 
                WHERE user_id = 1 AND content_id IN (27, 28, 29)
            """)
            
            deleted_count = cur.rowcount
            print(f"✅ Removed {deleted_count} non-existent Sherlock Holmes favorites")
        else:
            print("✅ No non-existent Sherlock Holmes favorites found")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fix_man_below_episode():
    """Fix The Man Below to be a series episode from Man with a Camera."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔧 Fixing The Man Below episode")
        print("=" * 50)
        
        # Update The Man Below to be a series episode
        cur.execute("""
            UPDATE content 
            SET type = 'SERIES', 
                series_name = 'Man with a Camera',
                episode_number = 1,
                season_number = 1
            WHERE title = 'The Man Below'
        """)
        
        updated_count = cur.rowcount
        if updated_count > 0:
            print("✅ Updated The Man Below to be a SERIES episode from Man with a Camera")
            
            # Get the updated record
            cur.execute("""
                SELECT id, title, type, series_name, episode_number, season_number
                FROM content 
                WHERE title = 'The Man Below'
            """)
            
            record = cur.fetchone()
            if record:
                content_id, title, content_type, series_name, episode_number, season_number = record
                print(f"  • {title} (ID: {content_id})")
                print(f"  • Type: {content_type}")
                print(f"  • Series: {series_name}")
                print(f"  • Episode: {episode_number}, Season: {season_number}")
        else:
            print("⚠️  The Man Below not found or already updated")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def check_favorites_after_fixes():
    """Check favorites status after fixes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔍 Checking Favorites After Fixes")
        print("=" * 50)
        
        # Check favorites for user 1
        cur.execute("""
            SELECT f.id, f.user_id, c.title, c.id as content_id, c.type, f.created_at 
            FROM favorites f 
            JOIN content c ON f.content_id = c.id 
            WHERE f.user_id = 1
            ORDER BY f.created_at
        """)
        
        favorites = cur.fetchall()
        print(f"Favorites for user 1: {len(favorites)}")
        
        for fav in favorites:
            fav_id, user_id, title, content_id, content_type, created_at = fav
            print(f"  • {title} (ID: {content_id}, Type: {content_type})")
        
        # Check if any favorites point to non-existent content
        cur.execute("""
            SELECT f.id, f.user_id, f.content_id
            FROM favorites f 
            LEFT JOIN content c ON f.content_id = c.id 
            WHERE f.user_id = 1 AND c.id IS NULL
        """)
        
        orphaned_favorites = cur.fetchall()
        if orphaned_favorites:
            print(f"\n⚠️  Found {len(orphaned_favorites)} orphaned favorites:")
            for fav_id, user_id, content_id in orphaned_favorites:
                print(f"  • Favorite ID: {fav_id}, Content ID: {content_id}")
        else:
            print("\n✅ All favorites point to valid content")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

def test_api_favorites():
    """Test the favorites API endpoint."""
    import requests
    
    print("\n🌐 Testing Favorites API")
    print("=" * 50)
    
    base_url = "https://77b9-192-69-240-171.ngrok-free.app"
    
    try:
        # Test favorites endpoint
        response = requests.get(f"{base_url}/favorites/1")
        print(f"GET /favorites/1: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            favorites = data.get('favorites', [])
            print(f"✅ Favorites returned: {len(favorites)} items")
            
            for fav in favorites:
                print(f"  • {fav.get('title', 'Unknown')} (ID: {fav.get('id', 'Unknown')})")
        else:
            print(f"❌ Favorites error: {response.text}")
            
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        print(f"GET /health: {response.status_code}")
        
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    remove_nonexistent_sherlock_favorites()
    fix_man_below_episode()
    check_favorites_after_fixes()
    test_api_favorites() 