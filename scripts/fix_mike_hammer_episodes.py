#!/usr/bin/env python3
"""
Script to fix Mike Hammer episodes using Wurl metadata
Updates titles, descriptions, and content URLs to match actual GCS files
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def get_wurl_metadata():
    """Get Mike Hammer metadata from Wurl file"""
    try:
        df = pd.read_csv('Wurl - File Upload Metadata_Version 7.0.54.csv', encoding='utf-8')
        mh_data = df[df['Series Name'].astype(str).str.contains('Mike Hammer', case=False, na=False)]
        
        episodes = []
        for _, row in mh_data.iterrows():
            episodes.append({
                'title': row['Title'].strip(),
                'description': row['Description'].strip() if pd.notna(row['Description']) else '',
                'video_filename': row['Video Filename'].strip() if pd.notna(row['Video Filename']) else '',
                'content_url': f"https://storage.googleapis.com/pecantv_series/mike_hammer/{row['Video Filename'].strip()}"
            })
        
        return episodes
    except Exception as e:
        print(f"Error reading Wurl metadata: {e}")
        return []

def update_mike_hammer_episodes():
    """Update Mike Hammer episodes in the database"""
    # Get Wurl metadata
    wurl_episodes = get_wurl_metadata()
    
    if not wurl_episodes:
        print("No Mike Hammer episodes found in Wurl metadata")
        return
    
    print(f"Found {len(wurl_episodes)} Mike Hammer episodes in Wurl metadata:")
    for i, ep in enumerate(wurl_episodes, 1):
        print(f"{i}. {ep['title']} -> {ep['video_filename']}")
    
    # Connect to database
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current Mike Hammer episodes
        cur.execute("SELECT id, title, content_url FROM episodes WHERE series_id = 45 ORDER BY episode_number")
        current_episodes = cur.fetchall()
        
        print(f"\nCurrent database has {len(current_episodes)} Mike Hammer episodes:")
        for ep in current_episodes:
            print(f"ID: {ep['id']}, Title: {ep['title']}")
        
        # Update episodes
        for i, wurl_ep in enumerate(wurl_episodes):
            if i < len(current_episodes):
                episode_id = current_episodes[i]['id']
                
                # Update the episode
                cur.execute("""
                    UPDATE episodes 
                    SET title = %s, description = %s, content_url = %s
                    WHERE id = %s
                """, (
                    wurl_ep['title'],
                    wurl_ep['description'],
                    wurl_ep['content_url'],
                    episode_id
                ))
                
                print(f"Updated episode {episode_id}: {wurl_ep['title']}")
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully updated {len(wurl_episodes)} Mike Hammer episodes")
        
        # Verify the updates
        cur.execute("SELECT id, title, content_url FROM episodes WHERE series_id = 45 ORDER BY episode_number")
        updated_episodes = cur.fetchall()
        
        print("\nUpdated episodes:")
        for ep in updated_episodes:
            print(f"ID: {ep['id']}, Title: {ep['title']}")
            print(f"  URL: {ep['content_url']}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("🔧 Fixing Mike Hammer episodes with Wurl metadata...")
    update_mike_hammer_episodes()
    print("Done!") 