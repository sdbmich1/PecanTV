#!/usr/bin/env python3
"""
Check which Count of Monte Cristo episodes are actually available in Google Cloud Storage
and update the database to remove episodes that don't exist.
"""

import psycopg2
import requests
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

def check_gcs_availability(url):
    """Check if a file exists in Google Cloud Storage"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def check_cmc_gcs_availability():
    """Check which Count of Monte Cristo episodes are available in GCS"""
    print("🔍 Checking Count of Monte Cristo episodes availability in Google Cloud Storage")
    print("=" * 70)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Count of Monte Cristo series ID
        cur.execute("""
            SELECT id, title FROM content 
            WHERE title = 'The Count of Monte Cristo' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Count of Monte Cristo series not found")
            return
        
        series_id, series_title = result
        print(f"✅ Found series: {series_title} (ID: {series_id})")
        
        # Get all episodes for Count of Monte Cristo
        cur.execute("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} episodes in database")
        print()
        
        available_episodes = []
        missing_episodes = []
        
        for episode_id, episode_number, title, content_url in episodes:
            print(f"🔍 Checking Episode {episode_number}: {title}")
            print(f"   URL: {content_url}")
            
            if check_gcs_availability(content_url):
                print(f"   ✅ Available")
                available_episodes.append((episode_id, episode_number, title))
            else:
                print(f"   ❌ Missing from GCS")
                missing_episodes.append((episode_id, episode_number, title))
            print()
        
        print("=" * 70)
        print(f"📊 Summary:")
        print(f"   Available episodes: {len(available_episodes)}")
        print(f"   Missing episodes: {len(missing_episodes)}")
        print()
        
        if missing_episodes:
            print("❌ Missing episodes:")
            for episode_id, episode_number, title in missing_episodes:
                print(f"   Episode {episode_number}: {title}")
            print()
            
            # Ask if user wants to remove missing episodes
            response = input("Do you want to remove missing episodes from the database? (y/N): ")
            if response.lower() == 'y':
                print("🗑️  Removing missing episodes...")
                for episode_id, episode_number, title in missing_episodes:
                    cur.execute("DELETE FROM episodes WHERE id = %s", (episode_id,))
                    print(f"   ✅ Removed Episode {episode_number}: {title}")
                
                conn.commit()
                print(f"\n🎉 Removed {len(missing_episodes)} missing episodes from database")
            else:
                print("⚠️  Keeping missing episodes in database")
        else:
            print("✅ All episodes are available in Google Cloud Storage!")
        
        # Show final count
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
        final_count = cur.fetchone()[0]
        print(f"\n📺 Final episode count: {final_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_cmc_gcs_availability() 