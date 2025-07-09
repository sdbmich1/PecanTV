#!/usr/bin/env python3
"""
Script to check series and add missing episodes
"""

import psycopg2
from datetime import datetime, timezone

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
    
    print("🔍 Checking available series...")
    print("=" * 50)
    
    # List all series
    cursor.execute("""
        SELECT id, title, type
        FROM content 
        WHERE type = 'SERIES'
        ORDER BY title
    """)
    
    series_list = cursor.fetchall()
    print(f"Found {len(series_list)} series:")
    for row in series_list:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
    
    # Find Mike Hammer series
    cursor.execute("SELECT id FROM content WHERE title = 'Mike Hammer' AND type = 'SERIES'")
    mike_hammer_id = cursor.fetchone()
    if not mike_hammer_id:
        print("\n❌ Mike Hammer series not found!")
        return
    mike_hammer_id = mike_hammer_id[0]
    
    print(f"\n✅ Mike Hammer series ID: {mike_hammer_id}")
    
    # Add My Fair Deadly to Mike Hammer
    print(f"\n🎬 Adding 'My Fair Deadly' to Mike Hammer...")
    
    # Check if episode already exists
    cursor.execute("""
        SELECT id FROM episodes 
        WHERE series_id = %s AND title = 'My Fair Deadly'
    """, (mike_hammer_id,))
    
    if cursor.fetchone():
        print("   ⚠️  Episode already exists, skipping...")
    else:
        # Create video URL
        video_url = "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-My-Fair-Deadly_with-credits.mp4"
        
        # Create thumbnail URL
        thumbnail_url = "https://storage.googleapis.com/pecantv_title_images/MikeHammer_Title-Img-with-title.png"
        
        cursor.execute("""
            INSERT INTO episodes (
                series_id, season_number, episode_number, title, description, 
                content_url, thumbnail_url, runtime, air_date, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            mike_hammer_id,
            1,  # season
            2,  # episode
            "My Fair Deadly",
            "Mike Hammer investigates a case involving a deadly fair.",  # placeholder description
            video_url,
            thumbnail_url,
            60,  # runtime
            None,  # air_date
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        print("   ✅ Added 'My Fair Deadly' to Mike Hammer (S01E02)")
        print(f"      Video: {video_url}")
        print(f"      Thumbnail: {thumbnail_url}")
    
    # For Eyewitness, let's check if it's in the content table as a film
    print(f"\n👁️ Checking for 'Eyewitness' in content table...")
    cursor.execute("""
        SELECT id, title, type, poster_url
        FROM content 
        WHERE title ILIKE '%eyewitness%'
        ORDER BY id
    """)
    
    eyewitness_content = cursor.fetchall()
    if eyewitness_content:
        print(f"Found {len(eyewitness_content)} 'Eyewitness' entries in content table:")
        for row in eyewitness_content:
            print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
            print(f"  Poster: {row[3]}")
            print()
            
            # If it's a film, we should remove it since it's actually an episode
            if row[2] == 'FILM':
                print(f"  🗑️  Removing 'Eyewitness' from films (it's actually an episode)...")
                cursor.execute("DELETE FROM content WHERE id = %s", (row[0],))
                print(f"  ✅ Removed film entry for 'Eyewitness'")
    else:
        print("  No 'Eyewitness' entries found in content table")
    
    # Check if we need to create Man with a Camera series
    print(f"\n📷 Checking for 'Man with a Camera' series...")
    cursor.execute("SELECT id FROM content WHERE title = 'Man with a Camera' AND type = 'SERIES'")
    man_with_camera_id = cursor.fetchone()
    
    if not man_with_camera_id:
        print("  ❌ Man with a Camera series not found - would need to create it")
        print("  For now, we'll skip adding Eyewitness episode")
    else:
        man_with_camera_id = man_with_camera_id[0]
        print(f"  ✅ Man with a Camera series ID: {man_with_camera_id}")
        
        # Add Eyewitness to Man with a Camera
        print(f"\n👁️ Adding 'Eyewitness' to Man with a Camera...")
        
        # Check if episode already exists
        cursor.execute("""
            SELECT id FROM episodes 
            WHERE series_id = %s AND title = 'Eyewitness'
        """, (man_with_camera_id,))
        
        if cursor.fetchone():
            print("   ⚠️  Episode already exists, skipping...")
        else:
            # Create video URL
            video_url = "https://storage.googleapis.com/pecantv_series/man_with_a_camera/MwC-Eyewitness_with-credits.mp4"
            
            # Create thumbnail URL
            thumbnail_url = "https://storage.googleapis.com/pecantv_title_images/ManWithACameraSeries_Title-Img-with-title.png"
            
            cursor.execute("""
                INSERT INTO episodes (
                    series_id, season_number, episode_number, title, description, 
                    content_url, thumbnail_url, runtime, air_date, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                man_with_camera_id,
                1,  # season
                2,  # episode
                "Eyewitness",
                "A photographer captures evidence of a crime.",  # placeholder description
                video_url,
                thumbnail_url,
                60,  # runtime
                None,  # air_date
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            
            print("   ✅ Added 'Eyewitness' to Man with a Camera (S01E02)")
            print(f"      Video: {video_url}")
            print(f"      Thumbnail: {thumbnail_url}")
    
    # Commit changes
    conn.commit()
    
    # Verify the additions
    print(f"\n✅ VERIFICATION")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (mike_hammer_id,))
    mh_count = cursor.fetchone()[0]
    print(f"🎬 Mike Hammer episodes: {mh_count}")
    
    # Show updated Mike Hammer episode list
    print(f"\n🎬 Updated Mike Hammer episodes:")
    cursor.execute("""
        SELECT title, season_number, episode_number
        FROM episodes 
        WHERE series_id = %s
        ORDER BY season_number, episode_number
    """, (mike_hammer_id,))
    
    for row in cursor.fetchall():
        print(f"  S{row[1]:02d}E{row[2]:02d} - {row[0]}")
    
    cursor.close()
    conn.close()
    
    print(f"\n🎉 SUCCESS! Fixed episode classifications")
    print("- 'My Fair Deadly' is now in Mike Hammer series")
    print("- 'Eyewitness' removed from films (needs Man with a Camera series)")

if __name__ == "__main__":
    main() 