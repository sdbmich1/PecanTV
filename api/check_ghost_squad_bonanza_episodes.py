#!/usr/bin/env python3
"""
Script to check Ghost Squad and Bonanza episodes in the database
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
    
    print("Checking Ghost Squad and Bonanza episodes in the database...")
    
    # Check content table for both series
    cursor.execute("""
        SELECT id, title, type
        FROM content 
        WHERE title ILIKE '%ghost squad%' OR title ILIKE '%bonanza%'
        ORDER BY title, id
    """)
    
    content_results = cursor.fetchall()
    
    print(f"\nFound {len(content_results)} entries in content table:")
    for row in content_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
    
    # Check episodes table for both series
    cursor.execute("""
        SELECT e.id, e.title, e.series_id, c.title as series_title, e.episode_number, e.content_url
        FROM episodes e
        JOIN content c ON e.series_id = c.id
        WHERE c.title ILIKE '%ghost squad%' OR c.title ILIKE '%bonanza%'
        ORDER BY c.title, e.episode_number
    """)
    
    episode_results = cursor.fetchall()
    
    print(f"\nFound {len(episode_results)} episodes:")
    for row in episode_results:
        print(f"  Episode ID: {row[0]}, Title: '{row[1]}', Series: '{row[3]}', Episode #: {row[4]}")
        print(f"    Content URL: {row[5]}")
    
    # Check if there are any episodes that should be moved to episodes table
    cursor.execute("""
        SELECT id, title, type, poster_url, content_url
        FROM content 
        WHERE (title ILIKE '%ghost squad%' OR title ILIKE '%bonanza%') 
        AND type = 'SERIES'
        ORDER BY title, id
    """)
    
    series_results = cursor.fetchall()
    
    print(f"\nSeries entries:")
    for row in series_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
        print(f"    Poster: {row[3]}")
        print(f"    Content URL: {row[4]}")
    
    # Check for any content that might be episodes but not properly categorized
    cursor.execute("""
        SELECT id, title, type, poster_url, content_url
        FROM content 
        WHERE (title ILIKE '%ghost squad%' OR title ILIKE '%bonanza%') 
        AND type != 'SERIES'
        ORDER BY title, id
    """)
    
    other_content_results = cursor.fetchall()
    
    if other_content_results:
        print(f"\nOther content entries (might be episodes):")
        for row in other_content_results:
            print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
            print(f"    Poster: {row[3]}")
            print(f"    Content URL: {row[4]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main() 