#!/usr/bin/env python3
"""
Check what the working Dragnet URLs look like
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_dragnet_urls():
    """Check Dragnet episode URLs"""
    
    with engine.connect() as conn:
        print("🔍 Checking Dragnet episode URLs...")
        print("=" * 50)
        
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 
            ORDER BY episode_number
        """))
        
        dragnet_episodes = result.fetchall()
        print(f"Found {len(dragnet_episodes)} Dragnet episodes")
        
        for episode_id, episode_num, title, content_url in dragnet_episodes:
            print(f"  Episode {episode_num}: {title}")
            print(f"    URL: {content_url}")

if __name__ == "__main__":
    check_dragnet_urls() 