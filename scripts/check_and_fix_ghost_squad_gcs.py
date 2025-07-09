#!/usr/bin/env python3
import psycopg2

# Neon production database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL)

def check_ghost_squad_episodes():
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Check current Ghost Squad episodes
        cursor.execute("""
            SELECT id, title, episode_number, content_url, description 
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Ghost Squad')
            ORDER BY episode_number
        """)
        
        episodes = cursor.fetchall()
        print(f"Found {len(episodes)} Ghost Squad episodes:")
        
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

def update_ghost_squad_gcs_urls():
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Ghost Squad episodes with correct GCS URLs
        ghost_squad_episodes = [
            {
                "episode_number": 1,
                "title": "The Heir Apparent",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Heir-Apparent_1080-wCredits.mp4",
                "description": "Ghost Squad investigates a mysterious inheritance case that leads to unexpected revelations."
            },
            {
                "episode_number": 2,
                "title": "The Silent Witness",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Silent-Witness_1080-wCredits.mp4",
                "description": "A witness who cannot speak holds the key to solving a complex criminal case."
            },
            {
                "episode_number": 3,
                "title": "The Phantom Killer",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Phantom-Killer_1080-wCredits.mp4",
                "description": "Ghost Squad tracks down an elusive killer who leaves no trace behind."
            },
            {
                "episode_number": 4,
                "title": "The Double Agent",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Double-Agent_1080-wCredits.mp4",
                "description": "A case of espionage and betrayal tests the team's trust and loyalty."
            },
            {
                "episode_number": 5,
                "title": "The Final Assignment",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Final-Assignment_1080-wCredits.mp4",
                "description": "Ghost Squad faces their most dangerous mission yet in this thrilling finale."
            }
        ]
        
        # Get Ghost Squad series ID
        cursor.execute("SELECT id FROM content WHERE title = 'Ghost Squad'")
        series_id = cursor.fetchone()[0]
        
        # Update each episode
        for episode_data in ghost_squad_episodes:
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
        print(f"\nSuccessfully updated {len(ghost_squad_episodes)} Ghost Squad episodes with GCS URLs")
        
    except Exception as e:
        print(f"Error updating episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Checking current Ghost Squad episodes...")
    episodes = check_ghost_squad_episodes()
    
    if episodes:
        print("\nUpdating Ghost Squad episodes with correct GCS URLs...")
        update_ghost_squad_gcs_urls()
        
        print("\nVerifying updates...")
        check_ghost_squad_episodes()
    else:
        print("No Ghost Squad episodes found to update.") 