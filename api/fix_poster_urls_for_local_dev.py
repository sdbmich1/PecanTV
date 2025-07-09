#!/usr/bin/env python3
"""
Fix poster URLs to use the local development server instead of GCS
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_poster_urls_for_local_dev():
    """Fix poster URLs to use the local development server"""
    
    with engine.begin() as conn:
        print("🔧 Fixing poster URLs for local development...")
        print("=" * 60)
        
        # 1. Fix Dragnet poster URL to use local server
        print("📺 1. Fixing Dragnet poster URL...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/dragnet/Dragnet1_poster.jpg'
            WHERE id = 68
        """))
        print(f"✅ Fixed Dragnet poster URL: {result.rowcount} rows affected")
        
        # 2. Fix Christie Love poster URL to use local server
        print("\n📺 2. Fixing Christie Love poster URL...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/get_christie_love/poster.jpg'
            WHERE id = 3
        """))
        print(f"✅ Fixed Christie Love poster URL: {result.rowcount} rows affected")
        
        # 3. Fix other series poster URLs to use local server
        print("\n📺 3. Fixing other series poster URLs...")
        
        # Petrocelli
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/petrocelli/Petrocelli1_poster.jpg'
            WHERE title LIKE '%Petrocelli%'
        """))
        print(f"✅ Fixed Petrocelli poster URL: {result.rowcount} rows affected")
        
        # Longstreet
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/longstreet/Longstreet1_poster.jpg'
            WHERE title LIKE '%Longstreet%'
        """))
        print(f"✅ Fixed Longstreet poster URL: {result.rowcount} rows affected")
        
        # 4. For films without specific posters, use a default
        print("\n📺 4. Setting default poster for films...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/default_poster.jpg'
            WHERE type = 'FILM' 
            AND (poster_url IS NULL OR poster_url = '' OR poster_url LIKE '%default_poster.jpg')
        """))
        print(f"✅ Set default poster for films: {result.rowcount} rows affected")
        
        # 5. For series that don't have specific poster files, use a default
        print("\n📺 5. Setting default poster for series without specific posters...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = 'http://localhost:8000/pecantv_series/default_poster.jpg'
            WHERE type = 'SERIES' 
            AND (poster_url IS NULL OR poster_url = '')
        """))
        print(f"✅ Set default poster for series: {result.rowcount} rows affected")
        
        # 6. Verify the fixes
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
        
        print("\n✅ All poster URLs fixed for local development!")

if __name__ == "__main__":
    fix_poster_urls_for_local_dev() 