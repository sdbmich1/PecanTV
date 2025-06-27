#!/usr/bin/env python3
"""
Script to check for any remaining URLs that still reference incorrect folder paths.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_remaining_wrong_urls():
    """Check for any remaining URLs with incorrect folder paths."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking for Remaining Wrong URLs")
        print("=" * 50)
        
        # Check for petrocelli_final_episodes references
        cur.execute("""
            SELECT id, title, content_url, poster_url, type
            FROM content 
            WHERE content_url LIKE '%petrocelli_final_episodes%' 
            OR poster_url LIKE '%petrocelli_final_episodes%'
            OR trailer_url LIKE '%petrocelli_final_episodes%'
        """)
        
        content_items = cur.fetchall()
        if content_items:
            print(f"\n❌ Found {len(content_items)} content items with petrocelli_final_episodes:")
            for item in content_items:
                print(f"  • {item['title']} (ID: {item['id']}, Type: {item['type']})")
                print(f"    Content URL: {item['content_url']}")
                print(f"    Poster URL: {item['poster_url']}")
        else:
            print("✅ No content items with petrocelli_final_episodes found")
        
        # Check episodes table
        cur.execute("""
            SELECT id, title, content_url, poster_url
            FROM episodes 
            WHERE content_url LIKE '%petrocelli_final_episodes%' 
            OR poster_url LIKE '%petrocelli_final_episodes%'
        """)
        
        episodes = cur.fetchall()
        if episodes:
            print(f"\n❌ Found {len(episodes)} episodes with petrocelli_final_episodes:")
            for episode in episodes:
                print(f"  • {episode['title']} (ID: {episode['id']})")
                print(f"    Content URL: {episode['content_url']}")
                print(f"    Poster URL: {episode['poster_url']}")
        else:
            print("✅ No episodes with petrocelli_final_episodes found")
        
        # Check for any other duplicate folder patterns
        cur.execute("""
            SELECT id, title, content_url, poster_url, type
            FROM content 
            WHERE content_url LIKE '%/%/%' 
            AND content_url LIKE 'https://storage.googleapis.com/pecantv_series/%'
        """)
        
        duplicate_folders = cur.fetchall()
        if duplicate_folders:
            print(f"\n⚠️  Found {len(duplicate_folders)} content items with potential duplicate folders:")
            for item in duplicate_folders:
                print(f"  • {item['title']} (ID: {item['id']}, Type: {item['type']})")
                print(f"    Content URL: {item['content_url']}")
        else:
            print("✅ No content items with duplicate folders found")
        
        # Check episodes table for duplicate folders
        cur.execute("""
            SELECT id, title, content_url, poster_url
            FROM episodes 
            WHERE content_url LIKE '%/%/%' 
            AND content_url LIKE 'https://storage.googleapis.com/pecantv_series/%'
        """)
        
        duplicate_episode_folders = cur.fetchall()
        if duplicate_episode_folders:
            print(f"\n⚠️  Found {len(duplicate_episode_folders)} episodes with potential duplicate folders:")
            for episode in duplicate_episode_folders:
                print(f"  • {episode['title']} (ID: {episode['id']})")
                print(f"    Content URL: {episode['content_url']}")
        else:
            print("✅ No episodes with duplicate folders found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_remaining_wrong_urls() 