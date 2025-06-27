#!/usr/bin/env python3
"""
Script to find Petrocelli episode video filenames from all Wurl metadata files (robust version).
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
                # Convert Series Name to string and handle NaN values
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                df_petrocelli = df[df['Series Name'].str.strip().str.lower() == 'petrocelli']
                
                for _, row in df_petrocelli.iterrows():
                    title = str(row.get('Title', ''))
                    video_filename = str(row.get('Video Filename', ''))
                    season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                    episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                    
                    if video_filename and video_filename.strip() and video_filename.strip() != 'nan':
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
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"  ❌ Could not read {file} with any encoding")
                continue
            
            # Check if Petrocelli episodes exist in this file
            if 'Series Name' in df.columns:
                # Convert Series Name to string and handle NaN values
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                df_petrocelli = df[df['Series Name'].str.strip().str.lower() == 'petrocelli']
                
                for _, row in df_petrocelli.iterrows():
                    title = str(row.get('Title', ''))
                    video_filename = str(row.get('Video Filename', ''))
                    
                    # Handle season and episode numbers more carefully
                    try:
                        season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                    except (ValueError, TypeError):
                        season = 1
                    
                    try:
                        episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                    except (ValueError, TypeError):
                        episode = 1
                    
                    if video_filename and video_filename.strip() and video_filename.strip() != 'nan':
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
    else:
        print("\n❌ No Petrocelli episodes with video filenames found in any files.")
    
    return petrocelli_episodes

if __name__ == "__main__":
    find_petrocelli_video_filenames() 