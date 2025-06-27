#!/usr/bin/env python3
"""
Comprehensive script to fix all video URLs for films and episodes.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
import re

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def normalize_series_name(series_name):
    """Convert series name to lowercase with underscores for folder names."""
    return series_name.lower().replace(' ', '_').replace('-', '_')

def fix_video_urls():
    """Fix all video URLs to use correct Google Cloud Storage paths."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing All Video URLs")
        print("=" * 50)
        
        # Fix film URLs
        print("\n📽️ Fixing Film URLs...")
        cur.execute("""
            SELECT id, title, content_url, trailer_url, type
            FROM content 
            WHERE type = 'FILM'
            ORDER BY title
        """)
        
        films = cur.fetchall()
        film_updates = 0
        
        for film in films:
            old_content_url = film['content_url']
            old_trailer_url = film['trailer_url']
            
            # Fix content URL
            new_content_url = old_content_url
            if old_content_url and 'pecantv_features' in old_content_url:
                # Films should use pecantv_features bucket
                new_content_url = old_content_url
            
            # Fix trailer URL (if it exists)
            new_trailer_url = old_trailer_url
            if old_trailer_url and 'pecantv_features' in old_trailer_url:
                new_trailer_url = old_trailer_url
            
            # Update if URLs changed
            if new_content_url != old_content_url or new_trailer_url != old_trailer_url:
                cur.execute("""
                    UPDATE content 
                    SET content_url = %s, trailer_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_content_url, new_trailer_url, datetime.now(timezone.utc), film['id']))
                film_updates += 1
        
        print(f"  ✅ Updated {film_updates} films")
        
        # Fix episode URLs
        print("\n📺 Fixing Episode URLs...")
        cur.execute("""
            SELECT e.id, e.title, e.content_url, e.poster_url, c.title as series_title
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            ORDER BY c.title, e.episode_number
        """)
        
        episodes = cur.fetchall()
        episode_updates = 0
        
        for episode in episodes:
            old_content_url = episode['content_url']
            old_poster_url = episode['poster_url']
            series_name = episode['series_title']
            
            # Determine correct series folder
            series_folder = normalize_series_name(series_name)
            
            # Fix content URL
            new_content_url = old_content_url
            if old_content_url and 'pecantv_series' in old_content_url:
                # Extract filename from URL
                filename = old_content_url.split('/')[-1]
                new_content_url = f"https://storage.googleapis.com/pecantv_series/{series_folder}/{filename}"
            
            # Fix poster URL
            new_poster_url = old_poster_url
            if old_poster_url and 'pecantv_series' in old_poster_url:
                # Extract filename from URL
                filename = old_poster_url.split('/')[-1]
                new_poster_url = f"https://storage.googleapis.com/pecantv_series/{series_folder}/{filename}"
            
            # Update if URLs changed
            if new_content_url != old_content_url or new_poster_url != old_poster_url:
                cur.execute("""
                    UPDATE episodes 
                    SET content_url = %s, poster_url = %s, updated_at = %s
                    WHERE id = %s
                """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode['id']))
                
                print(f"  ✅ {series_name} - {episode['title']}")
                print(f"     Content: {old_content_url} → {new_content_url}")
                print(f"     Poster: {old_poster_url} → {new_poster_url}")
                episode_updates += 1
        
        conn.commit()
        print(f"\n✅ Updated {episode_updates} episodes")
        print(f"✅ Total updates: {film_updates + episode_updates}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_video_urls() 