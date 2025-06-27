#!/usr/bin/env python3
"""
Script to search all Wurl metadata files for any 'Video Filename' containing 'commando-cody' (case-insensitive, substring match, with dashes, underscores, or spaces).
"""

import pandas as pd
import glob
import os
import re

def find_commando_cody_video_filenames():
    print("🔍 Searching for 'commando-cody' (wildcard) in Video Filename fields...")
    print("=" * 70)
    
    # Find all Wurl metadata files
    excel_files = glob.glob("Wurl*.xlsx") + glob.glob("Wurl - *.xlsx") + glob.glob("Wurl-File-Upload-Metadata*.xlsx")
    csv_files = glob.glob("Wurl*.csv") + glob.glob("Wurl - *.csv") + glob.glob("Wurl-File-Upload-Metadata*.csv")
    
    # Pattern: commando-cody, commando_cody, commando cody, any substring
    pattern = re.compile(r"commando[-_ ]?cody", re.IGNORECASE)
    found = False
    
    for file in excel_files + csv_files:
        try:
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except Exception:
                        continue
            if 'Video Filename' in df.columns:
                matches = df[df['Video Filename'].astype(str).str.contains(pattern, na=False)]
                if not matches.empty:
                    print(f"\n📁 File: {file}")
                    print(matches[['Series Name', 'Title', 'Video Filename']])
                    found = True
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
    if not found:
        print("No 'commando-cody' (wildcard) video filenames found in any Wurl metadata file.")

if __name__ == "__main__":
    find_commando_cody_video_filenames() 