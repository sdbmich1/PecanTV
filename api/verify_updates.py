#!/usr/bin/env python3
"""
Script to verify the updates made
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
    
    print("=== VERIFICATION REPORT ===\n")
    
    # Check Jesse Owens II
    print("1. Jesse Owens II Poster Update:")
    cursor.execute("""
        SELECT id, title, poster_url, type
        FROM content 
        WHERE title ILIKE '%Jesse Owens II%'
    """)
    
    jesse_results = cursor.fetchall()
    if jesse_results:
        for row in jesse_results:
            print(f"   ID: {row[0]}, Title: '{row[1]}'")
            print(f"   Poster URL: {row[2]}")
            print(f"   Type: {row[3]}")
            if row[2] and "Jesse-Owens-Feature-Img.png" in row[2]:
                print("   ✅ Poster URL updated successfully!")
            else:
                print("   ❌ Poster URL not updated correctly")
    else:
        print("   ❌ Jesse Owens II not found")
    
    print("\n2. Snake and Crane Duplicate Check:")
    cursor.execute("""
        SELECT id, title, type
        FROM content 
        WHERE title ILIKE '%snake%' AND title ILIKE '%crane%'
        ORDER BY id
    """)
    
    snake_results = cursor.fetchall()
    if snake_results:
        print(f"   Found {len(snake_results)} entries with 'snake' and 'crane':")
        for row in snake_results:
            print(f"   ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
        
        if len(snake_results) == 1:
            print("   ✅ Only one entry found - no duplicates")
        else:
            print(f"   ⚠️  Found {len(snake_results)} entries - potential duplicates")
    else:
        print("   ✅ No entries found with 'snake' and 'crane'")
    
    # Check for any entries with "animate movie"
    print("\n3. Animate Movie Entries Check:")
    cursor.execute("""
        SELECT id, title, type
        FROM content 
        WHERE title ILIKE '%animate movie%'
        ORDER BY id
    """)
    
    animate_results = cursor.fetchall()
    if animate_results:
        print(f"   Found {len(animate_results)} entries with 'animate movie':")
        for row in animate_results:
            print(f"   ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
    else:
        print("   ✅ No entries found with 'animate movie'")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    main() 