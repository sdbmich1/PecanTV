#!/usr/bin/env python3
"""
Fix the final issues that weren't resolved
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_final_issues():
    """Fix the final issues"""
    
    with engine.connect() as conn:
        print("🔧 Fixing final issues...")
        print("=" * 50)
        
        # 1. Fix Dragnet episodes 1 and 3 to use Dragnet14 and Dragnet15
        print("📺 1. Fixing Dragnet episodes 1 and 3...")
        
        # Fix episode 1 to use Dragnet14
        conn.execute(text("""
            UPDATE episodes 
            SET content_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet14_2p-1080-wCredits.mp4'
            WHERE series_id = 68 AND episode_number = 1
        """))
        print("✅ Updated Dragnet episode 1 to use Dragnet14")
        
        # Fix episode 3 to use Dragnet15
        conn.execute(text("""
            UPDATE episodes 
            SET content_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet15_2p-1080-wCredits.mp4'
            WHERE series_id = 68 AND episode_number = 3
        """))
        print("✅ Updated Dragnet episode 3 to use Dragnet15")
        
        # 2. Fix Christie Love poster URL
        print("\n📺 2. Fixing Christie Love poster URL...")
        conn.execute(text("""
            UPDATE content 
            SET poster_url = 'https://storage.googleapis.com/pecantv_series/get_christie_love/poster.jpg'
            WHERE id = 3
        """))
        print("✅ Fixed Christie Love poster URL")
        
        # 3. Fix all incomplete image URLs by adding /poster.jpg
        print("\n🖼️ 3. Fixing all incomplete image URLs...")
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            AND poster_url NOT LIKE '%poster.jpg'
            AND poster_url NOT LIKE '%png'
            AND poster_url NOT LIKE '%jpeg'
            AND poster_url NOT LIKE '%jpg'
            AND poster_url NOT LIKE '%default_poster.jpg'
        """))
        
        incomplete_images = result.fetchall()
        print(f"Found {len(incomplete_images)} incomplete image URLs")
        
        fixed_count = 0
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
                fixed_count += 1
                if fixed_count <= 5:  # Show first 5 for verification
                    print(f"  Fixed {title}: {poster_url} → {new_url}")
        
        print(f"✅ Fixed {fixed_count} image URLs")
        
        # 4. Verify the fixes
        print("\n🔍 Verifying fixes...")
        
        # Check Dragnet episodes
        result = conn.execute(text("""
            SELECT episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 AND episode_number IN (1, 3)
            ORDER BY episode_number
        """))
        
        dragnet_episodes = result.fetchall()
        print("Dragnet episodes 1 and 3:")
        for episode_num, title, content_url in dragnet_episodes:
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"  Episode {episode_num}: {filename}")
        
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
            AND poster_url LIKE '%poster.jpg'
            LIMIT 5
        """))
        
        sample_images = result.fetchall()
        print(f"Sample fixed image URLs ({len(sample_images)}):")
        for title, poster_url in sample_images:
            print(f"  {title}: {poster_url}")
        
        print("\n✅ All final issues fixed!")

if __name__ == "__main__":
    fix_final_issues() 