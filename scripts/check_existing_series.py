#!/usr/bin/env python3
"""
Script to check what series exist in the database that might match the ones in the Wurl file.
"""

import psycopg2

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_existing_series():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get all series from content table
        cur.execute("""
            SELECT id, title, type FROM content 
            WHERE type = 'SERIES'
            ORDER BY title
        """)
        
        series = cur.fetchall()
        print("📺 Series in database:")
        print("=" * 40)
        for series_id, title, content_type in series:
            print(f"  ID: {series_id}, Title: '{title}', Type: {content_type}")
            
        # Also check for any content with 'Cody', 'Ranger', 'Hornet', or 'Zorro' in the title
        cur.execute("""
            SELECT id, title, type FROM content 
            WHERE title ILIKE '%cody%' OR title ILIKE '%ranger%' OR title ILIKE '%hornet%' OR title ILIKE '%zorro%'
            ORDER BY title
        """)
        
        matches = cur.fetchall()
        print(f"\n🔍 Content matching keywords:")
        print("=" * 40)
        for content_id, title, content_type in matches:
            print(f"  ID: {content_id}, Title: '{title}', Type: {content_type}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_existing_series() 