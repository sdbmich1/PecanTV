#!/usr/bin/env python3
"""
Debug script to check series_id=21 and its episodes
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def debug_series_21():
    print("🔍 Debugging series_id=21...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Check content table for id=21
        print("\n📋 Content table (id=21):")
        cur.execute("SELECT id, title, type, poster_url FROM content WHERE id = 21")
        content = cur.fetchone()
        if content:
            print(f"  ID: {content[0]}")
            print(f"  Title: {content[1]}")
            print(f"  Type: {content[2]}")
            print(f"  Poster: {content[3]}")
        else:
            print("  ❌ No content found with id=21")

        # Check episodes table for series_id=21
        print("\n📺 Episodes table (series_id=21):")
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = 21")
        episode_count = cur.fetchone()[0]
        print(f"  Total episodes: {episode_count}")

        if episode_count > 0:
            cur.execute("SELECT episode_number, title, content_url FROM episodes WHERE series_id = 21 ORDER BY episode_number LIMIT 5")
            episodes = cur.fetchall()
            for ep in episodes:
                print(f"  S1E{ep[0]}: {ep[1]}")

        # Check for any null values in episodes
        print("\n🔍 Checking for null values in episodes (series_id=21):")
        cur.execute("""
            SELECT column_name, COUNT(*) 
            FROM episodes e
            CROSS JOIN information_schema.columns c
            WHERE c.table_name = 'episodes' 
            AND e.series_id = 21
            AND e.id IS NOT NULL
            GROUP BY column_name
        """)
        # This is a simplified check - let's check specific fields
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(title) as title_count,
                COUNT(content_url) as url_count,
                COUNT(poster_url) as poster_count
            FROM episodes 
            WHERE series_id = 21
        """)
        null_check = cur.fetchone()
        print(f"  Total episodes: {null_check[0]}")
        print(f"  Episodes with title: {null_check[1]}")
        print(f"  Episodes with content_url: {null_check[2]}")
        print(f"  Episodes with poster_url: {null_check[3]}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_series_21() 