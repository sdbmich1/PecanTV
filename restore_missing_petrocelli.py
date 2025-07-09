#!/usr/bin/env python3
"""
Restore missing Petrocelli episodes 14-22
"""

import psycopg2
from datetime import datetime, timezone

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

# Petrocelli episodes 14-22 with titles and content URLs
PETROCELLI_EPISODES_14_22 = [
    (14, "A Covenant with Evil", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli14_2p-1080-wCredits.mp4"),
    (15, "The Golden Fleece", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli15_2p-1080-wCredits.mp4"),
    (16, "The Day of the Dragon", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli16_2p-1080-wCredits.mp4"),
    (17, "The Golden Cage", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli17_2p-1080-wCredits.mp4"),
    (18, "The Fatal Impulse", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli18_2p-1080-wCredits.mp4"),
    (19, "The Fatal Impulse", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli19_2p-1080-wCredits.mp4"),
    (20, "The Fatal Impulse", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli20_2p-1080-wCredits.mp4"),
    (21, "The Fatal Impulse", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli21_2p-1080-wCredits.mp4"),
    (22, "The Fatal Impulse", "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli22_2p-1080-wCredits.mp4"),
]

def restore_missing_episodes():
    print("🔧 Restoring missing Petrocelli episodes 14-22...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Check which episodes already exist
        cur.execute("SELECT episode_number FROM episodes WHERE series_id = 21")
        existing_episodes = [row[0] for row in cur.fetchall()]
        
        added_count = 0
        for episode_num, title, content_url in PETROCELLI_EPISODES_14_22:
            if episode_num not in existing_episodes:
                # Insert the episode
                cur.execute("""
                    INSERT INTO episodes (series_id, season_number, episode_number, title, content_url, thumbnail_url, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    21,  # series_id for Petrocelli
                    1,   # season_number
                    episode_num,
                    title,
                    content_url,
                    f"https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli{episode_num}_poster.jpg",
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                print(f"  ✅ Added S1E{episode_num}: {title}")
                added_count += 1
            else:
                print(f"  ⏭️  S1E{episode_num} already exists")
        
        conn.commit()
        print(f"\n🎉 Successfully added {added_count} missing episodes!")
        
        # Verify total count
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = 21")
        total_episodes = cur.fetchone()[0]
        print(f"📊 Total Petrocelli episodes: {total_episodes}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    restore_missing_episodes() 