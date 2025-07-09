#!/usr/bin/env python3
"""
Script to fix episode URLs for Dragnet and Commando Cody series.
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

def fix_dragnet_urls():
    """Fix Dragnet episode URLs to use correct file names."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing Dragnet Episode URLs")
        print("=" * 40)
        
        # Get Dragnet series ID
        cur.execute("SELECT id FROM content WHERE title = 'Dragnet' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Dragnet series not found")
            return
        series_id = series_record[0]
        print(f"✅ Found Dragnet series ID: {series_id}")
        
        # Update Dragnet episode URLs
        dragnet_updates = [
            (1, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet1_2p-1080-wCredits.mp4"),
            (2, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet2_2p-1080-wCredits.mp4"),
            (3, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet3_2p-1080-wCredits.mp4"),
            (4, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet4_2p-1080-wCredits.mp4"),
            (5, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet5_2p-1080-wCredits.mp4"),
            (6, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet6_2p-1080-wCredits.mp4"),
            (7, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet7_2p-1080-wCredits.mp4"),
            (8, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet8_2p-1080-wCredits.mp4"),
            (9, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet9_2p-1080-wCredits.mp4"),
            (10, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet10_2p-1080-wCredits.mp4"),
            (11, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet11_2p-1080-wCredits.mp4"),
            (12, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet12_2p-1080-wCredits.mp4"),
            (13, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet13_2p-1080-wCredits.mp4"),
            (14, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet14_2p-1080-wCredits.mp4"),
            (15, "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet15_2p-1080-wCredits.mp4"),
        ]
        
        updated = 0
        for episode_num, new_url in dragnet_updates:
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (new_url, datetime.now(timezone.utc), series_id, episode_num))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated Dragnet Episode {episode_num}: {new_url}")
                updated += 1
            else:
                print(f"  ⚠️  No episode found for Dragnet Episode {episode_num}")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Dragnet episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fix_commando_cody_urls():
    """Fix Commando Cody episode URLs to use correct file paths."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🎬 Fixing Commando Cody Episode URLs")
        print("=" * 40)
        
        # Get Commando Cody series ID
        cur.execute("SELECT id FROM content WHERE title = 'Commando Cody - Sky Marshal of the Universe' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Commando Cody series not found")
            return
        series_id = series_record[0]
        print(f"✅ Found Commando Cody series ID: {series_id}")
        
        # Update Commando Cody episode URLs
        cody_updates = [
            (1, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch1_1pass-10fps.mp4"),
            (2, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch2_1pass-10fps.mp4"),
            (3, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch3_1pass-10fps.mp4"),
            (4, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch4_1pass-10fps.mp4"),
            (5, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch5_1pass-10fps.mp4"),
            (6, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch6_1pass-10fps.mp4"),
            (7, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch7_1pass-10fps.mp4"),
            (8, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch8_1pass-10fps.mp4"),
            (9, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch9_1pass-10fps.mp4"),
            (10, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch10_1pass-10fps.mp4"),
            (11, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch11_1pass-10fps.mp4"),
            (12, "https://storage.googleapis.com/pecantv_series/commando_cody/Commando-Cody-ch12_1pass-10fps.mp4"),
        ]
        
        updated = 0
        for episode_num, new_url in cody_updates:
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (new_url, datetime.now(timezone.utc), series_id, episode_num))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated Commando Cody Episode {episode_num}: {new_url}")
                updated += 1
            else:
                print(f"  ⚠️  No episode found for Commando Cody Episode {episode_num}")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Commando Cody episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to fix all episode URLs."""
    print("🎬 Fixing Episode URLs for Dragnet and Commando Cody")
    print("=" * 60)
    
    fix_dragnet_urls()
    fix_commando_cody_urls()
    
    print("\n🎉 URL fixes completed!")

if __name__ == "__main__":
    main() 