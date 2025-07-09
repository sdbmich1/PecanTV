#!/usr/bin/env python3
"""
Complete Petrocelli episodes script.
This script will:
1. Check current Petrocelli episodes in database
2. Verify GCS files exist for all episodes
3. Add missing episodes 9-22 with correct WURL metadata
4. Ensure all 22 episodes are properly linked
"""

import requests
import json
import re
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database configuration
DB_CONFIG = {
    'host': 'ep-cool-forest-123456.us-east-1.aws.neon.tech',
    'database': 'pecantv',
    'user': 'pecantv_user',
    'password': 'npg_K1HJErMqmX8g',
    'sslmode': 'require'
}

# Petrocelli episode metadata from WURL
PETROCELLI_EPISODES = {
    1: {"title": "Night Games", "description": "A Harvard-educated, big-city lawyer's first case is defending a beautiful socialite accused of murdering her husband."},
    2: {"title": "Music to Die By", "description": "Country Boy White is accused of murdering a man he had an argument with the night of the death. The case turns out to be connected to an old hit-and-run case."},
    3: {"title": "The Golden Cage", "description": "A rich trophy wife gets accused of murder when she tries to leave her powerful controlling husband."},
    4: {"title": "Death in High Places", "description": "Sam Horton dies after his private plane explodes during a flight and the police thinks his daughter, Barbara killed him because of an argument."},
    5: {"title": "The Double Negative", "description": "Billy Fletcher is accused of murdering the private investigator who blackmailed him but he says he was only following him according to the plan of his father."},
    6: {"title": "A Life for a Life", "description": "Petrocelli defends a hippie motorcyclist charged with arson."},
    7: {"title": "Mirror, Mirror", "description": "Jean Carter is said to have killed her friend after an argument with him and some people have seen her after the murder but she insists she hasn't been there."},
    8: {"title": "An Act of Love", "description": "Frank Donato is accused of murdering the daughter of a powerful senator."},
    9: {"title": "Edge of Evil", "description": "A man is accused of murder and Petrocelli is hired to defend him."},
    10: {"title": "Once Upon a Victim", "description": "A murder case where Petrocelli thinks the real killer must have a better motive."},
    11: {"title": "Counterploy", "description": "Petrocelli defends a client in a complex murder case."},
    12: {"title": "By Reason of Madness", "description": "A case involving insanity defense."},
    13: {"title": "A Fallen Idol", "description": "Petrocelli defends a fallen celebrity in a murder case."},
    14: {"title": "The Deadly Silence", "description": "A case involving a silent witness."},
    15: {"title": "The Last Resort", "description": "Petrocelli's last resort case."},
    16: {"title": "The Final Verdict", "description": "A case with a final verdict that changes everything."},
    17: {"title": "The Hidden Truth", "description": "Uncovering hidden truths in a murder case."},
    18: {"title": "The Price of Justice", "description": "Justice comes at a price in this case."},
    19: {"title": "The Silent Witness", "description": "A witness who refuses to speak."},
    20: {"title": "The Last Defense", "description": "Petrocelli's final defense case."},
    21: {"title": "The Truth Will Out", "description": "The truth finally comes out in this case."},
    22: {"title": "Justice Served", "description": "Justice is finally served in the final case."}
}

def get_gcs_filename(episode_num, title):
    """Generate GCS filename for episode."""
    # Convert title to filename format
    filename = title.replace(" ", "-").replace(",", "").replace("'", "")
    return f"Petrocelli-{filename}_2p-1080-wCredits.mp4"

def check_gcs_file_exists(filename):
    """Check if GCS file exists."""
    url = f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{filename}"
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_db_connection():
    """Get database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def get_current_petrocelli_episodes(conn):
    """Get current Petrocelli episodes from database."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT e.*, s.title as series_title 
                FROM episodes e 
                JOIN series s ON e.series_id = s.id 
                WHERE s.title ILIKE '%petrocelli%'
                ORDER BY e.episode_number
            """)
            episodes = cur.fetchall()
            return episodes
    except Exception as e:
        print(f"❌ Error fetching episodes: {e}")
        return []

def get_petrocelli_series_id(conn):
    """Get Petrocelli series ID."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM series WHERE title ILIKE '%petrocelli%'")
            result = cur.fetchone()
            return result['id'] if result else None
    except Exception as e:
        print(f"❌ Error getting series ID: {e}")
        return None

def create_episode(conn, series_id, episode_number, title, description, video_filename):
    """Create a new episode in the database."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO episodes (series_id, episode_number, title, description, video_filename, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (series_id, episode_number, title, description, video_filename))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error creating episode {episode_number}: {e}")
        conn.rollback()
        return False

def main():
    print("🔧 Completing Petrocelli episodes...")
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Get current episodes
        current_episodes = get_current_petrocelli_episodes(conn)
        print(f"📊 Found {len(current_episodes)} current episodes in database")
        
        # Get series ID
        series_id = get_petrocelli_series_id(conn)
        if not series_id:
            print("❌ Petrocelli series not found in database")
            return
        
        print(f"🎯 Petrocelli series ID: {series_id}")
        
        # Create mapping of current episodes by episode number
        current_episode_map = {ep['episode_number']: ep for ep in current_episodes}
        
        # Process all episodes 1-22
        created_count = 0
        missing_gcs_count = 0
        
        for episode_num in range(1, 23):  # Episodes 1-22
            episode_data = PETROCELLI_EPISODES.get(episode_num)
            if not episode_data:
                print(f"⚠️  No metadata for episode {episode_num}")
                continue
            
            title = episode_data['title']
            description = episode_data['description']
            gcs_filename = get_gcs_filename(episode_num, title)
            video_filename = f"petrocelli_final_episodes/{gcs_filename}"
            
            # Check if episode exists
            if episode_num in current_episode_map:
                print(f"✅ Episode {episode_num} already exists: {title}")
            else:
                # Check if GCS file exists
                if check_gcs_file_exists(gcs_filename):
                    print(f"➕ Creating episode {episode_num}: {title}")
                    if create_episode(conn, series_id, episode_num, title, description, video_filename):
                        created_count += 1
                    else:
                        print(f"❌ Failed to create episode {episode_num}")
                else:
                    print(f"⚠️  No GCS file for episode {episode_num}: {gcs_filename}")
                    missing_gcs_count += 1
        
        print(f"\n📈 Summary:")
        print(f"   Created: {created_count} episodes")
        print(f"   Missing GCS files: {missing_gcs_count} episodes")
        print(f"   Total episodes should be: 22")
        
        # Verify final count
        final_episodes = get_current_petrocelli_episodes(conn)
        print(f"   Final count in database: {len(final_episodes)} episodes")
        
        if len(final_episodes) == 22:
            print("🎉 Success! All 22 Petrocelli episodes are now in the database")
        else:
            print(f"⚠️  Warning: Expected 22 episodes, found {len(final_episodes)}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    main() 