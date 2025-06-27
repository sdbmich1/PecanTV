#!/usr/bin/env python3
"""
Script to check CSV files for Ghost Squad data.
"""

import pandas as pd
import glob
import os

def check_csv_for_ghost_squad():
    """Check CSV files for Ghost Squad data."""
    print("🔍 Checking CSV files for Ghost Squad data")
    print("=" * 50)
    
    # Get all CSV files with correct pattern
    csv_files = glob.glob("Wurl - File Upload Metadata_Version 7.0.*.csv")
    print(f"📁 Found {len(csv_files)} CSV files")
    
    for csv_file in csv_files[:5]:  # Check first 5 files
        print(f"\n📄 Checking: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            
            # Check if 'Series Name' column exists
            if 'Series Name' in df.columns:
                series_names = df['Series Name'].unique()
                print(f"  Series found: {list(series_names)}")
                
                # Check for Ghost Squad
                if 'Ghost Squad' in series_names:
                    ghost_squad_data = df[df['Series Name'] == 'Ghost Squad']
                    print(f"  ✅ Found Ghost Squad with {len(ghost_squad_data)} episodes!")
                    
                    # Show first few episodes
                    for _, row in ghost_squad_data.head(3).iterrows():
                        print(f"    - {row.get('Title', 'N/A')}")
                    return csv_file
                else:
                    print(f"  ❌ Ghost Squad not found")
            else:
                print(f"  ⚠️  No 'Series Name' column found")
                
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    
    print("\n❌ Ghost Squad not found in first 5 CSV files")
    return None

if __name__ == "__main__":
    check_csv_for_ghost_squad() 