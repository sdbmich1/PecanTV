#!/usr/bin/env python3
"""
Script to fix remaining data issues and investigate favorites problem.
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

def fix_petrocelli_episodes():
    """Fix Petrocelli episodes by changing type from FILM to SERIES."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing Petrocelli Episodes")
        print("=" * 50)
        
        # Find all Petrocelli episodes that are still FILM type
        cur.execute("""
            SELECT id, title, description, type
            FROM content 
            WHERE description LIKE '%Petrocelli%' AND type = 'FILM'
            ORDER BY title
        """)
        
        episodes = cur.fetchall()
        print(f"Found {len(episodes)} Petrocelli episodes to fix:")
        
        for episode_id, title, description, current_type in episodes:
            print(f"  • {title} (currently {current_type})")
            
            # Update to SERIES type and set series_name
            cur.execute("""
                UPDATE content 
                SET type = 'SERIES', 
                    series_name = 'Petrocelli',
                    updated_at = %s
                WHERE id = %s
            """, (datetime.now(timezone.utc), episode_id))
            
            print(f"✅ Updated {title} -> SERIES")
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Fixed {len(episodes)} Petrocelli episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fix_man_with_camera():
    """Fix 'Man with a camera' to be SERIES type."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🎬 Fixing 'Man with a camera'")
        print("=" * 50)
        
        # Find 'Man with a camera' content
        cur.execute("""
            SELECT id, title, description, type
            FROM content 
            WHERE title LIKE '%Man with a camera%' OR title LIKE '%Man with a Camera%'
        """)
        
        content = cur.fetchone()
        
        if content:
            content_id, title, description, current_type = content
            print(f"Found: {title} (currently {current_type})")
            
            # Update to SERIES type
            cur.execute("""
                UPDATE content 
                SET type = 'SERIES', 
                    updated_at = %s
                WHERE id = %s
            """, (datetime.now(timezone.utc), content_id))
            
            print(f"✅ Updated {title} -> SERIES")
        else:
            print("⚠️  'Man with a camera' not found")
        
        # Commit changes
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def check_sherlock_holmes_titles():
    """Check what Sherlock Holmes titles actually exist."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔍 Checking Sherlock Holmes Titles")
        print("=" * 50)
        
        cur.execute("""
            SELECT id, title, type
            FROM content 
            WHERE title LIKE '%Sherlock Holmes%'
            ORDER BY title
        """)
        
        titles = cur.fetchall()
        print(f"Found {len(titles)} Sherlock Holmes titles:")
        
        for content_id, title, content_type in titles:
            print(f"  • {title} (type: {content_type})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

def investigate_favorites_issue():
    """Investigate why favorites aren't showing in the app."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔍 Investigating Favorites Issue")
        print("=" * 50)
        
        # Check favorites in database
        cur.execute("""
            SELECT f.id, f.user_id, c.title, c.id as content_id, f.created_at 
            FROM favorites f 
            JOIN content c ON f.content_id = c.id 
            WHERE f.user_id = 1
            ORDER BY f.created_at
        """)
        
        favorites = cur.fetchall()
        print(f"Favorites in database for user 1: {len(favorites)}")
        
        for fav in favorites:
            fav_id, user_id, title, content_id, created_at = fav
            print(f"  • {title} (Content ID: {content_id})")
        
        # Check if the app is looking for the right content IDs
        print(f"\nContent IDs in favorites: {[fav[3] for fav in favorites]}")
        
        # Check if these content IDs exist in the content table
        content_ids = [fav[3] for fav in favorites]
        if content_ids:
            cur.execute("""
                SELECT id, title, type FROM content WHERE id = ANY(%s)
            """, (content_ids,))
            
            existing_content = cur.fetchall()
            print(f"\nContent that exists: {len(existing_content)}")
            for content_id, title, content_type in existing_content:
                print(f"  • {title} (ID: {content_id}, Type: {content_type})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

def test_favorites_api():
    """Test the favorites API endpoints."""
    import requests
    
    print("\n🌐 Testing Favorites API")
    print("=" * 50)
    
    base_url = "https://77b9-192-69-240-171.ngrok-free.app"
    
    try:
        # Test GET favorites
        response = requests.get(f"{base_url}/favorites/1")
        print(f"GET /favorites/1: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Favorites returned: {len(data.get('favorites', []))}")
            for fav in data.get('favorites', []):
                print(f"  • {fav.get('title')} (ID: {fav.get('id')})")
        else:
            print(f"Error: {response.text}")
        
        # Test toggle favorite
        response = requests.post(f"{base_url}/favorites/1/toggle/1")
        print(f"\nPOST /favorites/1/toggle/1: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Toggle response: {data}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    fix_petrocelli_episodes()
    fix_man_with_camera()
    check_sherlock_holmes_titles()
    investigate_favorites_issue()
    test_favorites_api() 