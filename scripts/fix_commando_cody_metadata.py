#!/usr/bin/env python3
"""
Fix Commando Cody episode metadata with proper titles and runtime
"""

import pandas as pd
import psycopg2
import os
from typing import Dict, List

# Database connection
DB_CONFIG = {
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'sslmode': 'require'
}

def extract_commando_cody_wurl_data() -> Dict[int, Dict]:
    """Extract Commando Cody episode data from Wurl file"""
    wurl_data = {}
    
    try:
        # Read the Excel file
        df = pd.read_excel('Wurl - File Upload Metadata_Version 7.0.xlsx')
        
        print(f"📊 Loaded Wurl file with {len(df)} rows")
        
        # Look for Commando Cody entries
        for _, row in df.iterrows():
            title = str(row.get('Title', '')).lower()
            if 'commando cody' in title or 'sky marshal' in title:
                # Extract episode number from title
                episode_num = None
                if 'chapter' in title:
                    # Look for chapter number
                    import re
                    chapter_match = re.search(r'chapter\s*(\d+)', title, re.IGNORECASE)
                    if chapter_match:
                        episode_num = int(chapter_match.group(1))
                
                if episode_num:
                    # Get runtime (convert to minutes if needed)
                    runtime = row.get('Runtime', 0)
                    if isinstance(runtime, str):
                        # Parse runtime string like "25:30" or "25 min"
                        if ':' in runtime:
                            parts = runtime.split(':')
                            if len(parts) == 2:
                                runtime = int(parts[0]) * 60 + int(parts[1])
                        elif 'min' in runtime.lower():
                            runtime = int(''.join(filter(str.isdigit, runtime)))
                        else:
                            runtime = 0
                    elif isinstance(runtime, (int, float)):
                        runtime = int(runtime)
                    else:
                        runtime = 0
                    
                    # Get description
                    description = str(row.get('Description', ''))
                    if description == 'nan':
                        description = f"Chapter {episode_num} of Commando Cody - Sky Marshal of the Universe"
                    
                    wurl_data[episode_num] = {
                        'title': str(row.get('Title', f'Chapter {episode_num}')),
                        'description': description,
                        'runtime': runtime
                    }
                    print(f"✅ Found Episode {episode_num}: {wurl_data[episode_num]['title']} ({runtime} min)")
        
        print(f"📋 Extracted {len(wurl_data)} Commando Cody episodes from Wurl data")
        return wurl_data
        
    except Exception as e:
        print(f"❌ Error reading Wurl file: {e}")
        return {}

def update_commando_cody_episodes(wurl_data: Dict[int, Dict]):
    """Update Commando Cody episodes with proper metadata"""
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
        
        for episode_num, metadata in wurl_data.items():
            # Update the episode
            cursor.execute("""
                UPDATE episodes 
                SET title = %s, 
                    description = %s,
                    runtime = %s
                WHERE series_id = %s AND episode_number = %s
            """, (metadata['title'], metadata['description'], metadata['runtime'], series_id, episode_num))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated Episode {episode_num}: {metadata['title']} ({metadata['runtime']} min)")
            else:
                print(f"❌ No update for Episode {episode_num}")
        
        conn.commit()
        print(f"🎉 Successfully updated {updated_count} episodes")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main function"""
    print("🔧 Fixing Commando Cody episode metadata...")
    
    # Extract Wurl data
    wurl_data = extract_commando_cody_wurl_data()
    
    if not wurl_data:
        print("❌ No Commando Cody data found in Wurl file")
        return
    
    # Update database
    update_commando_cody_episodes(wurl_data)
    
    print("✅ Commando Cody metadata fix complete!")

if __name__ == "__main__":
    main() 