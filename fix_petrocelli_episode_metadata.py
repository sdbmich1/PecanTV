#!/usr/bin/env python3
"""
Fix Petrocelli episode metadata to align with WURL data and GCS files.
This script will:
1. Read WURL metadata for Petrocelli episodes from CSV
2. Check GCS files for Petrocelli episodes
3. Update database episodes to match WURL metadata
4. Ensure all 22 episodes are properly linked
"""

import json
import os
import re
import pandas as pd
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database configuration
DB_CONFIG = {
    'host': 'ep-cool-forest-123456.us-east-1.aws.neon.tech',
    'database': 'pecantv',
    'user': 'pecantv_user',
    'password': 'npg_K1HJErMqmX8g'
}

def load_wurl_metadata():
    """Load WURL metadata for Petrocelli episodes from CSV."""
    # Use the latest WURL metadata file
    wurl_file = Path("Wurl - File Upload Metadata_Version 7.0.64.csv")
    if not wurl_file.exists():
        print("❌ WURL metadata file not found")
        return {}
    
    try:
        df = pd.read_csv(wurl_file, encoding='utf-8')
        print(f"📋 Loaded WURL metadata with {len(df)} entries")
    except Exception as e:
        print(f"❌ Error reading WURL file: {e}")
        return {}
    
    # Extract Petrocelli episodes
    petrocelli_episodes = {}
    
    for _, row in df.iterrows():
        title = str(row.get('Title', '')).strip()
        if 'petrocelli' in title.lower():
            # Extract episode number from title
            episode_match = re.search(r'episode\s+(\d+)', title.lower())
            if episode_match:
                episode_num = int(episode_match.group(1))
                petrocelli_episodes[episode_num] = {
                    'title': title,
                    'description': str(row.get('Description', '')).strip(),
                    'duration': str(row.get('Duration', '')).strip(),
                    'wurl_id': str(row.get('ID', '')).strip()
                }
    
    print(f"📋 Found {len(petrocelli_episodes)} Petrocelli episodes in WURL metadata")
    return petrocelli_episodes

def get_gcs_petrocelli_files():
    """Get list of Petrocelli video files from GCS."""
    gcs_dir = Path("../pecantv_series/Petrocelli_final_episodes")
    if not gcs_dir.exists():
        print(f"❌ GCS directory not found: {gcs_dir}")
        return {}
    
    video_files = {}
    for file_path in gcs_dir.glob("*.mp4"):
        filename = file_path.name
        # Extract episode number from filename
        episode_match = re.search(r'(\d+)', filename)
        if episode_match:
            episode_num = int(episode_match.group(1))
            video_files[episode_num] = filename
    
    print(f"🎬 Found {len(video_files)} Petrocelli video files in GCS")
    return video_files

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

def update_episode_metadata(conn, episode_id, episode_number, title, description, video_filename):
    """Update episode metadata in database."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE episodes 
                SET episode_number = %s, title = %s, description = %s, video_filename = %s
                WHERE id = %s
            """, (episode_number, title, description, video_filename, episode_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error updating episode {episode_id}: {e}")
        conn.rollback()
        return False

def create_missing_episode(conn, series_id, episode_number, title, description, video_filename):
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

def main():
    print("🔧 Fixing Petrocelli episode metadata...")
    
    # Load WURL metadata
    wurl_episodes = load_wurl_metadata()
    if not wurl_episodes:
        print("❌ No WURL metadata found for Petrocelli")
        return
    
    # Get GCS files
    gcs_files = get_gcs_petrocelli_files()
    if not gcs_files:
        print("❌ No GCS files found for Petrocelli")
        return
    
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
        updated_count = 0
        created_count = 0
        
        for episode_num in range(1, 23):  # Episodes 1-22
            wurl_data = wurl_episodes.get(episode_num)
            gcs_file = gcs_files.get(episode_num)
            
            if not wurl_data:
                print(f"⚠️  No WURL data for episode {episode_num}")
                continue
            
            if not gcs_file:
                print(f"⚠️  No GCS file for episode {episode_num}")
                continue
            
            title = wurl_data['title']
            description = wurl_data.get('description', '')
            video_filename = f"Petrocelli_final_episodes/{gcs_file}"
            
            # Check if episode exists
            if episode_num in current_episode_map:
                # Update existing episode
                episode = current_episode_map[episode_num]
                if (episode['title'] != title or 
                    episode['description'] != description or 
                    episode['video_filename'] != video_filename):
                    
                    print(f"🔄 Updating episode {episode_num}: {title}")
                    if update_episode_metadata(conn, episode['id'], episode_num, title, description, video_filename):
                        updated_count += 1
                    else:
                        print(f"❌ Failed to update episode {episode_num}")
                else:
                    print(f"✅ Episode {episode_num} already correct")
            else:
                # Create new episode
                print(f"➕ Creating episode {episode_num}: {title}")
                if create_missing_episode(conn, series_id, episode_num, title, description, video_filename):
                    created_count += 1
                else:
                    print(f"❌ Failed to create episode {episode_num}")
        
        print(f"\n📈 Summary:")
        print(f"   Updated: {updated_count} episodes")
        print(f"   Created: {created_count} episodes")
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