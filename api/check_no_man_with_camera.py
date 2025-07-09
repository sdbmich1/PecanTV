#!/usr/bin/env python3
"""
Check for "No Man with a Camera" series specifically
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_no_man_with_camera():
    """Check for No Man with a Camera series"""
    
    with engine.connect() as conn:
        print("🔍 Checking for 'No Man with a Camera' series...")
        print("=" * 50)
        
        # Check for exact title
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE LOWER(title) = LOWER('No Man with a Camera')
        """))
        
        exact_match = result.fetchone()
        if exact_match:
            content_id, title, poster_url = exact_match
            print(f"✅ Found exact match: ID {content_id}, Title: '{title}'")
            
            # Check episodes
            episode_result = conn.execute(text("""
                SELECT episode_number, title, content_url 
                FROM episodes 
                WHERE series_id = :series_id 
                ORDER BY episode_number
            """), {"series_id": content_id})
            
            episodes = episode_result.fetchall()
            print(f"  Episodes: {len(episodes)}")
            for ep_num, ep_title, ep_url in episodes:
                print(f"    Episode {ep_num}: {ep_title}")
                if ep_url:
                    print(f"      URL: {ep_url}")
        else:
            print("❌ No exact match found for 'No Man with a Camera'")
        
        # Check for similar titles
        print("\n🔍 Checking for similar titles...")
        similar_titles = [
            "man with camera",
            "no man",
            "camera"
        ]
        
        for search_term in similar_titles:
            result = conn.execute(text("""
                SELECT id, title, poster_url 
                FROM content 
                WHERE LOWER(title) LIKE LOWER(:search_term)
                ORDER BY title
            """), {"search_term": f"%{search_term}%"})
            
            similar_entries = result.fetchall()
            if similar_entries:
                print(f"📋 Series containing '{search_term}':")
                for content_id, title, poster_url in similar_entries:
                    print(f"   - ID: {content_id}, Title: '{title}'")
            else:
                print(f"❌ No series found containing '{search_term}'")

if __name__ == "__main__":
    check_no_man_with_camera() 