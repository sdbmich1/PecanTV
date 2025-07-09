#!/usr/bin/env python3
import psycopg2
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def fix_ghost_squad_episodes():
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Ghost Squad episodes with correct data from backup
        ghost_squad_episodes = [
            {
                "episode_number": 1,
                "title": "The Man with Delicate Hands",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Man-With-Delicate-Hands_1080-wCredits.mp4",
                "description": "Ghost Squad investigates a case involving a criminal with unusual methods."
            },
            {
                "episode_number": 2,
                "title": "The Menacing Mazurka",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Menacing-Mazurka_1080-wCredits.mp4",
                "description": "A mysterious dance leads Ghost Squad into a dangerous investigation."
            },
            {
                "episode_number": 3,
                "title": "The Last Jump",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-The-Last-Jump_1080-wCredits.mp4",
                "description": "Ghost Squad faces a high-stakes case that could be their final mission."
            },
            {
                "episode_number": 4,
                "title": "Ticket for Blackmail",
                "content_url": "https://storage.googleapis.com/pecantv_series/ghost_squad/GS-Ticket-for-Blackmail_1080-wCredits.mp4",
                "description": "A blackmail scheme puts Ghost Squad on the trail of a cunning criminal."
            }
        ]
        
        # Get Ghost Squad series ID and content_uuid
        cursor.execute("SELECT id, uuid FROM content WHERE title = 'Ghost Squad'")
        series_row = cursor.fetchone()
        series_id = series_row[0]
        content_uuid = series_row[1]
        print(f"Found Ghost Squad series ID: {series_id}, content_uuid: {content_uuid}")
        
        # First, delete existing episodes
        cursor.execute("DELETE FROM episodes WHERE series_id = %s", (series_id,))
        print(f"Deleted existing Ghost Squad episodes")
        
        # Insert new episodes with correct data
        for episode_data in ghost_squad_episodes:
            cursor.execute("""
                INSERT INTO episodes (
                    uuid, content_uuid, series_id, season_number, episode_number, title, 
                    description, content_url, runtime, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                str(uuid.uuid4()),
                content_uuid,
                series_id,
                1,  # season_number
                episode_data["episode_number"],
                episode_data["title"],
                episode_data["description"],
                episode_data["content_url"],
                60  # runtime
            ))
            
            print(f"Inserted Episode {episode_data['episode_number']}: {episode_data['title']}")
        
        conn.commit()
        print(f"\nSuccessfully updated Ghost Squad with {len(ghost_squad_episodes)} episodes")
        
        # Verify the updates
        cursor.execute("""
            SELECT episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cursor.fetchall()
        print(f"\nVerification - Found {len(episodes)} episodes:")
        for ep in episodes:
            print(f"Episode {ep[0]}: {ep[1]}")
        
    except Exception as e:
        print(f"Error updating episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Fixing Ghost Squad episodes with correct titles and GCS URLs...")
    fix_ghost_squad_episodes() 