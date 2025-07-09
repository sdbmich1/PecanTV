#!/usr/bin/env python3
"""
Test Petrocelli episodes database query directly
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def test_petrocelli_query():
    print("🔍 Testing Petrocelli episodes query directly...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Test the exact query that the API uses
        print("\n1. Checking content table for id=21:")
        cur.execute("SELECT id, title, type FROM content WHERE id = 21")
        content = cur.fetchone()
        if content:
            print(f"  ✅ Found: ID={content[0]}, Title='{content[1]}', Type='{content[2]}'")
        else:
            print("  ❌ No content found with id=21")
            return

        print("\n2. Checking episodes for series_id=21:")
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = 21")
        count = cur.fetchone()[0]
        print(f"  Found {count} episodes")

        if count > 0:
            print("\n3. Testing episode data retrieval:")
            cur.execute("""
                SELECT id, title, season_number, episode_number, content_url, thumbnail_url
                FROM episodes 
                WHERE series_id = 21 
                ORDER BY episode_number 
                LIMIT 3
            """)
            episodes = cur.fetchall()
            for ep in episodes:
                print(f"  Episode {ep[0]}: S{ep[2]}E{ep[3]} - {ep[1]}")
                print(f"    URL: {ep[4]}")
                print(f"    Thumbnail: {ep[5]}")

        print("\n4. Testing with the exact API query:")
        cur.execute("""
            SELECT e.*, c.title as series_title
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE e.series_id = 21
            ORDER BY e.episode_number
            LIMIT 5
        """)
        episodes = cur.fetchall()
        print(f"  Retrieved {len(episodes)} episodes successfully")

        cur.close()
        conn.close()
        print("\n✅ Database queries working fine!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_petrocelli_query() 