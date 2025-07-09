#!/usr/bin/env python3
"""
Check the episodes table schema
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def check_episodes_schema():
    print("🔍 Checking episodes table schema...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Get table schema
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'episodes'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        
        print("\n📋 Episodes table columns:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")

        # Check one episode record
        print("\n📺 Sample episode record:")
        cur.execute("SELECT * FROM episodes WHERE series_id = 21 LIMIT 1")
        episode = cur.fetchone()
        if episode:
            print(f"  Episode data: {episode}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_episodes_schema() 