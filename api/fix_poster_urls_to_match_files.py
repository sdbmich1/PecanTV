#!/usr/bin/env python3
"""
Fix poster URLs to match the actual file names in the GCS bucket
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_poster_urls_to_match_files():
    """Fix poster URLs to match the actual file names"""
    
    with engine.begin() as conn:
        print("🔧 Fixing poster URLs to match actual file names...")
        print("=" * 60)
        
        # 1. Fix Dragnet poster URL
        print("📺 1. Fixing Dragnet poster URL...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'https://storage.googleapis.com/pecantv_series/dragnet/Dragnet1_poster.jpg'
            WHERE id = 68
        """))
        print(f"✅ Fixed Dragnet poster URL: {result.rowcount} rows affected")
        
        # 2. Fix Christie Love poster URL (it should be a film, not a series)
        print("\n📺 2. Fixing Christie Love poster URL...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'https://storage.googleapis.com/pecantv_features/get_christie_love/poster.jpg'
            WHERE id = 3
        """))
        print(f"✅ Fixed Christie Love poster URL: {result.rowcount} rows affected")
        
        # 3. Fix other series poster URLs based on actual file structure
        print("\n📺 3. Fixing other series poster URLs...")
        
        # Petrocelli
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli1_poster.jpg'
            WHERE title LIKE '%Petrocelli%'
        """))
        print(f"✅ Fixed Petrocelli poster URL: {result.rowcount} rows affected")
        
        # Longstreet
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'https://storage.googleapis.com/pecantv_series/longstreet/Longstreet1_poster.jpg'
            WHERE title LIKE '%Longstreet%'
        """))
        print(f"✅ Fixed Longstreet poster URL: {result.rowcount} rows affected")
        
        # 4. For films, we need to check if they have poster files or use a default
        print("\n📺 4. Setting default poster for films without specific posters...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'https://storage.googleapis.com/pecantv_features/default_poster.jpg'
            WHERE type = 'FILM' 
            AND (poster_url IS NULL OR poster_url = '')
        """))
        print(f"✅ Set default poster for films: {result.rowcount} rows affected")
        
        # 5. Verify the fixes
        print("\n🔍 Verifying fixes...")
        
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
        
        # Check some sample content
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
        
        print("\n✅ All poster URLs fixed!")

if __name__ == "__main__":
    fix_poster_urls_to_match_files() 