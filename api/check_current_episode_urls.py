#!/usr/bin/env python3
"""
Check what URLs are currently in the database for episodes
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_current_episode_urls():
    """Check current episode URLs in database"""
    
    with engine.connect() as conn:
        print("🔍 Checking current episode URLs in database...")
        print("=" * 50)
        
        # Check Longstreet episodes
        print("📺 Longstreet episodes:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 49 
            ORDER BY episode_number
            LIMIT 5
        """))
        
        longstreet_episodes = result.fetchall()
        for episode_id, episode_num, title, content_url in longstreet_episodes:
            print(f"  Episode {episode_num}: {title}")
            print(f"    URL: {content_url}")
        
        # Check Count of Monte Cristo episodes
        print("\n📺 Count of Monte Cristo episodes:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 72 
            ORDER BY episode_number
            LIMIT 5
        """))
        
        monte_cristo_episodes = result.fetchall()
        for episode_id, episode_num, title, content_url in monte_cristo_episodes:
            print(f"  Episode {episode_num}: {title}")
            print(f"    URL: {content_url}")
        
        # Check Man with a Camera episodes
        print("\n📺 Man with a Camera episodes:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 700 
            ORDER BY episode_number
            LIMIT 5
        """))
        
        man_with_camera_episodes = result.fetchall()
        for episode_id, episode_num, title, content_url in man_with_camera_episodes:
            print(f"  Episode {episode_num}: {title}")
            print(f"    URL: {content_url}")
        
        # Check Ghost Squad episodes
        print("\n📺 Ghost Squad episodes:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 62 
            ORDER BY episode_number
            LIMIT 5
        """))
        
        ghost_squad_episodes = result.fetchall()
        for episode_id, episode_num, title, content_url in ghost_squad_episodes:
            print(f"  Episode {episode_num}: {title}")
            print(f"    URL: {content_url}")

if __name__ == "__main__":
    check_current_episode_urls() 