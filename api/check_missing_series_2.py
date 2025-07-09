#!/usr/bin/env python3
"""
Check for missing series: No Man with a Camera and Ghost Squad
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_missing_series_2():
    """Check for missing series in the database"""
    
    missing_series = [
        "No Man with a Camera",
        "Ghost Squad"
    ]
    
    with engine.connect() as conn:
        print("🔍 Checking for missing series...")
        print("=" * 50)
        
        for series_name in missing_series:
            # Check content table
            result = conn.execute(text("""
                SELECT id, title, poster_url 
                FROM content 
                WHERE LOWER(title) LIKE LOWER(:series_name)
            """), {"series_name": f"%{series_name}%"})
            
            content_entries = result.fetchall()
            
            if content_entries:
                print(f"✅ Found {len(content_entries)} content entries for '{series_name}':")
                for content_id, title, poster_url in content_entries:
                    print(f"   - ID: {content_id}, Title: '{title}'")
                    print(f"     Poster: {poster_url}")
                    
                    # Check if it has episodes
                    episode_result = conn.execute(text("""
                        SELECT episode_number, title, content_url 
                        FROM episodes 
                        WHERE series_id = :series_id 
                        ORDER BY episode_number
                    """), {"series_id": content_id})
                    
                    episodes = episode_result.fetchall()
                    print(f"     Episodes: {len(episodes)}")
                    for ep_num, ep_title, ep_url in episodes[:3]:  # Show first 3
                        print(f"       Episode {ep_num}: {ep_title}")
                        if ep_url:
                            print(f"         URL: {ep_url}")
                    if len(episodes) > 3:
                        print(f"       ... and {len(episodes) - 3} more episodes")
            else:
                print(f"❌ No content entries found for '{series_name}'")
            
            print()
        
        # Also check for any series with similar names
        print("🔍 Checking for similar series names...")
        print("=" * 50)
        
        similar_series = [
            "no man",
            "ghost squad"
        ]
        
        for search_term in similar_series:
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
            print()

if __name__ == "__main__":
    check_missing_series_2() 