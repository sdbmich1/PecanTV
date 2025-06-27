#!/usr/bin/env python3
"""
Script to list all unique series names found in Wurl metadata files.
"""

import pandas as pd
import glob
import os

def list_all_wurl_series():
    """List all unique series names found in Wurl metadata files."""
    print("🔍 Listing all series found in Wurl metadata files...")
    print("=" * 60)
    
    # Find all Wurl metadata files with different patterns
    excel_files = glob.glob("Wurl*.xlsx") + glob.glob("Wurl - *.xlsx") + glob.glob("Wurl-File-Upload-Metadata*.xlsx")
    csv_files = glob.glob("Wurl*.csv") + glob.glob("Wurl - *.csv") + glob.glob("Wurl-File-Upload-Metadata*.csv")
    
    all_series = {}
    
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
                
                for series_name in df['Series Name'].unique():
                    if series_name and series_name.strip() and series_name.strip().lower() != 'nan':
                        series_name_clean = series_name.strip()
                        if series_name_clean not in all_series:
                            all_series[series_name_clean] = {
                                'files': [],
                                'episode_count': 0,
                                'has_video_filenames': 0,
                                'has_artwork_filenames': 0
                            }
                        
                        if file not in all_series[series_name_clean]['files']:
                            all_series[series_name_clean]['files'].append(file)
                        
                        # Count episodes for this series
                        series_df = df[df['Series Name'].str.strip() == series_name_clean]
                        all_series[series_name_clean]['episode_count'] += len(series_df)
                        
                        # Count episodes with video filenames
                        if 'Video Filename' in df.columns:
                            video_count = len(series_df[series_df['Video Filename'].notna() & (series_df['Video Filename'] != '')])
                            all_series[series_name_clean]['has_video_filenames'] += video_count
                        
                        # Count episodes with artwork filenames
                        if 'Artwork Filename' in df.columns:
                            artwork_count = len(series_df[series_df['Artwork Filename'].notna() & (series_df['Artwork Filename'] != '')])
                            all_series[series_name_clean]['has_artwork_filenames'] += artwork_count
        
        except Exception as e:
            print(f"  ⚠️  Error reading {file}: {e}")
    
    # Display results
    if all_series:
        print(f"✅ Found {len(all_series)} unique series in Wurl metadata files:")
        print()
        
        # Sort by series name
        sorted_series = sorted(all_series.items(), key=lambda x: x[0].lower())
        
        for series_name, info in sorted_series:
            print(f"📺 {series_name}")
            print(f"   📁 Files: {len(info['files'])}")
            print(f"   📺 Episodes: {info['episode_count']}")
            print(f"   🎥 Video filenames: {info['has_video_filenames']}")
            print(f"   🖼️  Artwork filenames: {info['has_artwork_filenames']}")
            print()
        
        # Summary
        total_episodes = sum(info['episode_count'] for info in all_series.values())
        total_video = sum(info['has_video_filenames'] for info in all_series.values())
        total_artwork = sum(info['has_artwork_filenames'] for info in all_series.values())
        
        print("📊 SUMMARY:")
        print(f"   Total series: {len(all_series)}")
        print(f"   Total episodes: {total_episodes}")
        print(f"   Episodes with video filenames: {total_video}")
        print(f"   Episodes with artwork filenames: {total_artwork}")
        
    else:
        print("❌ No series data found in any Wurl metadata files.")

if __name__ == "__main__":
    list_all_wurl_series() 