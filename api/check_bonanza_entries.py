#!/usr/bin/env python3
"""
Script to check for Bonanza entries in the database
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
    
    print("Checking for Bonanza entries in the database...")
    
    # Check content table
    cursor.execute("""
        SELECT id, title, poster_url, type
        FROM content 
        WHERE title ILIKE '%bonanza%'
        ORDER BY id
    """)
    
    content_results = cursor.fetchall()
    
    print(f"\nFound {len(content_results)} Bonanza entries in content table:")
    for row in content_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[3]}")
        print(f"  Poster: {row[2] if row[2] else 'NULL'}")
    
    # Check series table
    cursor.execute("""
        SELECT id, title, poster_url
        FROM series 
        WHERE title ILIKE '%bonanza%'
        ORDER BY id
    """)
    
    series_results = cursor.fetchall()
    
    print(f"\nFound {len(series_results)} Bonanza entries in series table:")
    for row in series_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}'")
        print(f"  Poster: {row[2] if row[2] else 'NULL'}")
    
    # Check episodes table
    cursor.execute("""
        SELECT id, title, poster_url, series_id
        FROM episodes 
        WHERE title ILIKE '%bonanza%'
        ORDER BY id
    """)
    
    episode_results = cursor.fetchall()
    
    print(f"\nFound {len(episode_results)} Bonanza entries in episodes table:")
    for row in episode_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Series ID: {row[3]}")
        print(f"  Poster: {row[2] if row[2] else 'NULL'}")
    
    cursor.close()
    conn.close()
    
    print("\nDone!")

if __name__ == "__main__":
    main() 