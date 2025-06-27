#!/usr/bin/env python3
"""
Script to show all Petrocelli data from Wurl metadata files.
"""

import os
import pandas as pd

# Paths to the Wurl metadata files
WURL_FILES = [
    '../Wurl-File-Upload-Metadata_Version-7.0.40.xlsx',
    '../Wurl-File-Upload-Metadata_Version-7.0.41.xlsx'
]

SERIES_NAME = 'Petrocelli'

def check_wurl_petrocelli_data():
    """Show all Petrocelli data from Wurl metadata files."""
    print("🔍 CHECKING WURL METADATA FOR PETROCELLI DATA")
    print("=" * 60)
    
    all_petrocelli_data = []
    
    for file in WURL_FILES:
        if not os.path.exists(file):
            print(f"❌ File not found: {file}")
            continue
            
        print(f"\n📖 Loading from: {file}")
        df = pd.read_excel(file)
        
        # Show all columns for reference
        print(f"  Available columns: {list(df.columns)}")
        
        # Filter for Petrocelli content (case insensitive)
        df_petrocelli = df[df['Series Name'].str.strip().str.lower() == SERIES_NAME.lower()]
        
        print(f"  Found {len(df_petrocelli)} Petrocelli entries")
        
        if len(df_petrocelli) > 0:
            print(f"\n  📋 PETROCELLI ENTRIES IN {os.path.basename(file)}:")
            print("  " + "=" * 80)
            
            for idx, row in df_petrocelli.iterrows():
                print(f"  Entry {idx + 1}:")
                print(f"    Title: {row.get('Title', 'N/A')}")
                print(f"    Series Name: {row.get('Series Name', 'N/A')}")
                print(f"    Type: {row.get('Type', 'N/A')}")
                print(f"    Season Number: {row.get('Season Number', 'N/A')}")
                print(f"    Episode Number: {row.get('Episode Number', 'N/A')}")
                print(f"    Video Filename: {row.get('Video Filename', 'N/A')}")
                print(f"    Content URL: {row.get('Content URL', 'N/A')}")
                print(f"    Poster URL: {row.get('Poster URL', 'N/A')}")
                print(f"    Description: {row.get('Description', 'N/A')[:100]}...")
                print(f"    Runtime: {row.get('Runtime', 'N/A')}")
                print(f"    Genre: {row.get('Genre', 'N/A')}")
                print(f"    Rating: {row.get('Rating', 'N/A')}")
                print(f"    Air Date: {row.get('Air Date', 'N/A')}")
                print("    " + "-" * 60)
                
                all_petrocelli_data.append({
                    'file': os.path.basename(file),
                    'row_index': idx,
                    'title': row.get('Title', ''),
                    'type': row.get('Type', ''),
                    'season_number': row.get('Season Number', ''),
                    'episode_number': row.get('Episode Number', ''),
                    'video_filename': row.get('Video Filename', ''),
                    'content_url': row.get('Content URL', ''),
                    'poster_url': row.get('Poster URL', ''),
                    'description': row.get('Description', ''),
                    'runtime': row.get('Runtime', ''),
                    'genre': row.get('Genre', ''),
                    'rating': row.get('Rating', ''),
                    'air_date': row.get('Air Date', '')
                })
        else:
            print("  ❌ No Petrocelli entries found")
    
    print(f"\n📊 SUMMARY:")
    print("=" * 40)
    print(f"Total Petrocelli entries found: {len(all_petrocelli_data)}")
    
    if all_petrocelli_data:
        print(f"\n📋 ALL PETROCELLI ENTRIES:")
        for i, entry in enumerate(all_petrocelli_data, 1):
            print(f"  {i}. {entry['title']} (Type: {entry['type']})")
            print(f"     File: {entry['file']}, Row: {entry['row_index']}")
            print(f"     Video: {entry['video_filename']}")
            print(f"     Season/Episode: {entry['season_number']}/{entry['episode_number']}")
            print()
    
    return all_petrocelli_data

if __name__ == "__main__":
    data = check_wurl_petrocelli_data() 