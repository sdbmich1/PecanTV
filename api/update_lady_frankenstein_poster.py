#!/usr/bin/env python3
"""
Script to update the poster URL for Lady Frankenstein
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
    
    # New poster URL
    new_poster_url = "https://storage.googleapis.com/pecantv_title_images/Lady-Frankenstein_Title-Img.png"
    
    print("Looking for Lady Frankenstein entries...")
    
    # First, let's find Lady Frankenstein entries
    cursor.execute("""
        SELECT id, title, poster_url, type
        FROM content 
        WHERE title ILIKE '%lady frankenstein%'
        ORDER BY id
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print("No entries found with 'Lady Frankenstein' in title")
        return
    
    print(f"Found {len(results)} Lady Frankenstein entries:")
    for row in results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[3]}")
        print(f"  Current Poster: {row[2] if row[2] else 'NULL'}")
    
    # Update the poster URL for Lady Frankenstein
    cursor.execute("""
        UPDATE content 
        SET poster_url = %s 
        WHERE title ILIKE '%lady frankenstein%'
    """, (new_poster_url,))
    
    updated_count = cursor.rowcount
    print(f"\nUpdated {updated_count} record(s)")
    
    # Verify the update
    cursor.execute("""
        SELECT id, title, poster_url, type
        FROM content 
        WHERE title ILIKE '%lady frankenstein%'
    """)
    
    updated_results = cursor.fetchall()
    print("\nAfter update:")
    for row in updated_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[3]}")
        print(f"  New Poster: {row[2]}")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\nDone!")

if __name__ == "__main__":
    main() 