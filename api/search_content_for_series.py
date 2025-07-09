#!/usr/bin/env python3
"""
Script to search content table for Bonanza and Ghost Squad entries
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
    
    print("Searching content table for Bonanza and Ghost Squad entries...")
    
    # First, let's see the structure of the content table
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'content' 
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"\nContent table columns:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    # Search for any content with Bonanza or Ghost Squad in any text field
    cursor.execute("""
        SELECT id, title, type, poster_url, content_url, description, 
               genre_id, rating_id, release_date, created_at, updated_at
        FROM content 
        WHERE title ILIKE '%bonanza%' 
           OR title ILIKE '%ghost squad%'
           OR title ILIKE '%ghostsquad%'
           OR (description IS NOT NULL AND description ILIKE '%bonanza%')
           OR (description IS NOT NULL AND description ILIKE '%ghost squad%')
           OR (description IS NOT NULL AND description ILIKE '%ghostsquad%')
        ORDER BY title, id
    """)
    
    results = cursor.fetchall()
    
    print(f"\nFound {len(results)} entries matching Bonanza or Ghost Squad:")
    for row in results:
        print(f"\n  ID: {row[0]}")
        print(f"  Title: '{row[1]}'")
        print(f"  Type: {row[2]}")
        print(f"  Poster URL: {row[3]}")
        print(f"  Content URL: {row[4]}")
        print(f"  Description: {row[5][:100] if row[5] else 'None'}...")
        print(f"  Genre ID: {row[6]}")
        print(f"  Rating ID: {row[7]}")
        print(f"  Release Date: {row[8]}")
        print(f"  Created: {row[9]}")
        print(f"  Updated: {row[10]}")
    
    # Also check if there are any episodes that might be miscategorized
    cursor.execute("""
        SELECT id, title, type, poster_url, content_url, description, 
               genre_id, rating_id, release_date
        FROM content 
        WHERE type != 'SERIES' 
        AND (title ILIKE '%bonanza%' 
             OR title ILIKE '%ghost squad%'
             OR title ILIKE '%ghostsquad%')
        ORDER BY title, id
    """)
    
    miscategorized = cursor.fetchall()
    
    if miscategorized:
        print(f"\nFound {len(miscategorized)} potentially miscategorized entries:")
        for row in miscategorized:
            print(f"\n  ID: {row[0]}")
            print(f"  Title: '{row[1]}'")
            print(f"  Type: {row[2]}")
            print(f"  Content URL: {row[4]}")
            print(f"  Description: {row[5][:100] if row[5] else 'None'}...")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main() 