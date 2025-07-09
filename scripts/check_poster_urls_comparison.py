#!/usr/bin/env python3
"""
Script to compare poster URL handling between Longstreet and Count of Monte Cristo episodes.
"""

import psycopg2
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

def check_poster_urls():
    """Check poster URLs for Longstreet and Count of Monte Cristo episodes."""
    print("🔍 Comparing poster URL handling between Longstreet and Count of Monte Cristo")
    print("=" * 70)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Longstreet series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Longstreet' AND type = 'SERIES'
        """)
        longstreet_result = cur.fetchone()
        
        # Get Count of Monte Cristo series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'The Count of Monte Cristo' AND type = 'SERIES'
        """)
        cmc_result = cur.fetchone()
        
        if not longstreet_result or not cmc_result:
            print("❌ Could not find one or both series")
            return
        
        longstreet_id = longstreet_result[0]
        cmc_id = cmc_result[0]
        
        print(f"✅ Longstreet series ID: {longstreet_id}")
        print(f"✅ Count of Monte Cristo series ID: {cmc_id}")
        print()
        
        # Check Longstreet episodes
        print("📺 LONGSTREET EPISODES:")
        print("-" * 40)
        cur.execute("""
            SELECT episode_number, title, poster_url, content_url
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number 
            LIMIT 5
        """, (longstreet_id,))
        
        longstreet_episodes = cur.fetchall()
        for ep_num, title, poster_url, content_url in longstreet_episodes:
            print(f"  Episode {ep_num}: {title}")
            print(f"    Poster URL: {poster_url}")
            if poster_url:
                # Test if poster URL is accessible
                try:
                    response = requests.head(poster_url, timeout=5)
                    status = response.status_code
                    print(f"    Status: {status} {'✅' if status == 200 else '❌'}")
                except Exception as e:
                    print(f"    Status: Error - {e}")
            else:
                print(f"    Status: No poster URL")
            print()
        
        # Check Count of Monte Cristo episodes
        print("📺 COUNT OF MONTE CRISTO EPISODES:")
        print("-" * 40)
        cur.execute("""
            SELECT episode_number, title, poster_url, content_url
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number 
            LIMIT 5
        """, (cmc_id,))
        
        cmc_episodes = cur.fetchall()
        for ep_num, title, poster_url, content_url in cmc_episodes:
            print(f"  Episode {ep_num}: {title}")
            print(f"    Poster URL: {poster_url}")
            if poster_url:
                # Test if poster URL is accessible
                try:
                    response = requests.head(poster_url, timeout=5)
                    status = response.status_code
                    print(f"    Status: {status} {'✅' if status == 200 else '❌'}")
                except Exception as e:
                    print(f"    Status: Error - {e}")
            else:
                print(f"    Status: No poster URL")
            print()
        
        # Check what poster files exist in GCS for CMC
        print("🔍 CHECKING CMC POSTER FILES IN GCS:")
        print("-" * 40)
        
        # Test the poster URL that was set in the Wurl mapping
        test_poster_url = "https://storage.googleapis.com/pecantv_series/count_of_monte_cristo/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png"
        print(f"Testing CMC poster URL: {test_poster_url}")
        try:
            response = requests.head(test_poster_url, timeout=5)
            status = response.status_code
            print(f"Status: {status} {'✅' if status == 200 else '❌'}")
        except Exception as e:
            print(f"Status: Error - {e}")
        
        # Check if there are any other poster files in the CMC folder
        print("\n🔍 CHECKING FOR OTHER CMC POSTER FILES:")
        print("-" * 40)
        
        # Test some common poster filename patterns
        poster_patterns = [
            "count_of_monte_cristo_poster.jpg",
            "count_of_monte_cristo_poster.png",
            "CMC_poster.jpg",
            "CMC_poster.png",
            "monte_cristo_poster.jpg",
            "monte_cristo_poster.png"
        ]
        
        for pattern in poster_patterns:
            test_url = f"https://storage.googleapis.com/pecantv_series/count_of_monte_cristo/{pattern}"
            try:
                response = requests.head(test_url, timeout=5)
                status = response.status_code
                if status == 200:
                    print(f"✅ Found: {pattern}")
                    print(f"   URL: {test_url}")
                    break
            except Exception:
                continue
        
        # Check Longstreet poster pattern for comparison
        print("\n🔍 CHECKING LONGSTREET POSTER PATTERN:")
        print("-" * 40)
        longstreet_poster_url = "https://storage.googleapis.com/pecantv_series/longstreet/Longstreet1_poster.jpg"
        print(f"Testing Longstreet poster URL: {longstreet_poster_url}")
        try:
            response = requests.head(longstreet_poster_url, timeout=5)
            status = response.status_code
            print(f"Status: {status} {'✅' if status == 200 else '❌'}")
        except Exception as e:
            print(f"Status: Error - {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_poster_urls() 