#!/usr/bin/env python3
"""
Script to search all Wurl metadata files for Bonanza episodes and show their details.
"""

import pandas as pd
import glob

def find_all_bonanza_metadata():
    """Search all Wurl metadata files for Bonanza episodes."""
    
    # Find all Wurl metadata files
    excel_files = glob.glob("Wurl*.xlsx")
    csv_files = glob.glob("Wurl*.csv")
    
    print("🔍 Searching ALL Wurl metadata files for Bonanza episodes...")
    print("=" * 70)
    
    all_bonanza_episodes = []
    
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
                        
                        episode_info = {
                            'file': file,
                            'title': title,
                            'season': season,
                            'episode': episode,
                            'video_filename': video_filename if video_filename != 'nan' else '',
                            'artwork_filename': str(row.get('Artwork Filename', '')).strip() if str(row.get('Artwork Filename', '')).strip() != 'nan' else ''
                        }
                        
                        all_bonanza_episodes.append(episode_info)
                        
                        print(f"    S{season:02d}E{episode:02d} - {title}")
                        if video_filename and video_filename != 'nan':
                            print(f"      Video: {video_filename}")
                        else:
                            print(f"      Video: MISSING")
            
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    # Show summary
    print(f"\n📊 Summary of ALL Bonanza episodes found:")
    print("=" * 50)
    
    if all_bonanza_episodes:
        # Group by season/episode to remove duplicates
        unique_episodes = {}
        for ep in all_bonanza_episodes:
            key = (ep['season'], ep['episode'])
            if key not in unique_episodes:
                unique_episodes[key] = ep
        
        # Sort by season and episode
        sorted_episodes = sorted(unique_episodes.values(), key=lambda x: (x['season'], x['episode']))
        
        print(f"Found {len(sorted_episodes)} unique Bonanza episodes across all files:")
        print("-" * 50)
        
        for ep in sorted_episodes:
            status = "✅" if ep['video_filename'] else "❌"
            print(f"{status} S{ep['season']:02d}E{ep['episode']:02d} - {ep['title']}")
            if ep['video_filename']:
                print(f"     Video: {ep['video_filename']}")
            if ep['artwork_filename']:
                print(f"     Artwork: {ep['artwork_filename']}")
            print()
        
        # Show episode number ranges
        seasons = set(ep['season'] for ep in sorted_episodes)
        for season in sorted(seasons):
            season_episodes = [ep for ep in sorted_episodes if ep['season'] == season]
            episode_numbers = [ep['episode'] for ep in season_episodes]
            print(f"Season {season}: Episodes {min(episode_numbers)}-{max(episode_numbers)} ({len(season_episodes)} episodes)")
    else:
        print("❌ No Bonanza episodes found in any metadata files!")

if __name__ == "__main__":
    find_all_bonanza_metadata() 