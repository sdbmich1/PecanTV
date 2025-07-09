#!/usr/bin/env python3
"""
Script to fix Mike Hammer episodes and add My Fair Deadly
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
    
    print("🔧 Fixing Mike Hammer episodes...")
    print("=" * 50)
    
    # Find Mike Hammer series
    cursor.execute("SELECT id FROM content WHERE title = 'Mike Hammer' AND type = 'SERIES'")
    mike_hammer_id = cursor.fetchone()
    if not mike_hammer_id:
        print("❌ Mike Hammer series not found!")
        return
    mike_hammer_id = mike_hammer_id[0]
    
    print(f"✅ Mike Hammer series ID: {mike_hammer_id}")
    
    # Check current episodes
    print(f"\n🎬 Current Mike Hammer episodes:")
    cursor.execute("""
        SELECT id, title, season_number, episode_number
        FROM episodes 
        WHERE series_id = %s
        ORDER BY season_number, episode_number
    """, (mike_hammer_id,))
    
    current_episodes = cursor.fetchall()
    for row in current_episodes:
        print(f"  S{row[2]:02d}E{row[3]:02d} - {row[1]} (ID: {row[0]})")
    
    # Check if My Fair Deadly already exists
    cursor.execute("""
        SELECT id, title, season_number, episode_number
        FROM episodes 
        WHERE series_id = %s AND title = 'My Fair Deadly'
    """, (mike_hammer_id,))
    
    my_fair_deadly = cursor.fetchone()
    if my_fair_deadly:
        print(f"\n✅ 'My Fair Deadly' already exists as S{my_fair_deadly[2]:02d}E{my_fair_deadly[3]:02d}")
        print("   No changes needed!")
    else:
        print(f"\n🎬 Adding 'My Fair Deadly' to Mike Hammer...")
        
        # Find the next available episode number
        cursor.execute("""
            SELECT MAX(episode_number) 
            FROM episodes 
            WHERE series_id = %s AND season_number = 1
        """, (mike_hammer_id,))
        
        max_episode = cursor.fetchone()[0]
        next_episode = (max_episode or 0) + 1
        
        print(f"   Next available episode number: {next_episode}")
        
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
            next_episode,  # episode
            "My Fair Deadly",
            "Mike Hammer investigates a case involving a deadly fair.",  # placeholder description
            video_url,
            thumbnail_url,
            60,  # runtime
            None,  # air_date
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        print(f"   ✅ Added 'My Fair Deadly' to Mike Hammer (S01E{next_episode:02d})")
        print(f"      Video: {video_url}")
        print(f"      Thumbnail: {thumbnail_url}")
    
    # Check for Eyewitness in content table
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
    
    # Check for Man with a Camera series (note: it's "Man With a Camera" not "Man with a Camera")
    print(f"\n📷 Checking for 'Man With a Camera' series...")
    cursor.execute("SELECT id FROM content WHERE title = 'Man With a Camera' AND type = 'SERIES'")
    man_with_camera_id = cursor.fetchone()
    
    if not man_with_camera_id:
        print("  ❌ Man With a Camera series not found")
    else:
        man_with_camera_id = man_with_camera_id[0]
        print(f"  ✅ Man With a Camera series ID: {man_with_camera_id}")
        
        # Check current episodes
        cursor.execute("""
            SELECT id, title, season_number, episode_number
            FROM episodes 
            WHERE series_id = %s
            ORDER BY season_number, episode_number
        """, (man_with_camera_id,))
        
        mwc_episodes = cursor.fetchall()
        print(f"  Current Man With a Camera episodes: {len(mwc_episodes)}")
        for row in mwc_episodes:
            print(f"    S{row[2]:02d}E{row[3]:02d} - {row[1]}")
        
        # Check if Eyewitness already exists
        cursor.execute("""
            SELECT id, title, season_number, episode_number
            FROM episodes 
            WHERE series_id = %s AND title = 'Eyewitness'
        """, (man_with_camera_id,))
        
        eyewitness_episode = cursor.fetchone()
        if eyewitness_episode:
            print(f"  ✅ 'Eyewitness' already exists as S{eyewitness_episode[2]:02d}E{eyewitness_episode[3]:02d}")
        else:
            print(f"  👁️ Adding 'Eyewitness' to Man With a Camera...")
            
            # Find the next available episode number
            cursor.execute("""
                SELECT MAX(episode_number) 
                FROM episodes 
                WHERE series_id = %s AND season_number = 1
            """, (man_with_camera_id,))
            
            max_episode = cursor.fetchone()[0]
            next_episode = (max_episode or 0) + 1
            
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
                next_episode,  # episode
                "Eyewitness",
                "A photographer captures evidence of a crime.",  # placeholder description
                video_url,
                thumbnail_url,
                60,  # runtime
                None,  # air_date
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            
            print(f"  ✅ Added 'Eyewitness' to Man With a Camera (S01E{next_episode:02d})")
    
    # Commit changes
    conn.commit()
    
    # Final verification
    print(f"\n✅ FINAL VERIFICATION")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (mike_hammer_id,))
    mh_count = cursor.fetchone()[0]
    print(f"🎬 Mike Hammer episodes: {mh_count}")
    
    print(f"\n🎬 Final Mike Hammer episodes:")
    cursor.execute("""
        SELECT title, season_number, episode_number
        FROM episodes 
        WHERE series_id = %s
        ORDER BY season_number, episode_number
    """, (mike_hammer_id,))
    
    for row in cursor.fetchall():
        print(f"  S{row[1]:02d}E{row[2]:02d} - {row[0]}")
    
    if man_with_camera_id:
        cursor.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (man_with_camera_id,))
        mwc_count = cursor.fetchone()[0]
        print(f"\n📷 Man With a Camera episodes: {mwc_count}")
        
        print(f"\n📷 Final Man With a Camera episodes:")
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
    
    print(f"\n🎉 SUCCESS! Fixed episode classifications")
    print("- 'My Fair Deadly' added to Mike Hammer series")
    print("- 'Eyewitness' removed from films and added to Man With a Camera series")

if __name__ == "__main__":
    main() 