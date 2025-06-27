#!/usr/bin/env python3
"""
Script to search for Bonanza data across all Wurl metadata files.
"""

import pandas as pd
import glob
import os

def search_bonanza():
    """Search for Bonanza data in all Wurl files."""
    print("🔍 Searching for Bonanza in all Wurl metadata files")
    print("=" * 60)
    
    # Find all Wurl metadata files
    excel_files = glob.glob("Wurl*.xlsx")
    csv_files = glob.glob("Wurl*.csv")
    
    print(f"📁 Found {len(excel_files)} Excel files and {len(csv_files)} CSV files")
    
    all_files = excel_files + csv_files
    found_data = []
    
    for file_path in all_files:
        print(f"\n🔍 Checking: {file_path}")
        
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                # Try different encodings for CSV files
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"  ❌ Could not read {file_path}")
                    continue
            
            # Check if the file has the expected columns
            if 'Series Name' not in df.columns:
                print(f"  ⚠️  No 'Series Name' column found")
                continue
            
            # Convert Series Name to string and handle NaN values
            df['Series Name'] = df['Series Name'].astype(str).fillna('')
            
            # Search for Bonanza
            bonanza_mask = df['Series Name'].str.contains('Bonanza', case=False, na=False)
            bonanza_data = df[bonanza_mask]
            
            if not bonanza_data.empty:
                print(f"  ✅ Found {len(bonanza_data)} Bonanza entries!")
                
                for _, row in bonanza_data.iterrows():
                    found_data.append({
                        'file': file_path,
                        'series_name': row['Series Name'],
                        'title': row.get('Title', ''),
                        'episode_number': row.get('Episode Number', ''),
                        'video_filename': row.get('Video Filename', ''),
                        'artwork_filename': row.get('Artwork Filename', ''),
                        'content_url': row.get('Content URL', ''),
                        'poster_url': row.get('Poster URL', '')
                    })
                    
                    print(f"    - {row['Series Name']}: {row.get('Title', '')} (E{row.get('Episode Number', '')})")
            else:
                print(f"  ❌ No Bonanza data found")
                
        except Exception as e:
            print(f"  ❌ Error reading {file_path}: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total Bonanza entries found: {len(found_data)}")
    
    if found_data:
        print(f"\n📋 DETAILED RESULTS:")
        for entry in found_data:
            print(f"  File: {entry['file']}")
            print(f"    Series: {entry['series_name']}")
            print(f"    Title: {entry['title']}")
            print(f"    Episode: {entry['episode_number']}")
            print(f"    Video: {entry['video_filename']}")
            print(f"    Artwork: {entry['artwork_filename']}")
            print(f"    Content URL: {entry['content_url']}")
            print(f"    Poster URL: {entry['poster_url']}")
            print()
    else:
        print("❌ No Bonanza data found in any Wurl files")

if __name__ == "__main__":
    search_bonanza() 