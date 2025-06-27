#!/usr/bin/env python3
"""
Script to search all Wurl metadata files for Bonanza episodes with episode numbers 1-13.
"""

import pandas as pd
import glob

def search_for_bonanza_1_13():
    """Search all Wurl metadata files for Bonanza episodes 1-13."""
    
    # Find all Wurl metadata files
    excel_files = glob.glob("Wurl*.xlsx")
    csv_files = glob.glob("Wurl*.csv")
    
    print("🔍 Searching ALL Wurl metadata files for Bonanza episodes 1-13...")
    print("=" * 70)
    
    found_episodes = []
    
    for file in excel_files + csv_files:
        try:
            print(f"\n📖 Reading {file}...")
            
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                # Try different encodings for CSV
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"  ❌ Could not read {file} with any encoding")
                    continue
            
            # Check for Bonanza episodes
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                bonanza_df = df[df['Series Name'].str.strip().str.lower() == 'bonanza']
                
                if len(bonanza_df) > 0:
                    print(f"  🎬 Found {len(bonanza_df)} Bonanza episodes in {file}")
                    
                    for _, row in bonanza_df.iterrows():
                        title = str(row.get('Title', '')).strip()
                        video_filename = str(row.get('Video Filename', '')).strip()
                        
                        # Handle season and episode numbers
                        try:
                            season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                        except (ValueError, TypeError):
                            season = 1
                        
                        try:
                            episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                        except (ValueError, TypeError):
                            episode = 1
                        
                        # Check if this is episodes 1-13
                        if 1 <= episode <= 13:
                            episode_info = {
                                'file': file,
                                'title': title,
                                'season': season,
                                'episode': episode,
                                'video_filename': video_filename if video_filename != 'nan' else '',
                                'artwork_filename': str(row.get('Artwork Filename', '')).strip() if str(row.get('Artwork Filename', '')).strip() != 'nan' else ''
                            }
                            
                            found_episodes.append(episode_info)
                            
                            print(f"    ✅ S{season:02d}E{episode:02d} - {title}")
                            if video_filename and video_filename != 'nan':
                                print(f"      Video: {video_filename}")
                            else:
                                print(f"      Video: MISSING")
            
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    # Show summary
    print(f"\n📊 Summary of Bonanza episodes 1-13 found:")
    print("=" * 50)
    
    if found_episodes:
        # Sort by episode number
        sorted_episodes = sorted(found_episodes, key=lambda x: x['episode'])
        
        print(f"Found {len(sorted_episodes)} Bonanza episodes 1-13 across all files:")
        print("-" * 50)
        
        for ep in sorted_episodes:
            status = "✅" if ep['video_filename'] else "❌"
            print(f"{status} S{ep['season']:02d}E{ep['episode']:02d} - {ep['title']}")
            if ep['video_filename']:
                print(f"     Video: {ep['video_filename']}")
            if ep['artwork_filename']:
                print(f"     Artwork: {ep['artwork_filename']}")
            print(f"     File: {ep['file']}")
            print()
        
        # Show which files contain episodes 1-13
        files_with_1_13 = set(ep['file'] for ep in found_episodes)
        print(f"Files containing episodes 1-13:")
        for file in sorted(files_with_1_13):
            print(f"  - {file}")
    else:
        print("❌ No Bonanza episodes 1-13 found in any metadata files!")
        print("\nThis means the metadata files don't contain the episodes that are in the database.")
        print("The database has episodes 1-13, but metadata files only have episodes 20-32.")

if __name__ == "__main__":
    search_for_bonanza_1_13() 