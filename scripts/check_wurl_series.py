#!/usr/bin/env python3
"""
Script to check what series are actually in the new Wurl file.
"""

import pandas as pd

def check_wurl_series():
    file_path = "Wurl-File-Upload-Metadata_Version-7.0.4.1.xlsx"
    df = pd.read_excel(file_path)
    
    print("🔍 Series found in the new Wurl file:")
    print("=" * 50)
    
    # Get unique series names
    series_counts = df['Series Name'].value_counts()
    
    for series_name, count in series_counts.items():
        print(f"📺 {series_name}: {count} episodes")
        
        # Show a few episode titles as examples
        series_data = df[df['Series Name'] == series_name]
        print(f"   Examples: {', '.join(series_data['Title'].head(3).tolist())}")
        print()

if __name__ == "__main__":
    check_wurl_series() 