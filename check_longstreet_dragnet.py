#!/usr/bin/env python3
"""
Check Longstreet and Dragnet episodes in Wurl metadata and database
"""

import psycopg2
import pandas as pd
import os

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,  # Docker PostgreSQL port
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def check_wurl_metadata():
    print("🔍 Checking Wurl metadata files for Longstreet and Dragnet...")
    
    # Find the latest Wurl CSV file
    wurl_files = [f for f in os.listdir('.') if f.startswith('Wurl - File Upload Metadata_Version 7.0.') and f.endswith('.csv')]
    if not wurl_files:
        print("❌ No Wurl CSV files found")
        return
    
    latest_file = sorted(wurl_files)[-1]
    print(f"📁 Using: {latest_file}")
    
    try:
        df = pd.read_csv(latest_file)
        
        # Check for Longstreet episodes
        longstreet = df[df['Series Name'].fillna('').str.contains('Longstreet', case=False, na=False)]
        print(f"\n📺 Longstreet episodes in Wurl: {len(longstreet)}")
        if len(longstreet) > 0:
            for _, row in longstreet.head(5).iterrows():
                print(f"  - {row.get('Title', 'Unknown')} (S{row.get('Season Number', '?')}E{row.get('Episode Number', '?')})")
        
        # Check for Dragnet episodes
        dragnet = df[df['Series Name'].fillna('').str.contains('Dragnet', case=False, na=False)]
        print(f"\n📺 Dragnet episodes in Wurl: {len(dragnet)}")
        if len(dragnet) > 0:
            for _, row in dragnet.head(5).iterrows():
                print(f"  - {row.get('Title', 'Unknown')} (S{row.get('Season Number', '?')}E{row.get('Episode Number', '?')})")
                
    except Exception as e:
        print(f"❌ Error reading Wurl file: {e}")

def check_database():
    print("\n🔍 Checking database for Longstreet and Dragnet...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Check content table for series
        print("\n📋 Series in content table:")
        cur.execute("SELECT id, title, type FROM content WHERE title ILIKE '%longstreet%' OR title ILIKE '%dragnet%' ORDER BY title")
        series = cur.fetchall()
        
        for s in series:
            print(f"  ID {s[0]}: {s[1]} ({s[2]})")
            
            # Check episodes for this series
            cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (s[0],))
            episode_count = cur.fetchone()[0]
            print(f"    Episodes: {episode_count}")
            
            if episode_count > 0:
                cur.execute("SELECT episode_number, title FROM episodes WHERE series_id = %s ORDER BY episode_number LIMIT 3", (s[0],))
                episodes = cur.fetchall()
                for ep in episodes:
                    print(f"      S1E{ep[0]}: {ep[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_wurl_metadata()
    check_database() 