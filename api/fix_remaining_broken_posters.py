#!/usr/bin/env python3
"""
Script to fix the remaining broken poster URLs.
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

def fix_remaining_broken_posters():
    """Update remaining broken poster URLs."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing remaining broken poster URLs")
        print("=" * 50)
        
        # Define the fixes: title -> correct filename
        poster_fixes = {
            'Inframan': 'https://storage.googleapis.com/pecantv_title_images/Inframan_title-img.png',  # This file doesn't exist, will need to be uploaded
            'Sherlock Holmes in Dressed to Kill': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg',
            'Sherlock Holmes The Animated Series': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg',
            'Sherlock Holmes in The Secret Weapon': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg',
            'Sherlock Holmes in Woman in Green': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg',
            'Jesse Owens: The Fastest Man in the World Part I': 'https://storage.googleapis.com/pecantv_title_images/Jesse-Owens-Feature-Img.png',
            'Jesse Owens: The Fastest Man in the World Part II': 'https://storage.googleapis.com/pecantv_title_images/Jesse-Owens-Feature-Img.png',
            'The Case of Lady Beryl': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg',
            'The Case of Harry Crocker': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg',
            'The Case of the Cunningham Heritage': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-Series-Img.jpg'
        }
        
        updated_count = 0
        
        for title, new_url in poster_fixes.items():
            try:
                cur.execute(
                    "UPDATE content SET poster_url = %s, updated_at = NOW() WHERE title = %s",
                    (new_url, title)
                )
                if cur.rowcount > 0:
                    print(f"✅ Updated '{title}' -> {new_url.split('/')[-1]}")
                    updated_count += 1
                else:
                    print(f"❌ No rows updated for '{title}'")
            except Exception as e:
                print(f"❌ Error updating '{title}': {e}")
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} poster URLs")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_remaining_broken_posters() 