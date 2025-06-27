#!/usr/bin/env python3
"""
Script to search the newly downloaded Wurl metadata file for any 'Cody' or 'Commando Cody' content.
"""

import pandas as pd
import re

def search_cody_in_file():
    print("🔍 Searching for 'Cody' in the new Wurl metadata file...")
    print("=" * 60)
    
    file_path = "Wurl-File-Upload-Metadata_Version-7.0.4.1.xlsx"
    
    try:
        df = pd.read_excel(file_path)
        print(f"✅ Successfully loaded file: {file_path}")
        print(f"📊 File contains {len(df)} rows and {len(df.columns)} columns")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Search for 'Cody' in all string columns
        pattern = re.compile(r"cody", re.IGNORECASE)
        found = False
        
        for column in df.columns:
            if df[column].dtype == 'object':  # String columns
                matches = df[df[column].astype(str).str.contains(pattern, na=False)]
                if not matches.empty:
                    print(f"\n📁 Column: {column} - {len(matches)} match(es)")
                    for idx, row in matches.iterrows():
                        print(f"  Row {idx}: {row[column]}")
                        # Also show Series Name and Title if available
                        if 'Series Name' in df.columns:
                            print(f"    Series: {row.get('Series Name', 'N/A')}")
                        if 'Title' in df.columns:
                            print(f"    Title: {row.get('Title', 'N/A')}")
                        if 'Video Filename' in df.columns:
                            print(f"    Video: {row.get('Video Filename', 'N/A')}")
                    found = True
        
        if not found:
            print("❌ No 'Cody' content found in this file.")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    search_cody_in_file() 