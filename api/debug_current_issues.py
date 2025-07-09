#!/usr/bin/env python3
"""
Debug current issues and check what's actually in the database
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def debug_current_issues():
    """Debug current issues"""
    
    with engine.connect() as conn:
        print("🔍 Debugging current issues...")
        print("=" * 50)
        
        # 1. Check Dragnet episodes 1 and 3
        print("📺 1. Checking Dragnet episodes 1 and 3:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 AND episode_number IN (1, 3)
            ORDER BY episode_number
        """))
        
        dragnet_episodes = result.fetchall()
        for episode_id, episode_num, title, content_url in dragnet_episodes:
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"  Episode {episode_num}: {title}")
            print(f"    URL: {content_url}")
            print(f"    Filename: {filename}")
        print()
        
        # 2. Check Christie Love in content table
        print("📺 2. Checking Christie Love in content table:")
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
        
        # 3. Check if Christie Love is being served by API (check content endpoint)
        print("📺 3. Checking content API endpoint for Christie Love:")
        result = conn.execute(text("""
            SELECT id, title, type, poster_url 
            FROM content 
            WHERE type = 'FILM' 
            ORDER BY id 
            LIMIT 10
        """))
        
        sample_content = result.fetchall()
        print(f"  Sample content from API (first 10):")
        for content_id, title, content_type, poster_url in sample_content:
            print(f"  {content_id}: {title} ({content_type}) - {poster_url}")
        print()
        
        # 4. Check image URLs that should work
        print("🖼️ 4. Checking image URLs:")
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            AND poster_url LIKE '%poster.jpg'
            LIMIT 5
        """))
        
        working_images = result.fetchall()
        print(f"  Found {len(working_images)} content with poster.jpg URLs")
        for content_id, title, poster_url in working_images:
            print(f"  {title}: {poster_url}")
        print()
        
        # 5. Check if there are any malformed URLs
        print("🖼️ 5. Checking for malformed URLs:")
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            AND (poster_url LIKE '%https://%https://%' OR poster_url LIKE '%http://%http://%')
            LIMIT 5
        """))
        
        malformed_urls = result.fetchall()
        print(f"  Found {len(malformed_urls)} malformed URLs")
        for content_id, title, poster_url in malformed_urls:
            print(f"  {title}: {poster_url}")
        print()

if __name__ == "__main__":
    debug_current_issues() 