#!/usr/bin/env python3
"""
Script to check the database structure for series identification.
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

def check_series_structure():
    """Check the database structure for series."""
    print("🔍 Checking database structure for series")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Check content table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'content' 
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("Content table columns:")
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
        
        print()
        
        # Print all distinct values for the type column
        cur.execute("SELECT DISTINCT type FROM content")
        types = cur.fetchall()
        print("Distinct values for type column:")
        for t in types:
            print(f"  {t[0]}")
        print()
        
        # Check a few series records
        cur.execute("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE id IN (21, 49, 62, 68, 72, 78, 691)
            ORDER BY title
        """)
        
        series = cur.fetchall()
        print("Sample series records:")
        for series_id, title, poster_url in series:
            print(f"  ID {series_id}: {title}")
            print(f"    Poster: {poster_url}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_series_structure() 