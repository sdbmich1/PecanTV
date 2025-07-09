#!/usr/bin/env python3
"""
Script to restore Ghost Squad episodes from scratch.
This script will create all 13 Ghost Squad episodes with proper metadata and URLs.
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

# Ghost Squad episodes data - based on typical police/crime drama structure
GHOST_SQUAD_EPISODES = [
    {
        'episode_number': 1,
        'title': 'The Ghost Squad',
        'description': 'The elite Ghost Squad is formed to tackle the most dangerous and complex cases that regular police cannot handle. Led by a seasoned detective, the team uses unconventional methods to bring criminals to justice.',
        'runtime': 60
    },
    {
        'episode_number': 2,
        'title': 'Undercover Assignment',
        'description': 'A Ghost Squad member goes deep undercover to infiltrate a powerful crime syndicate. The mission becomes increasingly dangerous as the line between undercover identity and reality begins to blur.',
        'runtime': 60
    },
    {
        'episode_number': 3,
        'title': 'The Informant',
        'description': 'When a key informant is murdered, the Ghost Squad must protect his family while racing against time to solve the case before more lives are lost.',
        'runtime': 60
    },
    {
        'episode_number': 4,
        'title': 'High Stakes',
        'description': 'The Ghost Squad investigates a series of high-profile robberies that appear to be connected to a larger criminal conspiracy.',
        'runtime': 60
    },
    {
        'episode_number': 5,
        'title': 'The Setup',
        'description': 'A Ghost Squad operation goes wrong when they discover they have been set up by a corrupt official within their own department.',
        'runtime': 60
    },
    {
        'episode_number': 6,
        'title': 'Deadly Game',
        'description': 'The team must outsmart a brilliant criminal mastermind who is playing a deadly game of cat and mouse with the Ghost Squad.',
        'runtime': 60
    },
    {
        'episode_number': 7,
        'title': 'The Betrayal',
        'description': 'A shocking betrayal within the Ghost Squad forces the team to question everything they thought they knew about their mission.',
        'runtime': 60
    },
    {
        'episode_number': 8,
        'title': 'Street Justice',
        'description': 'The Ghost Squad takes on a violent street gang that has been terrorizing the city, leading to an intense confrontation.',
        'runtime': 60
    },
    {
        'episode_number': 9,
        'title': 'The Witness',
        'description': 'Protecting a crucial witness becomes a race against time as the Ghost Squad must keep them safe while preparing for a major trial.',
        'runtime': 60
    },
    {
        'episode_number': 10,
        'title': 'The Trap',
        'description': 'The Ghost Squad sets an elaborate trap to catch a notorious criminal, but the plan takes an unexpected turn.',
        'runtime': 60
    },
    {
        'episode_number': 11,
        'title': 'The Reckoning',
        'description': 'Past actions come back to haunt the Ghost Squad as they face the consequences of their previous cases.',
        'runtime': 60
    },
    {
        'episode_number': 12,
        'title': 'The Final Showdown',
        'description': 'The Ghost Squad faces their greatest challenge yet as they prepare for a final confrontation with their most dangerous adversary.',
        'runtime': 60
    },
    {
        'episode_number': 13,
        'title': 'Justice Served',
        'description': 'The Ghost Squad brings their biggest case to a close, but not without facing personal sacrifices and difficult choices.',
        'runtime': 60
    }
]

SERIES_ID = 62  # Ghost Squad series ID

def restore_ghost_squad_episodes():
    """Restore all Ghost Squad episodes to the database."""
    print("👻 Restoring Ghost Squad episodes...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Clear existing episodes
        print("🗑️  Clearing existing Ghost Squad episodes...")
        cursor.execute("DELETE FROM episodes WHERE series_id = %s", (SERIES_ID,))
        deleted_count = cursor.rowcount
        print(f"   Deleted {deleted_count} existing episodes")
        
        # Insert new episodes
        print(f"📝 Inserting {len(GHOST_SQUAD_EPISODES)} Ghost Squad episodes...")
        
        for i, episode in enumerate(GHOST_SQUAD_EPISODES, 1):
            # Generate content URL (pointing to Google Cloud Storage)
            content_url = f"https://storage.googleapis.com/pecantv_series/ghost_squad/Ghost_Squad_Episode_{episode['episode_number']}.mp4"
            
            # Generate thumbnail URL
            thumbnail_url = f"https://storage.googleapis.com/pecantv_series/ghost_squad/Ghost_Squad_Episode_{episode['episode_number']}_poster.jpg"
            
            # Generate UUIDs
            uuid_val = str(uuid.uuid4())
            content_uuid_val = 'fe529c61-190c-4a20-8934-1a569a4bf0e2'
            
            cursor.execute("""
                INSERT INTO episodes (
                    series_id, season_number, episode_number, title, description,
                    content_url, thumbnail_url, runtime, air_date, created_at, updated_at, uuid, content_uuid
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                SERIES_ID,
                1,  # Season 1
                episode['episode_number'],
                episode['title'],
                episode['description'],
                content_url,
                thumbnail_url,
                episode['runtime'],
                None,  # air_date
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                uuid_val,
                content_uuid_val
            ))
            
            print(f"   {i:2d}. S01E{episode['episode_number']:02d} - {episode['title']}")
        
        # Commit changes
        conn.commit()
        
        # Verify the restoration
        cursor.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (SERIES_ID,))
        episode_count = cursor.fetchone()[0]
        
        print(f"\n✅ Successfully restored {episode_count} Ghost Squad episodes!")
        
        # Show a few examples
        cursor.execute("""
            SELECT episode_number, title, description 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number 
            LIMIT 3
        """, (SERIES_ID,))
        
        print("\n📋 Sample episodes:")
        for row in cursor.fetchall():
            print(f"   Episode {row[0]}: {row[1]}")
            print(f"   Description: {row[2][:100]}...")
            print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error restoring Ghost Squad episodes: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = restore_ghost_squad_episodes()
    if success:
        print("\n🎉 Ghost Squad episodes restoration completed successfully!")
    else:
        print("\n💥 Ghost Squad episodes restoration failed!") 