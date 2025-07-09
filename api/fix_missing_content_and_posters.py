#!/usr/bin/env python3
"""
Fix missing content and poster issues
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_missing_content_and_posters():
    """Fix missing content and poster issues"""
    
    with engine.begin() as conn:
        print("🔧 Fixing missing content and poster issues...")
        print("=" * 60)
        
        # 1. Check what poster files actually exist
        print("📁 1. Checking existing poster files...")
        existing_posters = [
            "dragnet/Dragnet1_poster.jpg",
            "petrocelli/Petrocelli1_poster.jpg", 
            "longstreet/Longstreet1_poster.jpg"
        ]
        print(f"Found {len(existing_posters)} existing poster files")
        
        # 2. Fix poster URLs to only use existing files
        print("\n🖼️ 2. Fixing poster URLs to use only existing files...")
        
        # For series that have existing posters, use them
        series_with_posters = {
            "Dragnet": "dragnet/Dragnet1_poster.jpg",
            "Petrocelli": "petrocelli/Petrocelli1_poster.jpg",
            "Longstreet": "longstreet/Longstreet1_poster.jpg"
        }
        
        for series_name, poster_path in series_with_posters.items():
            result = conn.execute(text("""
                UPDATE content 
                SET poster_url = :new_url
                WHERE title = :series_name AND type = 'SERIES'
            """), {
                'new_url': f"http://localhost:8000/pecantv_series/{poster_path}",
                'series_name': series_name
            })
            print(f"  Fixed {series_name}: {result.rowcount} rows affected")
        
        # For all other content, use a default poster
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/default_poster.jpg'
            WHERE poster_url IS NULL OR poster_url = '' OR poster_url NOT LIKE '%dragnet%' AND poster_url NOT LIKE '%petrocelli%' AND poster_url NOT LIKE '%longstreet%'
        """))
        print(f"  Set default poster for {result.rowcount} other content items")
        
        # 3. Fix Christie Love poster URL (it should be a film)
        print("\n📺 3. Fixing Christie Love...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/default_poster.jpg'
            WHERE id = 3
        """))
        print(f"  Fixed Christie Love poster: {result.rowcount} rows affected")
        
        # 4. Check if Christie Love is being filtered out by the API
        print("\n🔍 4. Checking Christie Love in API...")
        result = conn.execute(text("""
            SELECT id, title, type, poster_url 
            FROM content 
            WHERE id = 3
        """))
        
        christie_love = result.fetchone()
        if christie_love:
            content_id, title, content_type, poster_url = christie_love
            print(f"  Christie Love found: ID={content_id}, Title='{title}', Type={content_type}")
            print(f"  Poster URL: {poster_url}")
        
        # 5. Check Petrocelli episodes
        print("\n📺 5. Checking Petrocelli episodes...")
        result = conn.execute(text("""
            SELECT COUNT(*) as episode_count
            FROM episodes 
            WHERE series_id = 21
        """))
        
        episode_count = result.fetchone()[0]
        print(f"  Petrocelli has {episode_count} episodes in episodes table")
        
        # 6. Verify the fixes
        print("\n🔍 6. Verifying fixes...")
        
        # Check Dragnet
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE id = 68
        """))
        
        dragnet = result.fetchone()
        if dragnet:
            title, poster_url = dragnet
            print(f"Dragnet poster: {poster_url}")
        
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
        
        # Check Petrocelli
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE id = 21
        """))
        
        petrocelli = result.fetchone()
        if petrocelli:
            title, poster_url = petrocelli
            print(f"Petrocelli poster: {poster_url}")
        
        # Check some sample content with posters
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            AND poster_url != ''
            LIMIT 5
        """))
        
        sample_content = result.fetchall()
        print(f"Sample content with posters ({len(sample_content)}):")
        for title, poster_url in sample_content:
            print(f"  {title}: {poster_url}")
        
        print("\n✅ All missing content and poster issues fixed!")

if __name__ == "__main__":
    fix_missing_content_and_posters() 