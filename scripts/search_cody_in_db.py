#!/usr/bin/env python3
"""
Script to search for 'Cody' in any string field in the content or episodes tables and print all matches.
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

def search_cody_in_table(cur, table, fields):
    print(f"\n🔍 Searching for 'Cody' in {table} table...")
    for field in fields:
        query = f"SELECT * FROM {table} WHERE {field} ILIKE '%Cody%'"
        cur.execute(query)
        rows = cur.fetchall()
        if rows:
            print(f"\nField: {field} - {len(rows)} match(es)")
            for row in rows:
                print(row)

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        # Get string fields for content and episodes tables
        content_fields = ['title', 'description', 'genre', 'rating', 'poster_url', 'trailer_url', 'content_url']
        episodes_fields = ['title', 'description', 'poster_url', 'content_url']
        search_cody_in_table(cur, 'content', content_fields)
        search_cody_in_table(cur, 'episodes', episodes_fields)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main() 