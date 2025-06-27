#!/usr/bin/env python3
"""
Script to check which Wurl metadata files contain Petrocelli data.
"""

import os
import pandas as pd
import glob

def check_wurl_petrocelli_files():
    """Check which Wurl metadata files contain Petrocelli data."""
    
    # Get all Wurl metadata files
    wurl_files = []
    
    # Excel files
    excel_files = glob.glob("../Wurl-File-Upload-Metadata_Version-*.xlsx")
    wurl_files.extend(excel_files)
    
    # CSV files
    csv_files = glob.glob("../Wurl-File-Upload-Metadata_Version-*.csv")
    wurl_files.extend(csv_files)
    
    print(f"🔍 Found {len(wurl_files)} Wurl metadata files")
    print("=" * 70)
    
    petrocelli_files = []
    
    for file_path in wurl_files:
        filename = os.path.basename(file_path)
        print(f"\n📖 Checking: {filename}")
        
        try:
            # Read the file
            if filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # Check for Petrocelli entries
            petrocelli_entries = []
            
            # Check different possible column names for series
            series_columns = ['Series Name', 'SeriesName', 'series_name', 'Series']
            title_columns = ['Title', 'title', 'Name', 'name']
            
            series_col = None
            title_col = None
            
            for col in series_columns:
                if col in df.columns:
                    series_col = col
                    break
            
            for col in title_columns:
                if col in df.columns:
                    title_col = col
                    break
            
            if series_col:
                # Check series name column
                petrocelli_series = df[df[series_col].str.contains('Petrocelli', case=False, na=False)]
                if not petrocelli_series.empty:
                    petrocelli_entries.extend(petrocelli_series.to_dict('records'))
            
            if title_col:
                # Check title column
                petrocelli_titles = df[df[title_col].str.contains('Petrocelli', case=False, na=False)]
                if not petrocelli_titles.empty:
                    petrocelli_entries.extend(petrocelli_titles.to_dict('records'))
            
            # Remove duplicates
            unique_entries = []
            seen = set()
            for entry in petrocelli_entries:
                # Create a unique key for each entry
                if series_col and title_col:
                    key = f"{entry.get(series_col, '')}_{entry.get(title_col, '')}"
                elif series_col:
                    key = str(entry.get(series_col, ''))
                elif title_col:
                    key = str(entry.get(title_col, ''))
                else:
                    key = str(entry)
                
                if key not in seen:
                    seen.add(key)
                    unique_entries.append(entry)
            
            if unique_entries:
                petrocelli_files.append({
                    'filename': filename,
                    'entries': unique_entries,
                    'count': len(unique_entries)
                })
                
                print(f"  ✅ Found {len(unique_entries)} Petrocelli entries")
                
                # Show some details about the entries
                for i, entry in enumerate(unique_entries[:3]):  # Show first 3
                    if series_col and entry.get(series_col):
                        print(f"    {i+1}. Series: {entry[series_col]}")
                    if title_col and entry.get(title_col):
                        print(f"       Title: {entry[title_col]}")
                
                if len(unique_entries) > 3:
                    print(f"    ... and {len(unique_entries) - 3} more entries")
            else:
                print(f"  ❌ No Petrocelli entries found")
                
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY: Wurl files containing Petrocelli data")
    print("=" * 70)
    
    if petrocelli_files:
        for file_info in petrocelli_files:
            print(f"📁 {file_info['filename']}: {file_info['count']} entries")
    else:
        print("❌ No Wurl metadata files contain Petrocelli data")
    
    return petrocelli_files

if __name__ == "__main__":
    check_wurl_petrocelli_files() 