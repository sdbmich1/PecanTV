#!/usr/bin/env python3
"""
Script to check Mike Hammer episodes in the database
"""

import psycopg2

def main():
    # Database connection
    conn = psycopg2.connect(
        host='localhost',
        database='pecantv',
        user='postgres',
        password='postgres',
        port='5433'
    )
    
    cursor = conn.cursor()
    
    print("Checking Mike Hammer episodes in the database...")
    
    # Check content table for Mike Hammer series
    cursor.execute("""
        SELECT id, title, type
        FROM content 
        WHERE title ILIKE '%mike hammer%'
        ORDER BY id
    """)
    
    content_results = cursor.fetchall()
    
    print(f"\nFound {len(content_results)} Mike Hammer entries in content table:")
    for row in content_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
    
    # Check episodes table for Mike Hammer episodes
    cursor.execute("""
        SELECT e.id, e.title, e.content_url, e.series_id, c.title as series_title
        FROM episodes e
        JOIN content c ON e.series_id = c.id
        WHERE c.title ILIKE '%mike hammer%'
        ORDER BY e.id
    """)
    
    episode_results = cursor.fetchall()
    
    print(f"\nFound {len(episode_results)} Mike Hammer episodes in episodes table:")
    for row in episode_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Series: {row[4]}")
        print(f"  Video URL: {row[2] if row[2] else 'NULL'}")
    
    cursor.close()
    conn.close()
    
    print("\nDone!")

if __name__ == "__main__":
    main() 