#!/usr/bin/env python3
"""
Marry Commando Cody Wurl data with GCS files
"""

import requests
import json
import re
from typing import Dict, List, Optional

# Database connection
DB_CONFIG = {
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'sslmode': 'require'
}

def check_gcs_file_exists(url: str) -> bool:
    """Check if a GCS file exists"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_commando_cody_gcs_files() -> List[str]:
    """Get list of available Commando Cody files in GCS"""
    base_url = "https://storage.googleapis.com/pecantv_series/commando_cody/"
    
    # Try different filename patterns based on the example provided
    patterns = [
        "Commando-Cody-ch{episode:02d}_1pass-10fps.mp4",
        "Commando-Cody-ch{episode}_1pass-10fps.mp4",
        "CommandoCody{episode:02d}_2p-1080-wCredits.mp4",
        "CommandoCody{episode}_2p-1080-wCredits.mp4",
        "Commando-Cody-{episode:02d}.mp4",
        "Commando-Cody-{episode}.mp4"
    ]
    
    available_files = []
    
    for episode in range(1, 13):  # Commando Cody has 12 episodes
        for pattern in patterns:
            try:
                filename = pattern.format(episode=episode)
                url = base_url + filename
                if check_gcs_file_exists(url):
                    available_files.append({
                        'episode': episode,
                        'filename': filename,
                        'url': url
                    })
                    print(f"✅ Found: {filename}")
                    break  # Found this episode, move to next
            except:
                continue
    
    return available_files

def extract_wurl_data() -> Dict[int, Dict]:
    """Extract Commando Cody data from Wurl file"""
    wurl_data = {}
    
    # Try to read the Wurl file
    try:
        import pandas as pd
        
        # Read the Excel file
        df = pd.read_excel('Wurl - File Upload Metadata_Version 7.0.xlsx')
        
        # Look for Commando Cody entries
        for _, row in df.iterrows():
            title = str(row.get('Title', '')).lower()
            if 'commando cody' in title or 'sky marshal' in title:
                episode_num = row.get('Episode Number', 0)
                if episode_num and episode_num > 0:
                    wurl_data[int(episode_num)] = {
                        'title': str(row.get('Title', '')),
                        'description': str(row.get('Description', '')),
                        'runtime': row.get('Runtime', 0),
                        'episode_number': int(episode_num)
                    }
                    print(f"📋 Wurl: Episode {episode_num} - {row.get('Title', '')}")
                    
    except FileNotFoundError:
        print("❌ Wurl file not found. Please place 'Wurl - File Upload Metadata_Version 7.0.xlsx' in the current directory.")
        return {}
    except Exception as e:
        print(f"❌ Error reading Wurl file: {e}")
        return {}
    
    return wurl_data

def update_database_episodes(gcs_files: List[Dict], wurl_data: Dict[int, Dict]):
    """Update database with GCS URLs and Wurl metadata"""
    import psycopg2
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get Commando Cody series ID
        cursor.execute("SELECT id FROM content WHERE title ILIKE '%commando cody%'")
        series_result = cursor.fetchone()
        
        if not series_result:
            print("❌ Commando Cody series not found in database")
            return
            
        series_id = series_result[0]
        print(f"✅ Found Commando Cody series ID: {series_id}")
        
        updated_count = 0
        
        for gcs_file in gcs_files:
            episode_num = gcs_file['episode']
            content_url = gcs_file['url']
            
            # Get Wurl metadata if available
            wurl_meta = wurl_data.get(episode_num, {})
            title = wurl_meta.get('title', f'Chapter {episode_num}')
            description = wurl_meta.get('description', f'Commando Cody Chapter {episode_num}')
            runtime = wurl_meta.get('runtime', 0)
            
            # Update the episode in the episodes table
            cursor.execute("""
                UPDATE episodes 
                SET content_url = %s, 
                    title = %s, 
                    description = %s,
                    runtime = %s
                WHERE series_id = %s AND episode_number = %s
            """, (content_url, title, description, runtime, series_id, episode_num))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated Episode {episode_num}: {title}")
            else:
                print(f"❌ No update for Episode {episode_num}")
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} episodes")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    print("🔍 Marrying Commando Cody Wurl data with GCS files")
    print("=" * 60)
    
    # Step 1: Find available GCS files
    print("\n📁 Checking GCS files...")
    gcs_files = get_commando_cody_gcs_files()
    
    if not gcs_files:
        print("❌ No Commando Cody files found in GCS")
        return
    
    print(f"\n✅ Found {len(gcs_files)} GCS files")
    
    # Step 2: Extract Wurl data
    print("\n📋 Extracting Wurl data...")
    wurl_data = extract_wurl_data()
    
    if not wurl_data:
        print("⚠️  No Wurl data found, will use default titles")
    
    print(f"✅ Found {len(wurl_data)} Wurl entries")
    
    # Step 3: Update database
    print("\n💾 Updating database...")
    update_database_episodes(gcs_files, wurl_data)
    
    print("\n🎯 Marriage complete!")

if __name__ == "__main__":
    main() 