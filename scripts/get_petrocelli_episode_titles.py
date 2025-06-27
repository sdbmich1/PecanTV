#!/usr/bin/env python3
"""
Script to fetch episode numbers and titles for Petrocelli episodes 8-22.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def get_episode_titles():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT episode_number, title
            FROM episodes
            WHERE series_id = (SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES')
            AND episode_number >= 8
            ORDER BY episode_number
        """)
        episodes = cur.fetchall()
        print("Petrocelli Episodes 8-22:")
        for ep in episodes:
            print(f"Episode {ep['episode_number']}: {ep['title']}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    get_episode_titles() 