#!/usr/bin/env python3
"""
Script to search ALL Wurl metadata files for Petrocelli data.
"""

import os
import pandas as pd
import glob

def search_all_wurl_files():
    """Search all Wurl metadata files for Petrocelli data."""
    print("🔍 SEARCHING ALL WURL METADATA FILES FOR PETROCELLI")
    print("=" * 60)
    
    # Find all Excel files in the project
    excel_files = []
    for root, dirs, files in os.walk('..'):
        for file in files:
            if file.endswith(('.xlsx', '.xls')) and 'wurl' in file.lower():
                excel_files.append(os.path.join(root, file))
    
    print(f"Found {len(excel_files)} Excel files with 'wurl' in the name:")
    for file in excel_files:
        print(f"  - {file}")
    
    all_petrocelli_data = []
    
    for file_path in excel_files:
        try:
            print(f"\n📖 Loading: {os.path.basename(file_path)}")
            df = pd.read_excel(file_path)
            
            # Show columns for reference
            print(f"  Columns: {list(df.columns)}")
            
            # Look for Petrocelli in different ways
            petrocelli_matches = []
            
            # Check Series Name column
            if 'Series Name' in df.columns:
                # Case insensitive search
                series_matches = df[df['Series Name'].astype(str).str.contains('petrocelli', case=False, na=False)]
                petrocelli_matches.extend(series_matches.index.tolist())
                print(f"  Found {len(series_matches)} matches in 'Series Name' column")
            
            # Check Title column
            if 'Title' in df.columns:
                title_matches = df[df['Title'].astype(str).str.contains('petrocelli', case=False, na=False)]
                petrocelli_matches.extend(title_matches.index.tolist())
                print(f"  Found {len(title_matches)} matches in 'Title' column")
            
            # Check Internal Title column
            if 'Internal Title' in df.columns:
                internal_matches = df[df['Internal Title'].astype(str).str.contains('petrocelli', case=False, na=False)]
                petrocelli_matches.extend(internal_matches.index.tolist())
                print(f"  Found {len(internal_matches)} matches in 'Internal Title' column")
            
            # Remove duplicates
            petrocelli_matches = list(set(petrocelli_matches))
            
            if petrocelli_matches:
                print(f"  ✅ Found {len(petrocelli_matches)} Petrocelli entries!")
                
                for idx in petrocelli_matches:
                    row = df.iloc[idx]
                    print(f"    Entry {idx + 1}:")
                    print(f"      Title: {row.get('Title', 'N/A')}")
                    print(f"      Series Name: {row.get('Series Name', 'N/A')}")
                    print(f"      Internal Title: {row.get('Internal Title', 'N/A')}")
                    print(f"      Video Filename: {row.get('Video Filename', 'N/A')}")
                    print(f"      Type: {row.get('Type', 'N/A')}")
                    print(f"      Entry Type: {row.get('Entry Type', 'N/A')}")
                    print(f"      Season/Episode: {row.get('Season Number', 'N/A')}/{row.get('Episode Number', 'N/A')}")
                    print("      " + "-" * 40)
                    
                    all_petrocelli_data.append({
                        'file': os.path.basename(file_path),
                        'file_path': file_path,
                        'row_index': idx,
                        'title': row.get('Title', ''),
                        'series_name': row.get('Series Name', ''),
                        'internal_title': row.get('Internal Title', ''),
                        'video_filename': row.get('Video Filename', ''),
                        'type': row.get('Type', ''),
                        'entry_type': row.get('Entry Type', ''),
                        'season_number': row.get('Season Number', ''),
                        'episode_number': row.get('Episode Number', ''),
                        'description': row.get('Description', ''),
                        'short_description': row.get('Short Description', ''),
                        'release_date': row.get('Release Date', ''),
                        'artwork_filename': row.get('Artwork Filename', ''),
                        'series_artwork_filename': row.get('Series Artwork Filename', ''),
                        'genre_value': row.get('Genre Value', ''),
                        'rating_value': row.get('Rating Value', '')
                    })
            else:
                print("  ❌ No Petrocelli entries found")
                
        except Exception as e:
            print(f"  ❌ Error reading {os.path.basename(file_path)}: {e}")
    
    print(f"\n📊 FINAL SUMMARY:")
    print("=" * 40)
    print(f"Total Petrocelli entries found: {len(all_petrocelli_data)}")
    
    if all_petrocelli_data:
        print(f"\n📋 ALL PETROCELLI ENTRIES:")
        for i, entry in enumerate(all_petrocelli_data, 1):
            print(f"  {i}. {entry['title']}")
            print(f"     File: {entry['file']}")
            print(f"     Series: {entry['series_name']}")
            print(f"     Video: {entry['video_filename']}")
            print(f"     Type: {entry['type']} / {entry['entry_type']}")
            print(f"     Season/Episode: {entry['season_number']}/{entry['episode_number']}")
            print()
    else:
        print("❌ No Petrocelli data found in any Wurl files")
    
    return all_petrocelli_data

if __name__ == "__main__":
    data = search_all_wurl_files() 