#!/usr/bin/env python3
"""
Fix all remaining issues: Dragnet episode 1, Count of Monte Cristo, Christie Love, and image URLs
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_all_remaining_issues():
    """Fix all remaining issues"""
    
    with engine.connect() as conn:
        print("🔧 Fixing all remaining issues...")
        print("=" * 50)
        
        # 1. Fix Dragnet episode 1 to use Dragnet14
        print("📺 1. Fixing Dragnet episode 1...")
        conn.execute(text("""
            UPDATE episodes 
            SET content_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet14_2p-1080-wCredits.mp4'
            WHERE series_id = 68 AND episode_number = 1
        """))
        print("✅ Updated Dragnet episode 1 to use Dragnet14")
        
        # 2. Fix Christie Love poster URL
        print("\n📺 2. Fixing Christie Love poster URL...")
        conn.execute(text("""
            UPDATE content 
            SET poster_url = 'https://storage.googleapis.com/pecantv_series/get_christie_love/poster.jpg'
            WHERE id = 3
        """))
        print("✅ Fixed Christie Love poster URL")
        
        # 3. Fix incomplete image URLs by adding /poster.jpg
        print("\n🖼️ 3. Fixing incomplete image URLs...")
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            AND poster_url NOT LIKE '%poster.jpg'
            AND poster_url NOT LIKE '%png'
            AND poster_url NOT LIKE '%jpeg'
            AND poster_url NOT LIKE '%jpg'
        """))
        
        incomplete_images = result.fetchall()
        print(f"Found {len(incomplete_images)} incomplete image URLs")
        
        for content_id, title, poster_url in incomplete_images:
            if poster_url and not poster_url.endswith(('.jpg', '.png', '.jpeg')):
                new_url = poster_url.rstrip('/') + '/poster.jpg'
                conn.execute(text("""
                    UPDATE content 
                    SET poster_url = :new_url
                    WHERE id = :content_id
                """), {
                    'new_url': new_url,
                    'content_id': content_id
                })
                print(f"  Fixed {title}: {poster_url} → {new_url}")
        
        print(f"✅ Fixed {len(incomplete_images)} image URLs")
        
        # 4. Verify the fixes
        print("\n🔍 Verifying fixes...")
        
        # Check Dragnet episode 1
        result = conn.execute(text("""
            SELECT episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 AND episode_number = 1
        """))
        
        dragnet_ep1 = result.fetchone()
        if dragnet_ep1:
            episode_num, title, content_url = dragnet_ep1
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"Dragnet Episode 1: {filename}")
        
        # Check Christie Love
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE id = 3
        """))
        
        christie_love = result.fetchone()
        if christie_love:
            title, poster_url = christie_love
            print(f"Christie Love poster: {poster_url}")
        
        # Check some fixed image URLs
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            LIMIT 3
        """))
        
        sample_images = result.fetchall()
        print("Sample image URLs:")
        for title, poster_url in sample_images:
            print(f"  {title}: {poster_url}")
        
        print("\n✅ All issues fixed!")

if __name__ == "__main__":
    fix_all_remaining_issues() 