#!/usr/bin/env python3
"""
Script to restore Bonanza episodes from scratch.
This script will create all 13 Bonanza episodes with proper metadata and URLs.
"""

import psycopg2
import uuid
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# Bonanza episodes data - based on typical Western series structure
BONANZA_EPISODES = [
    {
        'episode_number': 1,
        'title': 'A Rose for Lotta',
        'description': 'The Cartwrights help a young woman who is being pursued by outlaws.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_01.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_01_poster.jpg'
    },
    {
        'episode_number': 2,
        'title': 'Death on Sun Mountain',
        'description': 'Ben and his sons investigate a murder on their property.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_02.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_02_poster.jpg'
    },
    {
        'episode_number': 3,
        'title': 'The Newcomers',
        'description': 'A family of settlers arrives in Virginia City, bringing both hope and conflict.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_03.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_03_poster.jpg'
    },
    {
        'episode_number': 4,
        'title': 'The Paiute War',
        'description': 'The Cartwrights must navigate tensions between settlers and Native Americans.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_04.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_04_poster.jpg'
    },
    {
        'episode_number': 5,
        'title': 'Enter Mark Twain',
        'description': 'Samuel Clemens arrives in Virginia City and begins his writing career.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_05.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_05_poster.jpg'
    },
    {
        'episode_number': 6,
        'title': 'The Julia Bulette Story',
        'description': 'A famous madam in Virginia City becomes involved with the Cartwrights.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_06.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_06_poster.jpg'
    },
    {
        'episode_number': 7,
        'title': 'The Saga of Annie O\'Toole',
        'description': 'A woman from Ben\'s past arrives in Virginia City with a secret.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_07.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_07_poster.jpg'
    },
    {
        'episode_number': 8,
        'title': 'The Philip Deidesheimer Story',
        'description': 'A mining engineer develops a new method for supporting mine tunnels.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_08.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_08_poster.jpg'
    },
    {
        'episode_number': 9,
        'title': 'Mr. Henry Comstock',
        'description': 'The story of the man who discovered the Comstock Lode.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_09.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_09_poster.jpg'
    },
    {
        'episode_number': 10,
        'title': 'The Magnificent Adah',
        'description': 'A famous actress visits Virginia City and captures the attention of the Cartwrights.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_10.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_10_poster.jpg'
    },
    {
        'episode_number': 11,
        'title': 'The Truckee Strip',
        'description': 'A dispute over land ownership leads to violence in Virginia City.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_11.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_11_poster.jpg'
    },
    {
        'episode_number': 12,
        'title': 'The Hanging Posse',
        'description': 'A vigilante group threatens the peace of Virginia City.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_12.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_12_poster.jpg'
    },
    {
        'episode_number': 13,
        'title': 'The Spanish Grant',
        'description': 'The Cartwrights must defend their land from a Spanish land grant claim.',
        'runtime': 60,
        'content_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_13.mp4',
        'poster_url': 'https://storage.googleapis.com/pecantv_series/bonanza/Bonanza_Episode_13_poster.jpg'
    }
]

def restore_bonanza_episodes():
    """Restore all Bonanza episodes to the database."""
    print("🎬 Restoring Bonanza Episodes")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Bonanza series info
        cur.execute("""
            SELECT id, uuid FROM content 
            WHERE title = 'Bonanza' AND type = 'SERIES'
        """)
        series_result = cur.fetchone()
        
        if not series_result:
            print("❌ Bonanza series not found in database")
            return
        
        series_id, series_uuid = series_result
        print(f"✅ Found Bonanza series (ID: {series_id}, UUID: {series_uuid})")
        
        # Check if episodes already exist
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        existing_count = cur.fetchone()[0]
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing Bonanza episodes")
            response = input("Do you want to delete existing episodes and recreate them? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled")
                return
            
            # Delete existing episodes
            cur.execute("DELETE FROM episodes WHERE series_id = %s", (series_id,))
            print(f"🗑️  Deleted {existing_count} existing episodes")
        
        # Insert all Bonanza episodes
        inserted_count = 0
        for episode_data in BONANZA_EPISODES:
            try:
                cur.execute("""
                    INSERT INTO episodes (
                        uuid, title, description, season_number, episode_number, runtime,
                        content_url, poster_url, air_date, series_id, content_uuid,
                        created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    str(uuid.uuid4()),
                    episode_data['title'],
                    episode_data['description'],
                    1,  # season_number
                    episode_data['episode_number'],
                    episode_data['runtime'],
                    episode_data['content_url'],
                    episode_data['poster_url'],
                    None,  # air_date
                    series_id,
                    str(series_uuid),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
                
                print(f"✅ Inserted episode {episode_data['episode_number']}: {episode_data['title']}")
                inserted_count += 1
                
            except Exception as e:
                print(f"❌ Error inserting episode {episode_data['episode_number']}: {e}")
        
        conn.commit()
        print(f"\n🎉 Successfully restored {inserted_count} Bonanza episodes!")
        
        # Verify the restoration
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        final_count = cur.fetchone()[0]
        print(f"📊 Total Bonanza episodes in database: {final_count}")
        
        if final_count == 13:
            print("✅ All 13 Bonanza episodes successfully restored!")
        else:
            print(f"⚠️  Expected 13 episodes, found {final_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    restore_bonanza_episodes() 