#!/usr/bin/env python3
"""
Script to search for entries with 'animated' in title
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
    
    print("Searching for entries with 'animated' in title...")
    
    # Search for entries with animated
    cursor.execute("""
        SELECT id, title, type, created_at
        FROM content 
        WHERE title ILIKE '%animated%'
        ORDER BY id
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print("No entries found with 'animated' in title")
        return
    
    print(f"Found {len(results)} entries:")
    for row in results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}, Created: {row[3]}")
    
    # Check for duplicates
    titles = [row[1].lower() for row in results]
    unique_titles = set(titles)
    
    if len(titles) > len(unique_titles):
        print(f"\nFound potential duplicates! {len(titles)} total entries, {len(unique_titles)} unique titles")
        
        # Group by title
        title_groups = {}
        for row in results:
            title = row[1].lower()
            if title not in title_groups:
                title_groups[title] = []
            title_groups[title].append(row)
        
        for title, entries in title_groups.items():
            if len(entries) > 1:
                print(f"\nDuplicate entries for '{title}':")
                for entry in entries:
                    print(f"  ID: {entry[0]}, Title: '{entry[1]}', Type: {entry[2]}")
    else:
        print("No duplicates found")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Done!")

if __name__ == "__main__":
    main() 