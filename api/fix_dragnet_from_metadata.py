#!/usr/bin/env python3
"""
Fix Dragnet episode URLs using actual video filenames from Wurl metadata
"""

import pandas as pd
import requests
from database import get_db
from models import Episode
from sqlalchemy.orm import Session
import os

def download_metadata_file():
    """Download the Wurl metadata file from Dropbox"""
    url = "https://www.dropbox.com/scl/fi/acfckku34hglcfyzju91i/Wurl-File-Upload-Metadata_Version-7.0.34.csv?rlkey=2ctujh7e6jzgbsqj5gtdq103n&dl=1"
    
    print("📥 Downloading Wurl metadata file...")
    response = requests.get(url)
    
    if response.status_code == 200:
        # Save to temporary file
        with open("temp_wurl_metadata.csv", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Downloaded metadata file")
        return "temp_wurl_metadata.csv"
    else:
        print(f"❌ Failed to download file: {response.status_code}")
        return None

def extract_dragnet_filenames(csv_file):
    """Extract Dragnet video filenames from the CSV"""
    
    print("🔍 Reading Dragnet metadata from CSV...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Filter for Dragnet episodes
        dragnet_rows = df[df['Series Name'].str.contains('Dragnet', case=False, na=False)]
        
        print(f"Found {len(dragnet_rows)} Dragnet entries in metadata")
        
        # Extract episode information
        dragnet_episodes = []
        for _, row in dragnet_rows.iterrows():
            series_name = row.get('Series Name', '')
            title = row.get('Title', '')
            video_filename = row.get('Video Filename', '')
            
            # Try to extract episode number from title
            episode_number = None
            if 'Episode' in title:
                try:
                    import re
                    # Look for "Episode X" pattern - handle both numbers and words
                    match = re.search(r'Episode\s+(\d+)', title)
                    if match:
                        episode_number = int(match.group(1))
                    else:
                        # Handle "Episode One", "Episode Two", etc.
                        word_to_number = {
                            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15
                        }
                        for word, num in word_to_number.items():
                            if word in title.lower():
                                episode_number = num
                                break
                except:
                    pass
            
            dragnet_episodes.append({
                'series_name': series_name,
                'title': title,
                'video_filename': video_filename.strip() if video_filename else '',
                'episode_number': episode_number
            })
        
        print(f"Extracted {len(dragnet_episodes)} Dragnet episodes with video filenames")
        
        # Show what we found
        for episode in dragnet_episodes:
            print(f"  - {episode['title']} (Episode {episode['episode_number']}): {episode['video_filename']}")
        
        return dragnet_episodes
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

def update_dragnet_database(dragnet_episodes):
    """Update the database with correct video filenames"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("\n🔧 Updating Dragnet episodes in database...")
        
        # Get Dragnet series ID
        dragnet_series = db.query(Episode).filter(
            Episode.series_id == 68  # Dragnet series ID
        ).first()
        
        if not dragnet_series:
            print("❌ Dragnet series not found in database")
            return
        
        print(f"✅ Found Dragnet series (ID: 68)")
        
        # Get all Dragnet episodes
        dragnet_db_episodes = db.query(Episode).filter(
            Episode.series_id == 68
        ).all()
        
        print(f"Found {len(dragnet_db_episodes)} Dragnet episodes in database")
        
        # Create mapping from episode number to video filename
        filename_mapping = {}
        for episode in dragnet_episodes:
            if episode['episode_number'] and episode['video_filename']:
                filename_mapping[episode['episode_number']] = episode['video_filename']
        
        print(f"Created mapping for {len(filename_mapping)} episodes")
        
        # Update database episodes
        updated_count = 0
        for db_episode in dragnet_db_episodes:
            episode_number = db_episode.episode_number
            
            if episode_number in filename_mapping:
                video_filename = filename_mapping[episode_number]
                
                # Create the content URL
                # Check if it's a local file or GCS URL
                if video_filename.startswith('http'):
                    new_url = video_filename
                else:
                    # Assume it's a local file in the dragnet folder
                    new_url = f"http://localhost:8000/pecantv_series/dragnet/{video_filename}"
                
                # Update the episode
                old_url = db_episode.content_url
                db_episode.content_url = new_url
                
                print(f"✅ Updated Episode {episode_number}: {db_episode.title}")
                print(f"   Old URL: {old_url}")
                print(f"   New URL: {new_url}")
                print(f"   Video Filename: {video_filename}")
                
                updated_count += 1
            else:
                print(f"⚠️  No video filename found for Episode {episode_number}: {db_episode.title}")
                # Remove invalid URL
                db_episode.content_url = ""
        
        # Commit changes
        db.commit()
        print(f"\n✅ Updated {updated_count} Dragnet episodes")
        
        # Verify the fix
        print("\nVerification:")
        fixed_episodes = db.query(Episode).filter(
            Episode.series_id == 68
        ).all()
        
        for episode in fixed_episodes:
            print(f"  - {episode.title}: {episode.content_url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def cleanup_temp_file(csv_file):
    """Clean up temporary file"""
    if csv_file and os.path.exists(csv_file):
        os.remove(csv_file)
        print("🧹 Cleaned up temporary file")

def main():
    """Main function to fix Dragnet episodes"""
    
    print("🎬 Fixing Dragnet Episodes from Wurl Metadata")
    print("=" * 50)
    
    # Download metadata file
    csv_file = download_metadata_file()
    if not csv_file:
        return
    
    try:
        # Extract Dragnet filenames
        dragnet_episodes = extract_dragnet_filenames(csv_file)
        
        if dragnet_episodes:
            # Update database
            update_dragnet_database(dragnet_episodes)
        else:
            print("❌ No Dragnet episodes found in metadata")
    
    finally:
        # Clean up
        cleanup_temp_file(csv_file)

if __name__ == "__main__":
    main() 