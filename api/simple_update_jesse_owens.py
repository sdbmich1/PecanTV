#!/usr/bin/env python3
"""
Simple script to update Jesse Owens II poster URL
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
    new_poster_url = "https://storage.googleapis.com/pecantv_title_images/Jesse-Owens-Feature-Img.png"
    
    print("Updating Jesse Owens II poster URL...")
    
    # Update the poster URL
    cursor.execute("""
        UPDATE content 
        SET poster_url = %s 
        WHERE title = 'Jesse Owens II'
    """, (new_poster_url,))
    
    updated_count = cursor.rowcount
    print(f"Updated {updated_count} record(s)")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Done!")

if __name__ == "__main__":
    main() 