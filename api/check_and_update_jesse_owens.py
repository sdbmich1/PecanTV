#!/usr/bin/env python3
"""
Simple script to check and update Jesse Owens II poster
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'database': 'pecantv',
        'user': 'postgres',
        'password': 'postgres',
        'port': '5433'
    }
    
    # New poster URL
    new_poster_url = "https://storage.googleapis.com/pecantv_title_images/Jesse-Owens-Feature-Img.png"
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check Jesse Owens II
        cursor.execute("""
            SELECT id, title, poster_url, trailer_url, content_url, description, type
            FROM content WHERE title ILIKE '%Jesse Owens II%'
        """)
        
        results = cursor.fetchall()
        print(f"Found {len(results)} Jesse Owens II records:")
        for row in results:
            print(f"  ID: {row[0]}, Title: {row[1]}, Poster: '{row[2]}', Type: {row[6]}")
        
        if results:
            # Update the poster URL
            cursor.execute("""
                UPDATE content 
                SET poster_url = %s 
                WHERE title ILIKE '%Jesse Owens II%'
            """, (new_poster_url,))
            
            updated_count = cursor.rowcount
            print(f"\nUpdated {updated_count} record(s)")
            
            # Verify the update
            cursor.execute("""
                SELECT id, title, poster_url, type
                FROM content WHERE title ILIKE '%Jesse Owens II%'
            """)
            
            updated_results = cursor.fetchall()
            print("\nAfter update:")
            for row in updated_results:
                print(f"  ID: {row[0]}, Title: {row[1]}, Poster: {row[2]}, Type: {row[3]}")
        
        # Commit the changes
        conn.commit()
        print("\nChanges committed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    main() 