#!/usr/bin/env python3
"""
Script to check Wurl metadata for missing episodes
"""

import pandas as pd
import glob

def main():
    print("🔍 Checking Wurl metadata for missing episodes...")
    print("=" * 60)
    
    # Find Wurl metadata files
    wurl_files = []
    for pattern in [
        "Wurl - File Upload Metadata_Version 7.0.*.xlsx",
        "Wurl - File Upload Metadata_Version 7.0.*.csv",
        "Wurl-File-Upload-Metadata_Version-7.0.*.xlsx"
    ]:
        wurl_files.extend(glob.glob(pattern))
    
    my_fair_deadly_entries = []
    eyewitness_entries = []
    
    for file in sorted(wurl_files):
        try:
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, encoding='utf-8')
            
            if 'Title' in df.columns:
                df['Title'] = df['Title'].astype(str).fillna('')
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                
                # Check for "My Fair Deadly"
                my_fair_deadly_df = df[df['Title'].str.strip().str.lower().str.contains('my fair deadly')]
                for _, row in my_fair_deadly_df.iterrows():
                    entry = {
                        'file': file,
                        'title': str(row.get('Title', '')).strip(),
                        'series_name': str(row.get('Series Name', '')).strip(),
                        'video_filename': str(row.get('Video Filename', '')).strip(),
                        'artwork_filename': str(row.get('Artwork Filename', '')).strip(),
                        'description': str(row.get('Description', '')).strip(),
                        'season': int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1,
                        'episode': int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1,
                        'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60
                    }
                    my_fair_deadly_entries.append(entry)
                
                # Check for "Eyewitness"
                eyewitness_df = df[df['Title'].str.strip().str.lower().str.contains('eyewitness')]
                for _, row in eyewitness_df.iterrows():
                    entry = {
                        'file': file,
                        'title': str(row.get('Title', '')).strip(),
                        'series_name': str(row.get('Series Name', '')).strip(),
                        'video_filename': str(row.get('Video Filename', '')).strip(),
                        'artwork_filename': str(row.get('Artwork Filename', '')).strip(),
                        'description': str(row.get('Description', '')).strip(),
                        'season': int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1,
                        'episode': int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1,
                        'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60
                    }
                    eyewitness_entries.append(entry)
        
        except Exception as e:
            print(f"  ⚠️  Error reading {file}: {e}")
    
    # Show results
    print(f"\n🎬 MY FAIR DEADLY: Found {len(my_fair_deadly_entries)} entries")
    print("-" * 50)
    for entry in my_fair_deadly_entries:
        print(f"Title: {entry['title']}")
        print(f"Series: {entry['series_name']}")
        print(f"Season/Episode: S{entry['season']:02d}E{entry['episode']:02d}")
        print(f"Video: {entry['video_filename']}")
        print(f"Artwork: {entry['artwork_filename']}")
        print(f"Runtime: {entry['runtime']} min")
        print(f"File: {entry['file']}")
        print()
    
    print(f"\n👁️ EYEWITNESS: Found {len(eyewitness_entries)} entries")
    print("-" * 50)
    for entry in eyewitness_entries:
        print(f"Title: {entry['title']}")
        print(f"Series: {entry['series_name']}")
        print(f"Season/Episode: S{entry['season']:02d}E{entry['episode']:02d}")
        print(f"Video: {entry['video_filename']}")
        print(f"Artwork: {entry['artwork_filename']}")
        print(f"Runtime: {entry['runtime']} min")
        print(f"File: {entry['file']}")
        print()

if __name__ == "__main__":
    main() 