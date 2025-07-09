#!/usr/bin/env python3
"""
Check which Dragnet video files are missing and provide a comprehensive list
"""

import pandas as pd
import requests
import os
from database import get_db
from models import Episode

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

def get_dragnet_metadata(csv_file):
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
        
        return dragnet_episodes
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

def get_database_episodes():
    """Get Dragnet episodes from database"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get all Dragnet episodes
        dragnet_episodes = db.query(Episode).filter(
            Episode.series_id == 68  # Dragnet series ID
        ).all()
        
        db_episodes = []
        for episode in dragnet_episodes:
            db_episodes.append({
                'id': episode.id,
                'title': episode.title,
                'episode_number': episode.episode_number,
                'content_url': episode.content_url
            })
        
        return db_episodes
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return []
    finally:
        db.close()

def get_local_files():
    """Get list of files in the dragnet folder"""
    
    dragnet_dir = "../pecantv_series/dragnet/"
    local_files = []
    
    if os.path.exists(dragnet_dir):
        for file in os.listdir(dragnet_dir):
            if file.endswith('.mp4'):
                local_files.append(file)
    
    return local_files

def analyze_missing_files():
    """Analyze which files are missing"""
    
    print("🎬 Analyzing Missing Dragnet Files")
    print("=" * 50)
    
    # Download metadata file
    csv_file = download_metadata_file()
    if not csv_file:
        return
    
    try:
        # Get data from different sources
        metadata_episodes = get_dragnet_metadata(csv_file)
        db_episodes = get_database_episodes()
        local_files = get_local_files()
        
        print(f"\n📊 Summary:")
        print(f"  - Metadata entries: {len(metadata_episodes)}")
        print(f"  - Database episodes: {len(db_episodes)}")
        print(f"  - Local files: {len(local_files)}")
        
        # Create mapping from episode number to video filename
        metadata_mapping = {}
        for episode in metadata_episodes:
            if episode['episode_number'] and episode['video_filename']:
                metadata_mapping[episode['episode_number']] = episode['video_filename']
        
        print(f"\n📋 Metadata Video Filenames:")
        for episode_num in sorted(metadata_mapping.keys()):
            filename = metadata_mapping[episode_num]
            status = "✅ Present" if filename in local_files else "❌ Missing"
            print(f"  Episode {episode_num}: {filename} - {status}")
        
        print(f"\n📁 Local Files in dragnet folder:")
        for file in sorted(local_files):
            print(f"  - {file}")
        
        print(f"\n🗄️ Database Episodes:")
        for episode in sorted(db_episodes, key=lambda x: x['episode_number']):
            print(f"  Episode {episode['episode_number']}: {episode['title']}")
            if episode['content_url']:
                # Extract filename from URL
                filename = episode['content_url'].split('/')[-1]
                status = "✅ Present" if filename in local_files else "❌ Missing"
                print(f"    URL: {episode['content_url']} - {status}")
            else:
                print(f"    URL: None")
        
        # Find missing files
        missing_files = []
        for episode_num, filename in metadata_mapping.items():
            if filename not in local_files:
                missing_files.append({
                    'episode_number': episode_num,
                    'filename': filename,
                    'title': next((ep['title'] for ep in metadata_episodes if ep['episode_number'] == episode_num), 'Unknown')
                })
        
        print(f"\n❌ Missing Files ({len(missing_files)}):")
        for missing in missing_files:
            print(f"  Episode {missing['episode_number']}: {missing['filename']} ({missing['title']})")
        
        # Find orphaned local files
        orphaned_files = []
        for file in local_files:
            if file not in metadata_mapping.values():
                orphaned_files.append(file)
        
        if orphaned_files:
            print(f"\n⚠️ Orphaned Files ({len(orphaned_files)}):")
            for file in orphaned_files:
                print(f"  - {file}")
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"  - Total episodes in database: {len(db_episodes)}")
        print(f"  - Episodes with metadata: {len(metadata_mapping)}")
        print(f"  - Files present locally: {len(local_files)}")
        print(f"  - Files missing: {len(missing_files)}")
        print(f"  - Orphaned files: {len(orphaned_files)}")
        
        if missing_files:
            print(f"\n🔧 Action Required:")
            print(f"  Upload these {len(missing_files)} files to ../pecantv_series/dragnet/:")
            for missing in missing_files:
                print(f"    - {missing['filename']}")
        
    finally:
        # Clean up
        if csv_file and os.path.exists(csv_file):
            os.remove(csv_file)
            print("\n🧹 Cleaned up temporary file")

if __name__ == "__main__":
    analyze_missing_files() 