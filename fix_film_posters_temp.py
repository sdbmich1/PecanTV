#!/usr/bin/env python3
"""
Temporary fix: Set all films to use the default poster URL
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "api"))

from database import engine
from sqlalchemy import text

def fix_film_posters_temp():
    """Temporarily set all films to use the default poster URL"""
    
    with engine.begin() as conn:
        print("🎬 Temporarily setting all films to use default poster...")
        print("=" * 60)
        
        # Railway base URL
        railway_url = "https://pecantv-api-production.up.railway.app"
        default_poster_url = f"{railway_url}/pecantv_series/default_poster.jpg"
        
        # Update all films to use the default poster
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE type = 'FILM'
        """), {
            'poster_url': default_poster_url
        })
        
        print(f"✅ Updated {result.rowcount} films to use default poster")
        
        # Verify the changes
        print(f"\n🔍 Verifying film poster URLs...")
        
        # Check a few films
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE type = 'FILM'
            ORDER BY id 
            LIMIT 5
        """))
        
        film_items = result.fetchall()
        for item in film_items:
            print(f"  - {item.title}: {item.poster_url}")
        
        print(f"\n🎉 Temporary fix applied!")
        print(f"📁 All films now use the working default poster")
        print(f"🌐 This will show the Pecan logo for all films until we fix the individual posters")
        
        return True

if __name__ == "__main__":
    fix_film_posters_temp() 