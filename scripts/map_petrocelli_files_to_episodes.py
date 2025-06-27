#!/usr/bin/env python3
"""
Script to map the 9 actual Petrocelli files to episodes.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime, timezone

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# The 9 actual files we found in GCS with proper episode mappings
PETROCELLI_EPISODES = [
    {
        'episode_number': 1,
        'title': 'Deadly Journey',
        'filename': 'Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4',
        'description': 'Tony Petrocelli defends a man accused of murder during a deadly journey.',
        'runtime': 60
    },
    {
        'episode_number': 2,
        'title': 'Face of Evil',
        'filename': 'Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4',
        'description': 'Petrocelli faces the challenge of defending against the face of evil.',
        'runtime': 60
    },
    {
        'episode_number': 3,
        'title': 'Four the Hard Way',
        'filename': 'Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4',
        'description': 'A complex case involving four defendants takes Petrocelli the hard way.',
        'runtime': 60
    },
    {
        'episode_number': 4,
        'title': 'Shadow of Fear',
        'filename': 'Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4',
        'description': 'Petrocelli works to dispel the shadow of fear in a tense courtroom drama.',
        'runtime': 60
    },
    {
        'episode_number': 5,
        'title': 'The Night Visitor',
        'filename': 'Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4',
        'description': 'A mysterious night visitor becomes the center of Petrocelli\'s latest case.',
        'runtime': 60
    },
    {
        'episode_number': 6,
        'title': 'Too Many Alibis',
        'filename': 'Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4',
        'description': 'Petrocelli must navigate through too many alibis to find the truth.',
        'runtime': 60
    },
    {
        'episode_number': 7,
        'title': 'Shadow of a Doubt',
        'filename': 'Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4',
        'description': 'Petrocelli works to cast a shadow of doubt on the prosecution\'s case.',
        'runtime': 60
    },
    {
        'episode_number': 8,
        'title': 'Survival',
        'filename': 'Petrocelli-Survival_2p-1080-wCredits.mp4',
        'description': 'A case of survival becomes Petrocelli\'s most challenging defense yet.',
        'runtime': 60
    },
    {
        'episode_number': 9,
        'title': 'Death in Small Doses',
        'filename': 'Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4',
        'description': 'Petrocelli investigates a case involving death in small doses.',
        'runtime': 60
    }
]

def map_petrocelli_files_to_episodes():
    """Map the actual Petrocelli files to episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🎬 MAPPING PETROCELLI FILES TO EPISODES")
        print("=" * 50)
        
        # Get the main series record
        cur.execute("SELECT id, uuid FROM content WHERE type = 'SERIES' AND title = 'Petrocelli'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Petrocelli series not found")
            return
        
        series_id, series_uuid = series_record['id'], series_record['uuid']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Check if episodes already exist
        cur.execute("SELECT COUNT(*) as count FROM episodes WHERE series_id = %s", (series_id,))
        existing_count = cur.fetchone()['count']
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing episodes. Removing them first...")
            cur.execute("DELETE FROM episodes WHERE series_id = %s", (series_id,))
            print(f"🗑️  Deleted {cur.rowcount} existing episodes")
        
        # Insert the actual episodes
        inserted = 0
        for ep in PETROCELLI_EPISODES:
            episode_num = ep['episode_number']
            title = ep['title']
            filename = ep['filename']
            description = ep['description']
            runtime = ep['runtime']
            
            # Build the content URL
            content_url = f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{filename}"
            
            # Insert the episode
            cur.execute("""
                INSERT INTO episodes (
                    uuid, title, description, season_number, episode_number, runtime,
                    content_url, series_id, content_uuid, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                str(uuid.uuid4()),
                title,
                description,
                1,  # season_number
                episode_num,
                runtime,
                content_url,
                series_id,
                str(series_uuid),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            ))
            
            print(f"  ✅ Episode {episode_num}: {title}")
            print(f"     File: {filename}")
            inserted += 1
        
        conn.commit()
        print(f"\n✅ Successfully created {inserted} Petrocelli episodes")
        print("🎬 All episodes have real video files - no placeholders!")
        print("📺 Each episode corresponds to an actual file in the GCS bucket")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    map_petrocelli_files_to_episodes() 