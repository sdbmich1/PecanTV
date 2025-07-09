#!/usr/bin/env python3
"""
Script to update the poster URLs for Hercules films
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
    
    # Hercules film poster URLs
    hercules_posters = {
        "Hercules Against the Moon Men": "https://storage.googleapis.com/pecantv_title_images/Hercules-against-the-Moon-Men_Title-Img.png",
        "Hercules in the Haunted World": "https://storage.googleapis.com/pecantv_title_images/Hercules-in-the-Haunted-World_Title-Img.png"
    }
    
    print("Looking for Hercules film entries...")
    
    # Find Hercules entries
    cursor.execute("""
        SELECT id, title, poster_url, type
        FROM content 
        WHERE title ILIKE '%hercules%' AND type = 'FILM'
        ORDER BY id
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print("No Hercules film entries found")
        return
    
    print(f"Found {len(results)} Hercules film entries:")
    for row in results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[3]}")
        print(f"  Current Poster: {row[2] if row[2] else 'NULL'}")
    
    # Update each Hercules film poster
    updated_count = 0
    for title, poster_url in hercules_posters.items():
        cursor.execute("""
            UPDATE content 
            SET poster_url = %s 
            WHERE title ILIKE %s AND type = 'FILM'
        """, (poster_url, f"%{title}%"))
        
        if cursor.rowcount > 0:
            print(f"\n✅ Updated '{title}' with poster: {poster_url}")
            updated_count += cursor.rowcount
        else:
            print(f"\n❌ No match found for '{title}'")
    
    # Verify the updates
    cursor.execute("""
        SELECT id, title, poster_url, type
        FROM content 
        WHERE title ILIKE '%hercules%' AND type = 'FILM'
        ORDER BY id
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
    
    print(f"\nDone! Updated {updated_count} Hercules film(s)")

if __name__ == "__main__":
    main() 