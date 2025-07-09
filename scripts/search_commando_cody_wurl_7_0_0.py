#!/usr/bin/env python3
"""
Script to search for Commando Cody - Sky Marshal of the Universe data in the Wurl file Wurl-File-Upload-Metadata_Version-7.0.0.xlsx.
"""

import pandas as pd

def search_commando_cody_wurl_7_0_0():
    """Search for Commando Cody - Sky Marshal of the Universe in the Wurl file Wurl-File-Upload-Metadata_Version-7.0.0.xlsx."""
    print("🔍 Searching for Commando Cody - Sky Marshal of the Universe in Wurl data (Wurl-File-Upload-Metadata_Version-7.0.0.xlsx)")
    print("=" * 60)
    
    try:
        df = pd.read_excel("Wurl-File-Upload-Metadata_Version-7.0.0.xlsx")
        print(f"✅ Loaded Wurl file with {len(df)} rows")
        print(f"Columns: {list(df.columns)}\n")
        
        # Search for the exact series name
        matches = df[df['Series Name'].astype(str).str.strip().str.lower() == 'commando cody - sky marshal of the universe'.lower()]
        if not matches.empty:
            print(f"Found {len(matches)} episodes for Commando Cody:")
            for _, row in matches.iterrows():
                print(f"  Episode: {row.get('Title', 'N/A')}")
                print(f"    Video Filename: {row.get('Video Filename', 'N/A')}")
                print(f"    Episode Number: {row.get('Episode Number', 'N/A')}")
                print(f"    Description: {row.get('Description', 'N/A')}")
                print()
        else:
            print("❌ No episodes found for Commando Cody - Sky Marshal of the Universe in this Wurl file.")
        
    except Exception as e:
        print(f"❌ Error reading Wurl file: {e}")

if __name__ == "__main__":
    search_commando_cody_wurl_7_0_0() 