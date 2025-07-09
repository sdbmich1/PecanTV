#!/usr/bin/env python3
import psycopg2

# Neon production database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL)

def check_longstreet_episodes():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, episode_number, content_url, description 
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Longstreet')
            ORDER BY episode_number
        """)
        episodes = cursor.fetchall()
        print(f"Found {len(episodes)} Longstreet episodes:")
        for episode in episodes:
            print(f"Episode {episode[2]}: {episode[1]}")
            print(f"  URL: {episode[3]}")
            description = episode[4] if episode[4] else "No description"
            print(f"  Description: {description[:100]}...")
            print()
    finally:
        cursor.close()
        conn.close()

def update_longstreet_episodes():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Longstreet episode URLs with correct GCS format
        episode_urls = {
            1: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-1_2p-1080-withCredits.mp4",
            2: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-2_2p-1080-withCredits.mp4",
            3: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-3_2p-1080-withCredits.mp4",
            4: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-4_2p-1080-withCredits.mp4",
            5: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-5_2p-1080-withCredits.mp4",
            6: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-6_2p-1080-withCredits.mp4",
            7: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-7_2p-1080-withCredits.mp4",
            8: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-8_2p-1080-withCredits.mp4",
            9: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-9_2p-1080-withCredits.mp4",
            10: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-10_2p-1080-withCredits.mp4",
            11: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-11_2p-1080-withCredits.mp4",
            12: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-12_2p-1080-withCredits.mp4",
            13: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-13_2p-1080-withCredits.mp4",
            14: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-14_2p-1080-withCredits.mp4",
            15: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-15_2p-1080-withCredits.mp4",
            16: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-16_2p-1080-withCredits.mp4",
            17: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-17_2p-1080-withCredits.mp4",
            18: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-18_2p-1080-withCredits.mp4",
            19: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-19_2p-1080-withCredits.mp4",
            20: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-20_2p-1080-withCredits.mp4",
            21: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-21_2p-1080-withCredits.mp4",
            22: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-22_2p-1080-withCredits.mp4",
            23: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-23_2p-1080-withCredits.mp4",
            24: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-24_2p-1080-withCredits.mp4",
            25: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-25_2p-1080-withCredits.mp4",
            26: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-26_2p-1080-withCredits.mp4",
            27: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-27_2p-1080-withCredits.mp4",
            28: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-28_2p-1080-withCredits.mp4",
            29: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-29_2p-1080-withCredits.mp4",
            30: "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet-Episode-30_2p-1080-withCredits.mp4"
        }
        
        series_id = cursor.execute("SELECT id FROM content WHERE title = 'Longstreet'").fetchone()[0]
        
        for episode_num, url in episode_urls.items():
            cursor.execute("""
                UPDATE episodes 
                SET content_url = %s 
                WHERE series_id = %s AND episode_number = %s
            """, (url, series_id, episode_num))
            print(f"Updated Episode {episode_num}: {url}")
        
        conn.commit()
        print(f"\n✅ Updated {len(episode_urls)} Longstreet episodes with correct GCS URLs")
        
    except Exception as e:
        print(f"Error updating episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Checking current Longstreet episodes...")
    check_longstreet_episodes()
    
    print("\nUpdating Longstreet episodes with correct GCS URLs...")
    update_longstreet_episodes()
    
    print("\nFinal check of updated episodes...")
    check_longstreet_episodes() 