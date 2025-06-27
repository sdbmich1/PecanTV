#!/usr/bin/env python3
"""
Script to find Petrocelli episode video filenames from all Wurl metadata files.
"""

import os
import pandas as pd
import glob

def find_petrocelli_video_filenames():
    """Search all Wurl metadata files for Petrocelli episodes and their video filenames."""
    
    # Find all Wurl metadata files
    excel_files = glob.glob("Wurl*.xlsx")
    csv_files = glob.glob("Wurl*.csv")
    
    print("🎬 Searching for Petrocelli Video Filenames")
    print("=" * 50)
    
    petrocelli_episodes = {}
    
    # Process Excel files
    for file in excel_files:
        try:
            print(f"📖 Reading {file}...")
            df = pd.read_excel(file)
            
            # Check if Petrocelli episodes exist in this file
            if 'Series Name' in df.columns:
                df_petrocelli = df[df['Series Name'].str.strip().str.lower() == 'petrocelli']
                
                for _, row in df_petrocelli.iterrows():
                    title = row['Title']
                    video_filename = row.get('Video Filename', '')
                    season = row.get('Season Number', 1)
                    episode = row.get('Episode Number', 1)
                    
                    if video_filename and video_filename.strip():
                        key = f"S{season:02d}E{episode:02d} - {title}"
                        if key not in petrocelli_episodes:
                            petrocelli_episodes[key] = {
                                'title': title,
                                'video_filename': video_filename.strip(),
                                'season': season,
                                'episode': episode,
                                'source_file': file
                            }
                            print(f"  ✅ Found: {key}")
                            print(f"     Video Filename: {video_filename.strip()}")
                            print(f"     Source: {file}")
                            print()
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    # Process CSV files
    for file in csv_files:
        try:
            print(f"📖 Reading {file}...")
            df = pd.read_csv(file)
            
            # Check if Petrocelli episodes exist in this file
            if 'Series Name' in df.columns:
                df_petrocelli = df[df['Series Name'].str.strip().str.lower() == 'petrocelli']
                
                for _, row in df_petrocelli.iterrows():
                    title = row['Title']
                    video_filename = row.get('Video Filename', '')
                    season = row.get('Season Number', 1)
                    episode = row.get('Episode Number', 1)
                    
                    if video_filename and video_filename.strip():
                        key = f"S{season:02d}E{episode:02d} - {title}"
                        if key not in petrocelli_episodes:
                            petrocelli_episodes[key] = {
                                'title': title,
                                'video_filename': video_filename.strip(),
                                'season': season,
                                'episode': episode,
                                'source_file': file
                            }
                            print(f"  ✅ Found: {key}")
                            print(f"     Video Filename: {video_filename.strip()}")
                            print(f"     Source: {file}")
                            print()
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    # Summary
    print("📊 Summary:")
    print("-" * 30)
    print(f"Total Petrocelli episodes found with video filenames: {len(petrocelli_episodes)}")
    
    if petrocelli_episodes:
        print("\n📋 All Petrocelli Episodes with Video Filenames:")
        print("-" * 50)
        for key, data in sorted(petrocelli_episodes.items()):
            print(f"  {key}")
            print(f"    Video Filename: {data['video_filename']}")
            print(f"    Source: {data['source_file']}")
            print()
    
    return petrocelli_episodes

if __name__ == "__main__":
    find_petrocelli_video_filenames() 