#!/usr/bin/env python3
import psycopg2

# Neon production database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL)

def check_longstreet_series():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Check if Longstreet series exists
        cursor.execute("""
            SELECT id, title, type, description 
            FROM content 
            WHERE title ILIKE '%longstreet%'
        """)
        
        series = cursor.fetchall()
        print(f"Found {len(series)} series matching 'Longstreet':")
        for s in series:
            print(f"ID: {s[0]}, Title: {s[1]}, Type: {s[2]}")
            print(f"Description: {s[3]}")
            print()
        
        # Check all series to see what's there
        cursor.execute("""
            SELECT id, title, type 
            FROM content 
            WHERE type = 'SERIES'
            ORDER BY title
        """)
        
        all_series = cursor.fetchall()
        print(f"All series in database ({len(all_series)} total):")
        for s in all_series:
            print(f"ID: {s[0]}, Title: {s[1]}, Type: {s[2]}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_longstreet_series() 