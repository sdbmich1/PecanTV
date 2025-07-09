#!/usr/bin/env python3
import psycopg2

DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT id, title, poster_url FROM content WHERE id = 82 AND title = 'Count Duckula'")
    row = cur.fetchone()
    if row:
        print(f"ID: {row[0]}, Title: {row[1]}, Poster URL: {row[2]}")
    else:
        print("Count Duckula not found.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main() 