#!/usr/bin/env python3
"""
Script to check Lady Frankenstein poster URL
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
    
    print("Checking Lady Frankenstein poster URL...")
    
    # Check Lady Frankenstein entry
    cursor.execute("""
        SELECT id, title, poster_url, type
        FROM content 
        WHERE title ILIKE '%lady frankenstein%'
    """)
    
    results = cursor.fetchall()
    
    if results:
        for row in results:
            print(f"ID: {row[0]}")
            print(f"Title: '{row[1]}'")
            print(f"Type: {row[3]}")
            print(f"Poster URL: {row[2]}")
            
            if row[2] and "Lady-Frankenstein_Title-Img.png" in row[2]:
                print("✅ Poster URL is already correct!")
            else:
                print("❌ Poster URL needs updating")
    else:
        print("No Lady Frankenstein entries found")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("Done!")

if __name__ == "__main__":
    main() 