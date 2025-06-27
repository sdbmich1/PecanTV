#!/usr/bin/env python3
"""
Script to check the structure of the content table.
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

def check_table_structure():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get column information for content table
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'content' 
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("📋 Content table structure:")
        print("=" * 40)
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
        
        # Also check episodes table
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'episodes' 
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\n📋 Episodes table structure:")
        print("=" * 40)
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_table_structure() 