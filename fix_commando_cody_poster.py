#!/usr/bin/env python3
"""
Script to fix Commando Cody - Sky Marshal of the Universe poster URL to use the correct poster image.
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

def fix_commando_cody_poster():
    """Update Commando Cody - Sky Marshal of the Universe poster URL to use the correct poster."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing Commando Cody - Sky Marshal of the Universe poster URL")
        print("=" * 60)
        
        # Get Commando Cody series ID
        cur.execute("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE title = 'Commando Cody - Sky Marshal of the Universe' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Commando Cody - Sky Marshal of the Universe series not found")
            return
        
        series_id, series_title, current_poster = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        print(f"Current poster URL: {current_poster}")
        
        # New poster URL for Commando Cody
        new_poster_url = "https://storage.googleapis.com/pecantv_title_images/CommandoCodyTitleImg-061925.jpg"
        
        # Update the poster URL
        cur.execute("""
            UPDATE content 
            SET poster_url = %s, updated_at = %s
            WHERE id = %s
        """, (new_poster_url, datetime.now(timezone.utc), series_id))
        
        conn.commit()
        print(f"✅ Successfully updated Commando Cody poster URL:")
        print(f"   Old: {current_poster}")
        print(f"   New: {new_poster_url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_commando_cody_poster() 