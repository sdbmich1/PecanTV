#!/usr/bin/env python3
"""
Script to fix Commando Cody episode URLs to point to the correct Google Cloud Storage URLs.
"""

import psycopg2
from datetime import datetime, timezone

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_commando_cody_gcs_urls():
    """Update Commando Cody episode URLs to use correct Google Cloud Storage URLs."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        print("🎬 Fixing Commando Cody Episode URLs to Google Cloud Storage")
        print("=" * 60)
        
        # Get Commando Cody series ID
        cur.execute("SELECT id FROM content WHERE title = 'Commando Cody - Sky Marshal of the Universe'")
        series_id = cur.fetchone()[0]
        print(f"✅ Found Commando Cody series ID: {series_id}")
        
        # Define the correct GCS URLs for each episode
        episode_urls = {
            1: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch1_1pass-10fps.mp4",
            2: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch2_1pass-10fps.mp4",
            3: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch3_1pass-10fps.mp4",
            4: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch4_1pass-10fps.mp4",
            5: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch5_1pass-10fps.mp4",
            6: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch6_1pass-10fps.mp4",
            7: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch7_1pass-10fps.mp4",
            8: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch8_1pass-10fps.mp4",
            9: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch9_1pass-10fps.mp4",
            10: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch10_1pass-10fps.mp4",
            11: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch11_1pass-10fps.mp4",
            12: "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch12_1pass-10fps.mp4"
        }
        
        updated = 0
        for episode_num, gcs_url in episode_urls.items():
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (gcs_url, datetime.now(timezone.utc), series_id, episode_num))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated Episode {episode_num}: {gcs_url}")
                updated += 1
            else:
                print(f"  ⚠️  No episode found for Episode {episode_num}")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Commando Cody episodes with correct GCS URLs.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_commando_cody_gcs_urls() 