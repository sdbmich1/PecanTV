#!/usr/bin/env python3
"""
Final script to fix any remaining issues and check for missing content.
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

def check_missing_petrocelli_episodes():
    """Check for any Petrocelli episodes that might be missing."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Checking for Missing Petrocelli Episodes")
        print("=" * 50)
        
        # Check for any content with Petrocelli in description that might be episodes
        cur.execute("""
            SELECT id, title, description, type, series_name
            FROM content 
            WHERE description LIKE '%Petrocelli%' 
            ORDER BY title
        """)
        
        episodes = cur.fetchall()
        print(f"Found {len(episodes)} items with Petrocelli in description:")
        
        for episode_id, title, description, content_type, series_name in episodes:
            print(f"  • {title} (Type: {content_type}, Series: {series_name or 'None'})")
        
        # Check for any content with Petrocelli in title that might be episodes
        cur.execute("""
            SELECT id, title, description, type, series_name
            FROM content 
            WHERE title LIKE '%Petrocelli%' AND title != 'Petrocelli'
            ORDER BY title
        """)
        
        title_episodes = cur.fetchall()
        print(f"\nFound {len(title_episodes)} items with Petrocelli in title:")
        
        for episode_id, title, description, content_type, series_name in title_episodes:
            print(f"  • {title} (Type: {content_type}, Series: {series_name or 'None'})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

def check_favorites_status():
    """Check the current status of favorites."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔍 Checking Favorites Status")
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
            print(f"\n⚠️  Found {len(orphaned_favorites)} orphaned favorites (pointing to non-existent content):")
            for fav_id, user_id, content_id in orphaned_favorites:
                print(f"  • Favorite ID: {fav_id}, Content ID: {content_id}")
        else:
            print("\n✅ All favorites point to valid content")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

def check_series_content():
    """Check all SERIES type content."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🔍 Checking SERIES Content")
        print("=" * 50)
        
        cur.execute("""
            SELECT id, title, series_name, type
            FROM content 
            WHERE type = 'SERIES'
            ORDER BY title
        """)
        
        series = cur.fetchall()
        print(f"Found {len(series)} SERIES items:")
        
        for content_id, title, series_name, content_type in series:
            print(f"  • {title} (Series: {series_name or 'None'})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

def test_api_endpoints():
    """Test the API endpoints."""
    import requests
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    base_url = "https://77b9-192-69-240-171.ngrok-free.app"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        print(f"GET /health: {response.status_code}")
        
        # Test content endpoint
        response = requests.get(f"{base_url}/content")
        print(f"GET /content: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Content returned: {len(data)} items")
        
        # Test favorites endpoint
        response = requests.get(f"{base_url}/favorites/1")
        print(f"GET /favorites/1: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Favorites returned: {len(data.get('favorites', []))} items")
        else:
            print(f"Favorites error: {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    check_missing_petrocelli_episodes()
    check_favorites_status()
    check_series_content()
    test_api_endpoints() 