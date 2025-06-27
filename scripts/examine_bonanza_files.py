#!/usr/bin/env python3
"""
Script to examine the structure of Bonanza files and check column names.
"""

import pandas as pd

def examine_bonanza_files():
    """Examine the structure of Bonanza files to check column names."""
    
    bonanza_files = [
        'Wurl - File Upload Metadata_Version 7.0.28.xlsx',
        'Wurl - File Upload Metadata_Version 7.0.28.csv',
        'Wurl - File Upload Metadata_Version 7.0.29.csv',
        'Wurl - File Upload Metadata_Version 7.0.30.csv'
    ]
    
    print("🔍 Examining Bonanza files structure...")
    print("=" * 60)
    
    for file in bonanza_files:
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
            
            print(f"  📊 File shape: {df.shape}")
            print(f"  📋 Column names:")
            for i, col in enumerate(df.columns):
                print(f"    {i+1:2d}. {col}")
            
            # Check for Bonanza episodes
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                bonanza_df = df[df['Series Name'].str.strip().str.lower() == 'bonanza']
                print(f"  🎬 Found {len(bonanza_df)} Bonanza episodes")
                
                if len(bonanza_df) > 0:
                    print(f"  📺 Sample Bonanza episodes:")
                    for i, (_, row) in enumerate(bonanza_df.head(3).iterrows()):
                        print(f"    Episode {i+1}:")
                        print(f"      Title: {row.get('Title', 'N/A')}")
                        print(f"      Season: {row.get('Season Number', 'N/A')}")
                        print(f"      Episode: {row.get('Episode Number', 'N/A')}")
                        
                        # Check for Video Filename
                        video_filename = row.get('Video Filename', 'N/A')
                        print(f"      Video Filename: {video_filename}")
                        
                        # Check for Artwork Fieldname (CSV files)
                        if file.endswith('.csv'):
                            artwork_fieldname = row.get('Artwork Fieldname', 'N/A')
                            print(f"      Artwork Fieldname: {artwork_fieldname}")
                        
                        print()
            
        except Exception as e:
            print(f"  ❌ Error reading {file}: {e}")
    
    print("\n✅ Examination complete!")

if __name__ == "__main__":
    examine_bonanza_files() 