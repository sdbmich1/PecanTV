#!/usr/bin/env python3
"""
Script to find all Wurl metadata files that contain 'Commando Cody' data.
"""

import pandas as pd
import glob
import os

def find_commando_cody_files():
    """Find all Wurl metadata files that contain Commando Cody data."""
    print("🔍 Searching for Commando Cody data in Wurl metadata files...")
    print("=" * 60)
    
    # Find all Wurl metadata files with different patterns
    excel_files = glob.glob("Wurl*.xlsx") + glob.glob("Wurl - *.xlsx") + glob.glob("Wurl-File-Upload-Metadata*.xlsx")
    csv_files = glob.glob("Wurl*.csv") + glob.glob("Wurl - *.csv") + glob.glob("Wurl-File-Upload-Metadata*.csv")
    
    commando_cody_files = []
    
    for file in excel_files + csv_files:
        try:
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
                    continue
            
            # Check for series data
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                
                # Look for Commando Cody (case insensitive)
                commando_cody_mask = df['Series Name'].str.contains('Commando Cody', case=False, na=False)
                commando_cody_rows = df[commando_cody_mask]
                
                if len(commando_cody_rows) > 0:
                    commando_cody_files.append({
                        'file': file,
                        'episode_count': len(commando_cody_rows),
                        'series_names': commando_cody_rows['Series Name'].unique().tolist(),
                        'has_video_filenames': len(commando_cody_rows[commando_cody_rows['Video Filename'].notna() & (commando_cody_rows['Video Filename'] != '')]) if 'Video Filename' in df.columns else 0,
                        'has_artwork_filenames': len(commando_cody_rows[commando_cody_rows['Artwork Filename'].notna() & (commando_cody_rows['Artwork Filename'] != '')]) if 'Artwork Filename' in df.columns else 0
                    })
        
        except Exception as e:
            print(f"  ⚠️  Error reading {file}: {e}")
    
    # Display results
    if commando_cody_files:
        print(f"✅ Found Commando Cody data in {len(commando_cody_files)} files:")
        print()
        
        for i, file_info in enumerate(commando_cody_files, 1):
            print(f"{i}. 📁 {file_info['file']}")
            print(f"   📺 Episodes: {file_info['episode_count']}")
            print(f"   🎥 Video filenames: {file_info['has_video_filenames']}")
            print(f"   🖼️  Artwork filenames: {file_info['has_artwork_filenames']}")
            print(f"   📝 Series names found: {', '.join(file_info['series_names'])}")
            print()
        
        # Summary
        total_episodes = sum(f['episode_count'] for f in commando_cody_files)
        total_video = sum(f['has_video_filenames'] for f in commando_cody_files)
        total_artwork = sum(f['has_artwork_filenames'] for f in commando_cody_files)
        
        print("📊 SUMMARY:")
        print(f"   Total files: {len(commando_cody_files)}")
        print(f"   Total episodes: {total_episodes}")
        print(f"   Episodes with video filenames: {total_video}")
        print(f"   Episodes with artwork filenames: {total_artwork}")
        
    else:
        print("❌ No Commando Cody data found in any Wurl metadata files.")
        print("\n🔍 Checking for similar series names...")
        
        # Check for similar names
        similar_names = []
        for file in excel_files + csv_files:
            try:
                if file.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            df = pd.read_csv(file, encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        continue
                
                if 'Series Name' in df.columns:
                    df['Series Name'] = df['Series Name'].astype(str).fillna('')
                    unique_series = df['Series Name'].unique()
                    
                    for series in unique_series:
                        if series and series.strip() and series.strip().lower() != 'nan':
                            if 'commando' in series.lower() or 'cody' in series.lower():
                                similar_names.append({
                                    'file': file,
                                    'series_name': series.strip()
                                })
            
            except Exception as e:
                continue
        
        if similar_names:
            print("📋 Similar series names found:")
            for item in similar_names:
                print(f"   📁 {item['file']}: '{item['series_name']}'")
        else:
            print("   No similar series names found.")

if __name__ == "__main__":
    find_commando_cody_files() 