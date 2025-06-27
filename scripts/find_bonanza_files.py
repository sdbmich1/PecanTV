#!/usr/bin/env python3
"""
Script to find which Wurl metadata files contain Bonanza data.
"""

import os
import pandas as pd
import glob

def find_bonanza_files():
    """Search all Wurl metadata files for Bonanza data."""
    
    print("🔍 Searching for Bonanza data in Wurl metadata files...")
    print("=" * 60)
    
    excel_files = glob.glob("Wurl*.xlsx")
    csv_files = glob.glob("Wurl*.csv")
    
    bonanza_files = []
    
    # Check Excel files
    for file in excel_files:
        try:
            df = pd.read_excel(file)
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                bonanza_count = len(df[df['Series Name'].str.strip().str.lower() == 'bonanza'])
                if bonanza_count > 0:
                    bonanza_files.append({
                        'file': file,
                        'type': 'Excel',
                        'count': bonanza_count
                    })
                    print(f"✅ {file} - {bonanza_count} Bonanza episodes")
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
    
    # Check CSV files
    for file in csv_files:
        try:
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
                bonanza_count = len(df[df['Series Name'].str.strip().str.lower() == 'bonanza'])
                if bonanza_count > 0:
                    bonanza_files.append({
                        'file': file,
                        'type': 'CSV',
                        'count': bonanza_count
                    })
                    print(f"✅ {file} - {bonanza_count} Bonanza episodes")
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print("-" * 30)
    if bonanza_files:
        print(f"Found Bonanza data in {len(bonanza_files)} files:")
        total_episodes = sum(f['count'] for f in bonanza_files)
        print(f"Total Bonanza episodes found: {total_episodes}")
        
        print(f"\n📋 Files with Bonanza data:")
        print("-" * 40)
        for file_info in bonanza_files:
            print(f"  {file_info['file']} ({file_info['type']}) - {file_info['count']} episodes")
    else:
        print("❌ No Bonanza data found in any files")
    
    return bonanza_files

if __name__ == "__main__":
    find_bonanza_files() 