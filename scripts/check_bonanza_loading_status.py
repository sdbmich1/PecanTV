#!/usr/bin/env python3
"""
Script to check if Bonanza episodes were loaded from pecantv_series folder and verify the loading process.
"""

import psycopg2
import os

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_bonanza_loading_status():
    """Check if Bonanza episodes were loaded from pecantv_series folder."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Checking Bonanza Loading Status")
        print("=" * 50)
        
        # Check if pecantv_series folder exists
        if os.path.exists('pecantv_series'):
            print("✅ pecantv_series folder exists")
            bonanza_folder = os.path.join('pecantv_series', 'bonanza')
            if os.path.exists(bonanza_folder):
                print(f"✅ Bonanza folder exists: {bonanza_folder}")
                files = os.listdir(bonanza_folder)
                print(f"📁 Files in Bonanza folder: {len(files)}")
                for file in files[:5]:  # Show first 5 files
                    print(f"   - {file}")
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more files")
            else:
                print(f"❌ Bonanza folder not found: {bonanza_folder}")
        else:
            print("❌ pecantv_series folder not found")
        
        # Get Bonanza series ID
        cur.execute("SELECT id FROM content WHERE title = 'Bonanza' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Bonanza series not found in database")
            return
        
        series_id = series_result[0]
        print(f"✅ Found Bonanza series (ID: {series_id})")
        
        # Get all Bonanza episodes with detailed info
        cur.execute("""
            SELECT id, title, season_number, episode_number, content_url, poster_url, created_at
            FROM episodes 
            WHERE series_id = %s
            ORDER BY season_number, episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"\n📺 Found {len(episodes)} Bonanza episodes in database:")
        print("-" * 60)
        
        valid_content_urls = 0
        valid_poster_urls = 0
        
        for ep_id, title, season, episode, content_url, poster_url, created_at in episodes:
            content_status = "✅" if content_url and content_url.strip() else "❌"
            poster_status = "✅" if poster_url and poster_url.strip() else "❌"
            
            if content_url and content_url.strip():
                valid_content_urls += 1
            if poster_url and poster_url.strip():
                valid_poster_urls += 1
            
            print(f"{content_status} S{season:02d}E{episode:02d} - {title}")
            print(f"     Content URL: {content_url if content_url else 'MISSING'}")
            print(f"     Poster URL: {poster_url if poster_url else 'MISSING'}")
            print(f"     Created: {created_at}")
            print()
        
        # Summary
        print("📊 Summary:")
        print("-" * 30)
        print(f"  Total episodes: {len(episodes)}")
        print(f"  Episodes with content URLs: {valid_content_urls}")
        print(f"  Episodes with poster URLs: {valid_poster_urls}")
        print(f"  Episodes missing content URLs: {len(episodes) - valid_content_urls}")
        print(f"  Episodes missing poster URLs: {len(episodes) - valid_poster_urls}")
        
        # Check if episodes were loaded from pecantv_series
        if valid_content_urls == 0:
            print("\n❌ No content URLs found - episodes may not have been loaded from pecantv_series folder")
            print("   or the loading process didn't use the correct field names from Wurl metadata")
        else:
            print(f"\n✅ {valid_content_urls} episodes have content URLs")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_bonanza_loading_status() 