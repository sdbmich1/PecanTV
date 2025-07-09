#!/usr/bin/env python3
"""
Script to remove duplicate 'snake and crane secret: the animate movie'
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
    
    print("Looking for 'snake and crane secret: the animate movie' entries...")
    
    # Find all entries with this title
    cursor.execute("""
        SELECT id, title, poster_url, trailer_url, content_url, type, created_at
        FROM content 
        WHERE title ILIKE '%snake and crane secret%animate movie%'
        ORDER BY id
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print("No entries found with 'snake and crane secret: the animate movie'")
        return
    
    print(f"Found {len(results)} entries:")
    for row in results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[5]}, Created: {row[6]}")
    
    if len(results) > 1:
        # Keep the first one (lowest ID), remove the rest
        ids_to_remove = [row[0] for row in results[1:]]
        
        print(f"\nRemoving {len(ids_to_remove)} duplicate entries with IDs: {ids_to_remove}")
        
        # Remove the duplicates
        cursor.execute("""
            DELETE FROM content 
            WHERE id = ANY(%s)
        """, (ids_to_remove,))
        
        deleted_count = cursor.rowcount
        print(f"Deleted {deleted_count} duplicate entries")
        
        # Verify the remaining entry
        cursor.execute("""
            SELECT id, title, poster_url, trailer_url, content_url, type
            FROM content 
            WHERE title ILIKE '%snake and crane secret%animate movie%'
        """)
        
        remaining = cursor.fetchall()
        print(f"\nRemaining entry:")
        for row in remaining:
            print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[5]}")
    else:
        print("Only one entry found - no duplicates to remove")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Done!")

if __name__ == "__main__":
    main() 