#!/usr/bin/env python3
"""
Script to search for Commando Cody data in the Wurl file.
"""

import pandas as pd

def search_commando_cody_in_wurl():
    """Search for Commando Cody data in the Wurl file."""
    print("🔍 Searching for Commando Cody in Wurl data")
    print("=" * 50)
    
    try:
        df = pd.read_excel("Wurl - File Upload Metadata_Version 7.0.43.xlsx")
        
        # Search for Commando Cody in various columns
        search_terms = ['commando', 'cody', 'sky marshal']
        
        for term in search_terms:
            print(f"\nSearching for '{term}':")
            
            # Search in Series Name
            series_matches = df[df['Series Name'].str.contains(term, case=False, na=False)]
            if not series_matches.empty:
                print(f"  Found {len(series_matches)} matches in Series Name:")
                for _, row in series_matches.iterrows():
                    print(f"    Series: {row.get('Series Name', 'N/A')}")
                    print(f"    Episode: {row.get('Episode Title', 'N/A')}")
                    print(f"    Video File: {row.get('Video Filename', 'N/A')}")
                    print()
            
            # Search in Episode Title
            episode_matches = df[df['Episode Title'].str.contains(term, case=False, na=False)]
            if not episode_matches.empty:
                print(f"  Found {len(episode_matches)} matches in Episode Title:")
                for _, row in episode_matches.iterrows():
                    print(f"    Series: {row.get('Series Name', 'N/A')}")
                    print(f"    Episode: {row.get('Episode Title', 'N/A')}")
                    print(f"    Video File: {row.get('Video Filename', 'N/A')}")
                    print()
            
            # Search in Video Filename
            filename_matches = df[df['Video Filename'].str.contains(term, case=False, na=False)]
            if not filename_matches.empty:
                print(f"  Found {len(filename_matches)} matches in Video Filename:")
                for _, row in filename_matches.iterrows():
                    print(f"    Series: {row.get('Series Name', 'N/A')}")
                    print(f"    Episode: {row.get('Episode Title', 'N/A')}")
                    print(f"    Video File: {row.get('Video Filename', 'N/A')}")
                    print()
        
        # Also check for any series with "Sky" or "Marshal" in the name
        print("\nSearching for series with 'Sky' or 'Marshal':")
        sky_marshal_matches = df[df['Series Name'].str.contains('sky|marshal', case=False, na=False)]
        if not sky_marshal_matches.empty:
            print(f"  Found {len(sky_marshal_matches)} matches:")
            for _, row in sky_marshal_matches.iterrows():
                print(f"    Series: {row.get('Series Name', 'N/A')}")
                print(f"    Episode: {row.get('Episode Title', 'N/A')}")
                print(f"    Video File: {row.get('Video Filename', 'N/A')}")
                print()
        
    except Exception as e:
        print(f"❌ Error reading Wurl file: {e}")

if __name__ == "__main__":
    search_commando_cody_in_wurl() 