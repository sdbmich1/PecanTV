#!/usr/bin/env python3
"""
Insert missing Petrocelli episodes directly into the database.
This script will add episodes 9-22 to complete the series.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime, timezone

# Database configuration
DB_CONFIG = {
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'sslmode': 'require'
}

# Petrocelli series ID
PETROCELLI_SERIES_ID = 21

# Episode data for episodes 9-22
EPISODES_TO_ADD = [
    {
        "episode_number": 9,
        "title": "Five Yard of Trouble",
        "description": "A thrilling episode of Petrocelli where justice is served.",
        "gcs_filename": "Petrocelli-Five-Yard-of-Trouble_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 10,
        "title": "Jubilee Jones",
        "description": "Petrocelli investigates a complex case involving Jubilee Jones.",
        "gcs_filename": "Petrocelli-Jubilee-Jones_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 11,
        "title": "Six Strings of Guilt",
        "description": "A musical mystery unfolds in this gripping Petrocelli episode.",
        "gcs_filename": "Petrocelli-Six-Strings-of-Guilt_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 12,
        "title": "Terror on Wheels",
        "description": "Petrocelli faces danger in this high-speed thriller.",
        "gcs_filename": "Petrocelli-Terror-on-Wheels_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 13,
        "title": "The Gamblers",
        "description": "A tale of high stakes and deception in the world of gambling.",
        "gcs_filename": "Petrocelli-The-Gamblers_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 14,
        "title": "The Pay Off",
        "description": "Petrocelli uncovers a web of corruption and bribery.",
        "gcs_filename": "Petrocelli-The-Pay-Off_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 15,
        "title": "The Sleep of Reason",
        "description": "A psychological thriller that tests Petrocelli's resolve.",
        "gcs_filename": "Petrocelli-The-Sleep-of-Reason_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 16,
        "title": "To See No Evil",
        "description": "Petrocelli investigates a case where nothing is as it seems.",
        "gcs_filename": "Petrocelli-To-See-No-Evil_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 17,
        "title": "A Lonely Victim",
        "description": "Petrocelli defends a victim who stands alone against injustice.",
        "gcs_filename": "Petrocelli-A-Lonely-Victim_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 18,
        "title": "A Night of Terror",
        "description": "A night of horror and mystery in this Petrocelli episode.",
        "gcs_filename": "Petrocelli-A-Night-of-Terror_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 19,
        "title": "Any Number Can Die",
        "description": "A deadly game where anyone could be the next victim.",
        "gcs_filename": "Petrocelli-Any-Number-Can-Die_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 20,
        "title": "Blood Money",
        "description": "Petrocelli investigates a case involving dirty money and murder.",
        "gcs_filename": "Petrocelli-Blood-Money_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 21,
        "title": "Death Ride",
        "description": "A dangerous journey that could be Petrocelli's last.",
        "gcs_filename": "Petrocelli-Death-Ride_2p-1080-wCredits.mp4"
    },
    {
        "episode_number": 22,
        "title": "Death in Small Doses",
        "description": "A case of poisoning that requires Petrocelli's expertise.",
        "gcs_filename": "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4"
    }
]

EXISTING_CONTENT_UUID = 'f3a8b22b-0eee-42bf-8c2f-d40be637cbcc'

def get_next_episode_id(conn):
    """Get the next available episode ID."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT MAX(id) as max_id FROM episodes")
        result = cur.fetchone()
        return (result["max_id"] or 0) + 1

def create_episode(conn, episode_data):
    """Create a single episode in the database."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if episode already exists
            cur.execute(
                "SELECT id FROM episodes WHERE series_id = %s AND episode_number = %s",
                (PETROCELLI_SERIES_ID, episode_data["episode_number"])
            )
            existing = cur.fetchone()
            
            if existing:
                print(f"⚠️  Episode {episode_data['episode_number']} already exists: {episode_data['title']}")
                return False
            
            # Get next episode ID
            episode_id = get_next_episode_id(conn)
            episode_uuid = str(uuid.uuid4())
            
            # Insert episode
            cur.execute("""
                INSERT INTO episodes (
                    id, series_id, episode_number, title, description, 
                    content_url, poster_url, runtime, 
                    season_number, created_at, updated_at, uuid, content_uuid
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                episode_id,
                PETROCELLI_SERIES_ID,
                episode_data["episode_number"],
                episode_data["title"],
                episode_data["description"],
                f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{episode_data['gcs_filename']}",
                "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli1_poster.jpg",
                3600,  # 1 hour duration
                1,     # Season 1
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                episode_uuid,
                EXISTING_CONTENT_UUID
            ))
            
            conn.commit()
            print(f"✅ Created Episode {episode_data['episode_number']}: {episode_data['title']}")
            return True
            
    except Exception as e:
        print(f"❌ Error creating Episode {episode_data['episode_number']}: {str(e)}")
        conn.rollback()
        return False

def main():
    print("🎬 Adding missing Petrocelli episodes to database...")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        
        # Check current episodes
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT COUNT(*) as count FROM episodes WHERE series_id = %s",
                (PETROCELLI_SERIES_ID,)
            )
            result = cur.fetchone()
            current_count = result["count"]
            print(f"📊 Current episodes in database: {current_count}")
        
        # Add missing episodes
        success_count = 0
        for episode_data in EPISODES_TO_ADD:
            if create_episode(conn, episode_data):
                success_count += 1
        
        print("=" * 60)
        print(f"✅ Successfully added {success_count}/{len(EPISODES_TO_ADD)} episodes")
        
        # Verify final count
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT COUNT(*) as count FROM episodes WHERE series_id = %s",
                (PETROCELLI_SERIES_ID,)
            )
            result = cur.fetchone()
            final_count = result["count"]
            print(f"📊 Final episode count in database: {final_count}")
            
            if final_count == 22:
                print("🎉 All 22 Petrocelli episodes are now in the database!")
            else:
                print(f"⚠️  Expected 22 episodes, but found {final_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")

if __name__ == "__main__":
    main() 