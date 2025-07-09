#!/usr/bin/env python3
"""
Find and fix malformed URLs with double URLs in the database
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_malformed_urls():
    """Find and fix malformed URLs with double URLs"""
    
    with engine.connect() as conn:
        print("🔍 Checking for malformed URLs...")
        print("=" * 50)
        
        # Check content table for malformed poster URLs
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url LIKE '%https://storage.googleapis.com%https://storage.googleapis.com%'
        """))
        
        malformed_content = result.fetchall()
        print(f"Found {len(malformed_content)} content entries with malformed poster URLs")
        
        for content_id, title, poster_url in malformed_content:
            print(f"  - ID: {content_id}, Title: '{title}'")
            print(f"    Malformed URL: {poster_url}")
            
            # Fix the URL by removing the duplicate part
            if poster_url and 'https://storage.googleapis.com' in poster_url:
                # Find the second occurrence and keep only the first part
                parts = poster_url.split('https://storage.googleapis.com')
                if len(parts) > 2:
                    fixed_url = 'https://storage.googleapis.com' + parts[1]
                    print(f"    Fixed URL: {fixed_url}")
                    
                    conn.execute(text("""
                        UPDATE content 
                        SET poster_url = :poster_url
                        WHERE id = :content_id
                    """), {
                        "poster_url": fixed_url,
                        "content_id": content_id
                    })
                    print(f"    ✅ Updated")
        
        # Check episodes table for malformed content URLs
        result = conn.execute(text("""
            SELECT id, title, content_url 
            FROM episodes 
            WHERE content_url LIKE '%https://storage.googleapis.com%https://storage.googleapis.com%'
        """))
        
        malformed_episodes = result.fetchall()
        print(f"\nFound {len(malformed_episodes)} episodes with malformed content URLs")
        
        for episode_id, title, content_url in malformed_episodes:
            print(f"  - ID: {episode_id}, Title: '{title}'")
            print(f"    Malformed URL: {content_url}")
            
            # Fix the URL by removing the duplicate part
            if content_url and 'https://storage.googleapis.com' in content_url:
                # Find the second occurrence and keep only the first part
                parts = content_url.split('https://storage.googleapis.com')
                if len(parts) > 2:
                    fixed_url = 'https://storage.googleapis.com' + parts[1]
                    print(f"    Fixed URL: {fixed_url}")
                    
                    conn.execute(text("""
                        UPDATE episodes 
                        SET content_url = :content_url
                        WHERE id = :episode_id
                    """), {
                        "content_url": fixed_url,
                        "episode_id": episode_id
                    })
                    print(f"    ✅ Updated")
        
        conn.commit()
        print(f"\n🎉 Successfully fixed malformed URLs!")

if __name__ == "__main__":
    fix_malformed_urls() 