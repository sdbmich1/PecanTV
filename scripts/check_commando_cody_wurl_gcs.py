#!/usr/bin/env python3
"""
Script to check Commando Cody's Wurl data and GCS availability.
"""

import psycopg2
import pandas as pd
import requests

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_commando_cody_status():
    """Check Commando Cody's current status and Wurl data."""
    print("🔍 Checking Commando Cody status")
    print("=" * 50)
    
    # Check current episodes in database
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Commando Cody series info
        cur.execute("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE title ILIKE '%commando%cody%' 
            AND type = 'SERIES'
        """)
        
        series = cur.fetchone()
        if series:
            series_id, series_title, series_poster = series
            print(f"Series: {series_title} (ID: {series_id})")
            print(f"Poster: {series_poster}")
            print()
            
            # Get episodes
            cur.execute("""
                SELECT id, title, episode_number, content_url, poster_url
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number
            """, (series_id,))
            
            episodes = cur.fetchall()
            print(f"Found {len(episodes)} episodes in database:")
            for ep_id, ep_title, ep_num, content_url, poster_url in episodes:
                print(f"  Episode {ep_num}: {ep_title}")
                print(f"    Content URL: {content_url}")
                print(f"    Poster URL: {poster_url}")
                print()
        else:
            print("❌ Commando Cody series not found in database")
            return
        
        # Check Wurl data
        print("📋 Checking Wurl data...")
        try:
            df = pd.read_excel("Wurl - File Upload Metadata_Version 7.0.43.xlsx")
            
            # Filter for Commando Cody
            commando_cody_data = df[df['Series Name'].str.contains('Commando Cody', case=False, na=False)]
            
            if not commando_cody_data.empty:
                print(f"Found {len(commando_cody_data)} Commando Cody entries in Wurl data:")
                for _, row in commando_cody_data.iterrows():
                    print(f"  Episode: {row.get('Episode Title', 'N/A')}")
                    print(f"  Video File: {row.get('Video Filename', 'N/A')}")
                    print(f"  Series: {row.get('Series Name', 'N/A')}")
                    print()
            else:
                print("❌ No Commando Cody data found in Wurl file")
                
        except Exception as e:
            print(f"❌ Error reading Wurl file: {e}")
        
        # Test GCS URLs
        print("🌐 Testing GCS availability...")
        test_urls = [
            "https://storage.googleapis.com/pecantv_series/commando_cody/CommandoCody1_2p-1080-wCredits.mp4",
            "https://storage.googleapis.com/pecantv_series/commando_cody/CommandoCody2_2p-1080-wCredits.mp4",
            "https://storage.googleapis.com/pecantv_series/commando_cody/CommandoCody3_2p-1080-wCredits.mp4",
            "https://storage.googleapis.com/pecantv_series/commando_cody/CommandoCody4_2p-1080-wCredits.mp4",
            "https://storage.googleapis.com/pecantv_series/commando_cody/CommandoCody5_2p-1080-wCredits.mp4"
        ]
        
        for url in test_urls:
            try:
                response = requests.head(url, timeout=10)
                status = "✅ Available" if response.status_code == 200 else "❌ Not Found"
                print(f"  {url}: {status}")
            except Exception as e:
                print(f"  {url}: ❌ Error - {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_commando_cody_status() 