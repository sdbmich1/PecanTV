#!/usr/bin/env python3
"""
Script to fix all trailer URLs in the database that are double-prefixed (e.g., contain both the series and trailer bucket URLs).
"""

import psycopg2
from psycopg2.extras import RealDictCursor
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

TRAILER_BUCKET = 'https://storage.googleapis.com/pecantv_trailers/'


def fix_trailer_urls():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        print("🔧 Fixing double-prefixed trailer URLs...")
        cur.execute("""
            SELECT id, title, trailer_url FROM content WHERE trailer_url LIKE '%https://storage.googleapis.com/pecantv_series/%https://storage.googleapis.com/pecantv_trailers/%'
        """)
        items = cur.fetchall()
        fixed = 0
        for item in items:
            url = item['trailer_url']
            # Extract the correct trailer URL
            match = re.search(r'(https://storage.googleapis.com/pecantv_trailers/[^\s]+)', url)
            if match:
                new_url = match.group(1)
                cur.execute("UPDATE content SET trailer_url = %s WHERE id = %s", (new_url, item['id']))
                print(f"  ✅ Fixed trailer for: {item['title']}\n    Old: {url}\n    New: {new_url}")
                fixed += 1
        conn.commit()
        print(f"\n✅ Fixed {fixed} trailer URLs.")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_trailer_urls() 