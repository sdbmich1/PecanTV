#!/usr/bin/env python3
"""
Script to update the poster URL for Jesse Owens II
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_jesse_owens_ii_poster():
    """Update the poster URL for Jesse Owens II"""
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'pecantv'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'port': os.getenv('DB_PORT', '5433')
    }
    
    # New poster URL
    new_poster_url = "https://storage.googleapis.com/pecantv_title_images/Jesse-Owens-Feature-Img.png"
    
    conn = None
    cursor = None
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # First, let's check if Jesse Owens II exists in the content table
        cursor.execute("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE title ILIKE '%Jesse Owens II%'
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No content found with title containing 'Jesse Owens II'")
            return
        
        print(f"Found {len(results)} content items:")
        for row in results:
            poster_url = row[2] if row[2] else "NULL"
            print(f"  ID: {row[0]}, Title: {row[1]}, Current Poster: {poster_url}")
        
        # Update the poster URL for Jesse Owens II
        cursor.execute("""
            UPDATE content 
            SET poster_url = %s 
            WHERE title ILIKE '%Jesse Owens II%'
        """, (new_poster_url,))
        
        updated_count = cursor.rowcount
        
        if updated_count > 0:
            print(f"Successfully updated poster URL for {updated_count} content item(s)")
            
            # Verify the update
            cursor.execute("""
                SELECT id, title, poster_url 
                FROM content 
                WHERE title ILIKE '%Jesse Owens II%'
            """)
            
            updated_results = cursor.fetchall()
            print("\nUpdated content:")
            for row in updated_results:
                poster_url = row[2] if row[2] else "NULL"
                print(f"  ID: {row[0]}, Title: {row[1]}, New Poster: {poster_url}")
        else:
            print("No content was updated")
        
        # Commit the changes
        conn.commit()
        print("Changes committed successfully")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
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
    update_jesse_owens_ii_poster() 