#!/usr/bin/env python3
"""
Script to fix Longstreet episodes using Wurl metadata
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
    """Get Longstreet metadata from Wurl files"""
    try:
        # Use the Wurl file that has Longstreet episodes
        df = pd.read_csv('Wurl - File Upload Metadata_Version 7.0.41.csv', encoding='utf-8')
        longstreet_data = df[df['Series Name'].astype(str).str.contains('Longstreet', case=False, na=False)]
        
        episodes = []
        for _, row in longstreet_data.iterrows():
            episodes.append({
                'title': row['Title'].strip(),
                'description': row['Description'].strip() if pd.notna(row['Description']) else '',
                'video_filename': row['Video Filename'].strip() if pd.notna(row['Video Filename']) else '',
                'content_url': f"https://storage.googleapis.com/pecantv_series/longstreet/{row['Video Filename'].strip()}"
            })
        
        return episodes
    except Exception as e:
        print(f"Error reading Wurl metadata: {e}")
        return []

def update_longstreet_episodes():
    """Update Longstreet episodes in the database"""
    # Get Wurl metadata
    wurl_episodes = get_wurl_metadata()
    
    if not wurl_episodes:
        print("No Longstreet episodes found in Wurl metadata")
        return
    
    print(f"Found {len(wurl_episodes)} Longstreet episodes in Wurl metadata:")
    for i, ep in enumerate(wurl_episodes, 1):
        print(f"{i}. {ep['title']} -> {ep['video_filename']}")
    
    # Connect to database
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current Longstreet episodes
        cur.execute("SELECT id, title, content_url FROM episodes WHERE series_id = 49 ORDER BY episode_number")
        current_episodes = cur.fetchall()
        
        print(f"\nCurrent database has {len(current_episodes)} Longstreet episodes:")
        for ep in current_episodes:
            print(f"ID: {ep['id']}, Title: {ep['title']}")
        
        # Update episodes - only update the first 22 episodes (matching Wurl metadata)
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
        
        # Delete duplicate episodes (keep only first 22)
        if len(current_episodes) > len(wurl_episodes):
            duplicate_ids = [ep['id'] for ep in current_episodes[len(wurl_episodes):]]
            cur.execute("DELETE FROM episodes WHERE id = ANY(%s)", (duplicate_ids,))
            print(f"Deleted {len(duplicate_ids)} duplicate episodes")
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully updated {len(wurl_episodes)} Longstreet episodes")
        
        # Verify the updates
        cur.execute("SELECT id, title, content_url FROM episodes WHERE series_id = 49 ORDER BY episode_number")
        updated_episodes = cur.fetchall()
        
        print(f"\nFinal episode count: {len(updated_episodes)}")
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
    print("🔧 Fixing Longstreet episodes with Wurl metadata...")
    update_longstreet_episodes()
    print("Done!") 