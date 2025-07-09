#!/usr/bin/env python3
import pandas as pd
import glob

def search_longstreet():
    files = glob.glob('Wurl*.csv')
    found = False
    
    for f in files:
        try:
            df = pd.read_csv(f, encoding='utf-8', on_bad_lines='skip')
            if 'Series Name' in df.columns and df['Series Name'].astype(str).str.contains('Longstreet', case=False, na=False).any():
                print(f'✅ {f}')
                longstreet_data = df[df['Series Name'].astype(str).str.contains('Longstreet', case=False, na=False)]
                print(longstreet_data[['Title','Description','Video Filename']])
                found = True
        except Exception as e:
            continue
    
    print(f'Found: {found}')

if __name__ == "__main__":
    search_longstreet() 