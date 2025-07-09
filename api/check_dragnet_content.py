#!/usr/bin/env python3
"""
Check what content UUIDs exist for Dragnet
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_dragnet_content():
    """Check what content UUIDs exist for Dragnet"""
    
    with engine.connect() as conn:
        print("🔍 Checking Dragnet content entries...")
        print("=" * 40)
        
        # Get Dragnet content entry
        result = conn.execute(text("""
            SELECT id, title, uuid 
            FROM content 
            WHERE title LIKE '%Dragnet%'
        """))
        
        dragnet_content = result.fetchall()
        print(f"Found {len(dragnet_content)} Dragnet content entries")
        
        for content_id, title, content_uuid in dragnet_content:
            print(f"Content ID: {content_id}")
            print(f"Title: {title}")
            print(f"UUID: {content_uuid}")
            print()
        
        # Check if there are any existing Dragnet episodes to see what content_uuid they use
        result = conn.execute(text("""
            SELECT id, title, content_uuid 
            FROM episodes 
            WHERE series_id = 68
        """))
        
        existing_episodes = result.fetchall()
        if existing_episodes:
            print("Existing Dragnet episodes (if any):")
            for episode_id, title, content_uuid in existing_episodes:
                print(f"Episode ID: {episode_id}")
                print(f"Title: {title}")
                print(f"Content UUID: {content_uuid}")
                print()

if __name__ == "__main__":
    check_dragnet_content() 