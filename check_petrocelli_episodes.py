#!/usr/bin/env python3
"""
Check Petrocelli episodes in database and files
"""

import psycopg2
import os

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def check_database_episodes():
    print("🔍 Checking Petrocelli episodes in database...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Get all Petrocelli episodes
        cur.execute("SELECT episode_number, title, content_url FROM episodes WHERE series_id = 21 ORDER BY episode_number")
        episodes = cur.fetchall()
        
        print(f"📋 Found {len(episodes)} episodes in database:")
        for ep in episodes:
            print(f"  S1E{ep[0]}: {ep[1]}")
        
        # Check for gaps
        episode_numbers = [ep[0] for ep in episodes]
        missing = []
        for i in range(1, 23):  # Should have 22 episodes
            if i not in episode_numbers:
                missing.append(i)
        
        if missing:
            print(f"\n❌ Missing episodes: {missing}")
        else:
            print(f"\n✅ All 22 episodes present!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def check_episode_files():
    print("\n🔍 Checking Petrocelli episode files...")
    
    petrocelli_dir = "pecantv_series/petrocelli"
    if not os.path.exists(petrocelli_dir):
        print(f"❌ Directory {petrocelli_dir} not found")
        return
    
    files = os.listdir(petrocelli_dir)
    mp4_files = [f for f in files if f.endswith('.mp4')]
    
    print(f"📁 Found {len(mp4_files)} MP4 files:")
    for file in sorted(mp4_files):
        print(f"  - {file}")

if __name__ == "__main__":
    check_database_episodes()
    check_episode_files() 