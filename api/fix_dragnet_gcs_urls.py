#!/usr/bin/env python3
"""
Fix Dragnet episode URLs to point to Google Cloud Storage
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from database import get_db, engine
from models import ContentType
from sqlalchemy import text

def fix_dragnet_gcs_urls():
    """Fix Dragnet episode URLs to point to Google Cloud Storage"""
    
    # Map of episode numbers to GCS filenames
    episode_to_gcs = {
        1: "Dragnet1_2p-1080-wCredits.mp4",
        2: "Dragnet2_2p-1080-wCredits.mp4", 
        3: "Dragnet3_2p-1080-wCredits.mp4",
        4: "Dragnet4_2p-1080-wCredits.mp4",
        5: "Dragnet5_2p-1080-wCredits.mp4",
        6: "Dragnet6_2p-1080-wCredits.mp4",
        7: "Dragnet7_2p-1080-wCredits.mp4",
        8: "Dragnet8_2p-1080-wCredits.mp4",
        9: "Dragnet9_2p-1080-wCredits.mp4",
        10: "Dragnet10_2p-1080-wCredits.mp4",
        11: "Dragnet11_2p-1080-wCredits.mp4",
        12: "Dragnet12_2p-1080-wCredits.mp4",
        13: "Dragnet13_2p-1080-wCredits.mp4"
    }
    
    with engine.connect() as conn:
        try:
            # Get Dragnet series ID
            result = conn.execute(text("""
                SELECT id FROM content 
                WHERE title = 'Dragnet'
            """))
            
            dragnet_series = result.fetchone()
            if not dragnet_series:
                print("❌ Dragnet series not found in database")
                return
            
            series_id = dragnet_series[0]
            print(f"✅ Found Dragnet series with ID: {series_id}")
            
            # Update each episode URL
            updated_count = 0
            for episode_num, gcs_filename in episode_to_gcs.items():
                gcs_url = f"https://storage.googleapis.com/pecantv_series/dragnet/{gcs_filename}"
                
                result = conn.execute(text("""
                    UPDATE episodes 
                    SET content_url = :content_url
                    WHERE series_id = :series_id AND episode_number = :episode_num
                """), {
                    "content_url": gcs_url,
                    "series_id": series_id,
                    "episode_num": episode_num
                })
                
                if result.rowcount > 0:
                    print(f"✅ Updated Episode {episode_num}: {gcs_filename}")
                    updated_count += 1
                else:
                    print(f"⚠️  Episode {episode_num} not found or already updated")
            
            conn.commit()
            print(f"\n🎉 Successfully updated {updated_count} Dragnet episode URLs")
            
            # Verify the updates
            result = conn.execute(text("""
                SELECT episode_number, title, content_url 
                FROM episodes 
                WHERE series_id = :series_id 
                ORDER BY episode_number
            """), {"series_id": series_id})
            
            episodes = result.fetchall()
            print(f"\n📋 Updated Dragnet episodes:")
            for episode_num, title, content_url in episodes:
                status = "✅" if content_url and "storage.googleapis.com" in content_url else "❌"
                print(f"  {status} Episode {episode_num}: {title}")
                if content_url:
                    print(f"     URL: {content_url}")
            
        except Exception as e:
            print(f"❌ Error updating Dragnet URLs: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    fix_dragnet_gcs_urls() 