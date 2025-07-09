#!/usr/bin/env python3
"""
Script to add missing episodes: My Fair Deadly (Mike Hammer) and Eyewitness (Man with a Camera)
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
    
    print("🔧 Adding missing episodes to their correct series...")
    print("=" * 60)
    
    # Find series IDs
    cursor.execute("SELECT id FROM content WHERE title = 'Mike Hammer' AND type = 'SERIES'")
    mike_hammer_id = cursor.fetchone()
    if not mike_hammer_id:
        print("❌ Mike Hammer series not found!")
        return
    mike_hammer_id = mike_hammer_id[0]
    
    cursor.execute("SELECT id FROM content WHERE title = 'Man with a Camera' AND type = 'SERIES'")
    man_with_camera_id = cursor.fetchone()
    if not man_with_camera_id:
        print("❌ Man with a Camera series not found!")
        return
    man_with_camera_id = man_with_camera_id[0]
    
    print(f"✅ Mike Hammer series ID: {mike_hammer_id}")
    print(f"✅ Man with a Camera series ID: {man_with_camera_id}")
    
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
    
    cursor.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (man_with_camera_id,))
    mwc_count = cursor.fetchone()[0]
    print(f"📷 Man with a Camera episodes: {mwc_count}")
    
    # Show updated episode lists
    print(f"\n🎬 Updated Mike Hammer episodes:")
    cursor.execute("""
        SELECT title, season_number, episode_number
        FROM episodes 
        WHERE series_id = %s
        ORDER BY season_number, episode_number
    """, (mike_hammer_id,))
    
    for row in cursor.fetchall():
        print(f"  S{row[1]:02d}E{row[2]:02d} - {row[0]}")
    
    print(f"\n📷 Updated Man with a Camera episodes:")
    cursor.execute("""
        SELECT title, season_number, episode_number
        FROM episodes 
        WHERE series_id = %s
        ORDER BY season_number, episode_number
    """, (man_with_camera_id,))
    
    for row in cursor.fetchall():
        print(f"  S{row[1]:02d}E{row[2]:02d} - {row[0]}")
    
    cursor.close()
    conn.close()
    
    print(f"\n🎉 SUCCESS! Added missing episodes to their correct series")
    print("The episodes should now appear in their proper series carousels!")

if __name__ == "__main__":
    main() 