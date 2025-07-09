#!/usr/bin/env python3
"""
Script to check what episodes are available in Wurl metadata files for Bonanza and Ghost Squad
"""

import pandas as pd
import os
import glob

def check_metadata_episodes():
    """Check what episodes are available in Wurl metadata files."""
    print("🔍 Checking Wurl metadata files for Bonanza and Ghost Squad episodes")
    print("=" * 70)
    
    # Find all Wurl metadata files
    wurl_files = []
    for pattern in [
        "Wurl - File Upload Metadata_Version 7.0.*.xlsx",
        "Wurl - File Upload Metadata_Version 7.0.*.csv",
        "Wurl-File-Upload-Metadata_Version-7.0.*.xlsx"
    ]:
        wurl_files.extend(glob.glob(pattern))
    
    print(f"Found {len(wurl_files)} Wurl metadata files")
    
    bonanza_episodes = []
    ghost_squad_episodes = []
    
    for file in sorted(wurl_files):
        print(f"\n📁 Processing: {file}")
        
        try:
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, encoding='utf-8')
            
            # Check for Bonanza episodes
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                
                # Bonanza episodes
                bonanza_df = df[df['Series Name'].str.strip().str.lower() == 'bonanza']
                if len(bonanza_df) > 0:
                    print(f"  🎬 Found {len(bonanza_df)} Bonanza episodes")
                    for _, row in bonanza_df.iterrows():
                        title = str(row.get('Title', '')).strip()
                        video_filename = str(row.get('Video Filename', '')).strip()
                        artwork_filename = str(row.get('Artwork Filename', '')).strip()
                        
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
                            'artwork_filename': artwork_filename if artwork_filename != 'nan' else '',
                            'description': str(row.get('Description', '')).strip(),
                            'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60
                        }
                        
                        bonanza_episodes.append(episode_info)
                        print(f"    S{season:02d}E{episode:02d} - {title}")
                
                # Ghost Squad episodes
                ghost_squad_df = df[df['Series Name'].str.strip().str.lower() == 'ghost squad']
                if len(ghost_squad_df) > 0:
                    print(f"  👻 Found {len(ghost_squad_df)} Ghost Squad episodes")
                    for _, row in ghost_squad_df.iterrows():
                        title = str(row.get('Title', '')).strip()
                        video_filename = str(row.get('Video Filename', '')).strip()
                        artwork_filename = str(row.get('Artwork Filename', '')).strip()
                        
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
                            'artwork_filename': artwork_filename if artwork_filename != 'nan' else '',
                            'description': str(row.get('Description', '')).strip(),
                            'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60
                        }
                        
                        ghost_squad_episodes.append(episode_info)
                        print(f"    S{season:02d}E{episode:02d} - {title}")
        
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    # Show summary
    print(f"\n📊 SUMMARY")
    print("=" * 70)
    
    # Bonanza summary
    if bonanza_episodes:
        # Remove duplicates based on season/episode
        unique_bonanza = {}
        for ep in bonanza_episodes:
            key = (ep['season'], ep['episode'])
            if key not in unique_bonanza:
                unique_bonanza[key] = ep
        
        sorted_bonanza = sorted(unique_bonanza.values(), key=lambda x: (x['season'], x['episode']))
        
        print(f"\n🎬 BONANZA: Found {len(sorted_bonanza)} unique episodes")
        print("-" * 50)
        for ep in sorted_bonanza:
            status = "✅" if ep['video_filename'] else "❌"
            print(f"{status} S{ep['season']:02d}E{ep['episode']:02d} - {ep['title']}")
            if ep['video_filename']:
                print(f"     Video: {ep['video_filename']}")
            if ep['artwork_filename']:
                print(f"     Artwork: {ep['artwork_filename']}")
            print(f"     Runtime: {ep['runtime']} min")
            print()
    else:
        print(f"\n🎬 BONANZA: No episodes found in metadata files")
    
    # Ghost Squad summary
    if ghost_squad_episodes:
        # Remove duplicates based on season/episode
        unique_ghost_squad = {}
        for ep in ghost_squad_episodes:
            key = (ep['season'], ep['episode'])
            if key not in unique_ghost_squad:
                unique_ghost_squad[key] = ep
        
        sorted_ghost_squad = sorted(unique_ghost_squad.values(), key=lambda x: (x['season'], x['episode']))
        
        print(f"\n👻 GHOST SQUAD: Found {len(sorted_ghost_squad)} unique episodes")
        print("-" * 50)
        for ep in sorted_ghost_squad:
            status = "✅" if ep['video_filename'] else "❌"
            print(f"{status} S{ep['season']:02d}E{ep['episode']:02d} - {ep['title']}")
            if ep['video_filename']:
                print(f"     Video: {ep['video_filename']}")
            if ep['artwork_filename']:
                print(f"     Artwork: {ep['artwork_filename']}")
            print(f"     Runtime: {ep['runtime']} min")
            print()
    else:
        print(f"\n👻 GHOST SQUAD: No episodes found in metadata files")
    
    return {
        'bonanza': bonanza_episodes,
        'ghost_squad': ghost_squad_episodes
    }

if __name__ == "__main__":
    check_metadata_episodes() 