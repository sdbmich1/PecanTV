#!/usr/bin/env python3
"""
Script to check the current trailer URL for Little Shop of Horrors in the database.
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

def check_little_shop_trailer():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking Little Shop of Horrors trailer URL in database...")
        cur.execute("SELECT id, title, trailer_url FROM content WHERE title ILIKE '%Little Shop of Horrors%'")
        result = cur.fetchone()
        
        if result:
            print(f"✅ Found {result['title']} (ID: {result['id']})")
            print(f"   Trailer URL: {result['trailer_url']}")
            
            if 'https://storage.googleapis.com/pecantv_trailers/' in result['trailer_url']:
                print("✅ Trailer URL looks correct")
            else:
                print("❌ Trailer URL may be incorrect!")
        else:
            print("❌ Little Shop of Horrors not found in database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_little_shop_trailer() 