#!/usr/bin/env python3
"""
Script to update Dragnet Animated - Episode % rows to type EPISODE in the Neon database.
"""

import psycopg2

# Database connection parameters for Neon
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_dragnet_animated_episodes():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        print("🔍 Finding Dragnet Animated - Episode % rows...")
        cur.execute("""
            SELECT id, title, type, series_name
            FROM content
            WHERE title ILIKE 'Dragnet Animated - Episode %' AND series_name = 'Dragnet';
        """)
        rows = cur.fetchall()
        print(f"Found {len(rows)} rows to update.")
        for row in rows:
            print(f"   ID {row[0]}: {row[1]} (was {row[2]})")
        if not rows:
            print("No rows found to update.")
            return
        # Update the type to EPISODE
        cur.execute("""
            UPDATE content
            SET type = 'EPISODE'
            WHERE title ILIKE 'Dragnet Animated - Episode %' AND series_name = 'Dragnet';
        """)
        conn.commit()
        print(f"✅ Updated {len(rows)} rows to type EPISODE.")
        # Show the updated rows
        cur.execute("""
            SELECT id, title, type, series_name
            FROM content
            WHERE title ILIKE 'Dragnet Animated - Episode %' AND series_name = 'Dragnet';
        """)
        updated = cur.fetchall()
        print("\nUpdated rows:")
        for row in updated:
            print(f"   ID {row[0]}: {row[1]} (now {row[2]})")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_dragnet_animated_episodes() 