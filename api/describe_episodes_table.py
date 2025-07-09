#!/usr/bin/env python3
"""
Script to print the schema of the episodes table.
"""
import psycopg2

def main():
    conn = psycopg2.connect(
        host='localhost',
        database='pecantv',
        user='postgres',
        password='postgres',
        port='5433'
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'episodes'
        ORDER BY ordinal_position
    """)
    rows = cur.fetchall()
    print("episodes table columns:")
    for name, dtype in rows:
        print(f"  {name}: {dtype}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main() 