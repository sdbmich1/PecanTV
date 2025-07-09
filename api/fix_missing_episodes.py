#!/usr/bin/env python3
"""
Fix missing episodes and URLs for Count of Monte Cristo, Longstreet, and Christie Love
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_missing_episodes():
    """Fix missing episodes and URLs for various series"""
    
    with engine.connect() as conn:
        print("🔧 Fixing missing episodes and URLs...")
        print("=" * 50)
        
        # 1. Fix Count of Monte Cristo episodes (add content URLs)
        print("📺 Fixing Count of Monte Cristo episodes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title 
            FROM episodes 
            WHERE series_id = 72 AND (content_url IS NULL OR content_url = '')
            ORDER BY episode_number
        """))
        
        monte_cristo_episodes = result.fetchall()
        print(f"Found {len(monte_cristo_episodes)} episodes with missing URLs")
        
        for episode_id, episode_num, title in monte_cristo_episodes:
            # Generate GCS URL for Count of Monte Cristo
            gcs_url = f"https://storage.googleapis.com/pecantv_series/the_count_of_monte_cristo/count_of_monte_cristo/Count-of-Monte-Cristo-Episode-{episode_num}.mp4"
            
            conn.execute(text("""
                UPDATE episodes 
                SET content_url = :content_url
                WHERE id = :episode_id
            """), {
                "content_url": gcs_url,
                "episode_id": episode_id
            })
            print(f"✅ Updated Episode {episode_num}: {title}")
        
        # 2. Fix Longstreet episodes (add missing content URLs)
        print("\n📺 Fixing Longstreet episodes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 49 AND (content_url IS NULL OR content_url = '' OR content_url LIKE 'http://localhost%')
            ORDER BY episode_number
        """))
        
        longstreet_episodes = result.fetchall()
        print(f"Found {len(longstreet_episodes)} episodes with missing or localhost URLs")
        
        for episode_id, episode_num, title, old_url in longstreet_episodes:
            # Convert to GCS URL
            gcs_url = f"https://storage.googleapis.com/pecantv_series/longstreet/Longstreet{episode_num}.mp4"
            
            conn.execute(text("""
                UPDATE episodes 
                SET content_url = :content_url
                WHERE id = :episode_id
            """), {
                "content_url": gcs_url,
                "episode_id": episode_id
            })
            print(f"✅ Updated Episode {episode_num}: {title}")
            if old_url:
                print(f"   Old URL: {old_url}")
            print(f"   New URL: {gcs_url}")
        
        # 3. Check Christie Love episodes
        print("\n📺 Checking Christie Love episodes...")
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE LOWER(title) LIKE '%christie love%'
        """))
        
        christie_love_series = result.fetchall()
        for series_id, title, poster_url in christie_love_series:
            print(f"Series: {title} (ID: {series_id})")
            
            # Check if it has episodes
            episode_result = conn.execute(text("""
                SELECT episode_number, title, content_url 
                FROM episodes 
                WHERE series_id = :series_id 
                ORDER BY episode_number
            """), {"series_id": series_id})
            
            episodes = episode_result.fetchall()
            print(f"  Episodes: {len(episodes)}")
            
            if len(episodes) == 0:
                print(f"  ⚠️  No episodes found for {title}")
                print(f"  💡 You may need to add episodes manually or import from metadata")
        
        conn.commit()
        print(f"\n🎉 Successfully updated episodes!")
        
        # Verify the fixes
        print("\n📋 Verification:")
        print("=" * 30)
        
        # Check Count of Monte Cristo
        result = conn.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN content_url IS NOT NULL AND content_url != '' THEN 1 END) as with_urls
            FROM episodes 
            WHERE series_id = 72
        """))
        
        monte_cristo_stats = result.fetchone()
        print(f"Count of Monte Cristo: {monte_cristo_stats[0]} total episodes, {monte_cristo_stats[1]} with URLs")
        
        # Check Longstreet
        result = conn.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN content_url LIKE 'https://storage.googleapis.com%' THEN 1 END) as gcs_urls
            FROM episodes 
            WHERE series_id = 49
        """))
        
        longstreet_stats = result.fetchone()
        print(f"Longstreet: {longstreet_stats[0]} total episodes, {longstreet_stats[1]} with GCS URLs")

if __name__ == "__main__":
    fix_missing_episodes() 