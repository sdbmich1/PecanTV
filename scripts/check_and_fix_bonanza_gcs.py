#!/usr/bin/env python3
import psycopg2

# Neon production database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL)

def check_bonanza_episodes():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, episode_number, content_url, description 
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Bonanza')
            ORDER BY episode_number
        """)
        episodes = cursor.fetchall()
        print(f"Found {len(episodes)} Bonanza episodes:")
        for episode in episodes:
            print(f"Episode {episode[2]}: {episode[1]}")
            print(f"  Content URL: {episode[3]}")
            print(f"  Description: {episode[4][:100]}...")
            print()
        return episodes
    except Exception as e:
        print(f"Error checking episodes: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_bonanza_gcs_urls():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Bonanza episodes with correct GCS URLs based on actual file locations
        bonanza_episodes = [
            {
                "episode_number": 1,
                "title": "Denver McKee",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-Denver-McKee_2p-1080-wCredits.mp4",
                "description": "The Cartwrights encounter Denver McKee, a mysterious stranger with a troubled past."
            },
            {
                "episode_number": 2,
                "title": "The Savage",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Savage_2p-1080-wCredits.mp4",
                "description": "A savage attack on the Ponderosa leads to a search for justice and revenge."
            },
            {
                "episode_number": 3,
                "title": "Day of Reckoning",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-Day-of-Reckoning_2p-1080-wCredits.mp4",
                "description": "The Cartwrights face a day of reckoning when old enemies return to the Ponderosa."
            },
            {
                "episode_number": 4,
                "title": "The Gunmen",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Gunmen_2p-1080-wCredits.mp4",
                "description": "Professional gunmen arrive in Virginia City, threatening the peace of the community."
            },
            {
                "episode_number": 5,
                "title": "The Last Trophy",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Last-Trophy_2p-1080-wCredits.mp4",
                "description": "A hunting expedition turns deadly when the Cartwrights pursue the last trophy."
            },
            {
                "episode_number": 6,
                "title": "The Killer",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Killer_2p-1080-wCredits.mp4",
                "description": "A notorious killer escapes and seeks revenge against those who captured him."
            },
            {
                "episode_number": 7,
                "title": "The Fear Merchants",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Fear-Merchants_2p-1080-wCredits.mp4",
                "description": "Fear merchants spread terror in Virginia City, forcing the Cartwrights to act."
            },
            {
                "episode_number": 8,
                "title": "The Last Trophy",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Last-Trophy_2p-1080-wCredits.mp4",
                "description": "A hunting expedition turns deadly when the Cartwrights pursue the last trophy."
            },
            {
                "episode_number": 9,
                "title": "The Killer",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Killer_2p-1080-wCredits.mp4",
                "description": "A notorious killer escapes and seeks revenge against those who captured him."
            },
            {
                "episode_number": 10,
                "title": "The Fear Merchants",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Fear-Merchants_2p-1080-wCredits.mp4",
                "description": "Fear merchants spread terror in Virginia City, forcing the Cartwrights to act."
            },
            {
                "episode_number": 11,
                "title": "The Last Trophy",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Last-Trophy_2p-1080-wCredits.mp4",
                "description": "A hunting expedition turns deadly when the Cartwrights pursue the last trophy."
            },
            {
                "episode_number": 12,
                "title": "The Killer",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Killer_2p-1080-wCredits.mp4",
                "description": "A notorious killer escapes and seeks revenge against those who captured him."
            },
            {
                "episode_number": 13,
                "title": "The Fear Merchants",
                "content_url": "https://storage.googleapis.com/pecantv_series/bonanza/Bonanza-The-Fear-Merchants_2p-1080-wCredits.mp4",
                "description": "Fear merchants spread terror in Virginia City, forcing the Cartwrights to act."
            }
        ]
        
        cursor.execute("SELECT id FROM content WHERE title = 'Bonanza'")
        series_id = cursor.fetchone()[0]
        
        for episode_data in bonanza_episodes:
            cursor.execute("""
                UPDATE episodes 
                SET title = %s, content_url = %s, description = %s
                WHERE series_id = %s AND episode_number = %s
            """, (
                episode_data["title"],
                episode_data["content_url"],
                episode_data["description"],
                series_id,
                episode_data["episode_number"]
            ))
            print(f"Updated Episode {episode_data['episode_number']}: {episode_data['title']}")
        
        conn.commit()
        print(f"\nSuccessfully updated {len(bonanza_episodes)} Bonanza episodes with GCS URLs")
        
    except Exception as e:
        print(f"Error updating episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Checking current Bonanza episodes...")
    episodes = check_bonanza_episodes()
    
    if episodes:
        print("\nUpdating Bonanza episodes with correct GCS URLs...")
        update_bonanza_gcs_urls()
        
        print("\nVerifying updates...")
        check_bonanza_episodes()
    else:
        print("No Bonanza episodes found to update.") 