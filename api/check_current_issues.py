#!/usr/bin/env python3
"""
Check the current status of all reported issues
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_current_issues():
    """Check the current status of all reported issues"""
    
    with engine.connect() as conn:
        print("🔍 Checking current issues...")
        print("=" * 50)
        
        # 1. Check Dragnet episode 1
        print("📺 1. Checking Dragnet episode 1:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 AND episode_number = 1
        """))
        
        dragnet_ep1 = result.fetchone()
        if dragnet_ep1:
            episode_id, episode_num, title, content_url = dragnet_ep1
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"  Episode 1: {title}")
            print(f"  URL: {content_url}")
            print(f"  Filename: {filename}")
        else:
            print("  ❌ Episode 1 not found!")
        print()
        
        # 2. Check Count of Monte Cristo episodes
        print("📺 2. Checking Count of Monte Cristo episodes:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 72 
            ORDER BY episode_number
        """))
        
        monte_cristo_episodes = result.fetchall()
        print(f"  Found {len(monte_cristo_episodes)} episodes")
        for episode_id, episode_num, title, content_url in monte_cristo_episodes:
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"  Episode {episode_num}: {title}")
            print(f"    URL: {content_url}")
            print(f"    Filename: {filename}")
        print()
        
        # 3. Check Christie Love
        print("📺 3. Checking Christie Love:")
        result = conn.execute(text("""
            SELECT id, title, type, content_url, poster_url 
            FROM content 
            WHERE title LIKE '%Christie Love%'
        """))
        
        christie_love = result.fetchall()
        print(f"  Found {len(christie_love)} Christie Love entries")
        for content_id, title, content_type, content_url, poster_url in christie_love:
            print(f"  ID: {content_id}, Title: {title}, Type: {content_type}")
            print(f"    Content URL: {content_url}")
            print(f"    Poster URL: {poster_url}")
        print()
        
        # 4. Check some image URLs
        print("🖼️ 4. Checking some image URLs:")
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            LIMIT 5
        """))
        
        sample_images = result.fetchall()
        print(f"  Found {len(sample_images)} sample images")
        for content_id, title, poster_url in sample_images:
            print(f"  {title}: {poster_url}")
        print()

if __name__ == "__main__":
    check_current_issues() 