#!/usr/bin/env python3
"""
Fix poster URLs to use Railway deployment with local images
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "api"))

from database import engine
from sqlalchemy import text

def fix_poster_urls_for_railway():
    """Fix poster URLs to use Railway deployment with local images"""
    
    with engine.begin() as conn:
        print("🔧 Fixing poster URLs for Railway deployment...")
        print("=" * 60)
        
        # Railway base URL
        railway_url = "https://pecantv-api-production.up.railway.app"
        
        # Update all GCS poster URLs to use Railway with local images
        print("📺 1. Updating GCS poster URLs to Railway...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :new_poster_url
            WHERE poster_url LIKE '%storage.googleapis.com%'
        """), {
            'new_poster_url': f"{railway_url}/pecantv_series/default_poster.jpg"
        })
        
        gcs_updated = result.rowcount
        print(f"✅ Updated {gcs_updated} GCS poster URLs")
        
        # Update localhost poster URLs to use Railway
        print("\n📺 2. Updating localhost poster URLs to Railway...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :new_poster_url
            WHERE poster_url LIKE '%localhost%'
        """), {
            'new_poster_url': f"{railway_url}/pecantv_series/default_poster.jpg"
        })
        
        localhost_updated = result.rowcount
        print(f"✅ Updated {localhost_updated} localhost poster URLs")
        
        # Update NULL poster URLs
        print("\n📺 3. Updating NULL poster URLs...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :new_poster_url
            WHERE poster_url IS NULL
        """), {
            'new_poster_url': f"{railway_url}/pecantv_series/default_poster.jpg"
        })
        
        null_updated = result.rowcount
        print(f"✅ Updated {null_updated} NULL poster URLs")
        
        # Now let's set specific poster URLs for known series
        print("\n📺 4. Setting specific poster URLs for known series...")
        
        # Petrocelli
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE title LIKE '%Petrocelli%'
        """), {
            'poster_url': f"{railway_url}/pecantv_series/petrocelli/Petrocelli1_poster.jpg"
        })
        print(f"✅ Updated Petrocelli poster URL: {result.rowcount} rows")
        
        # Longstreet
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE title LIKE '%Longstreet%'
        """), {
            'poster_url': f"{railway_url}/pecantv_series/longstreet/Longstreet1_poster.jpg"
        })
        print(f"✅ Updated Longstreet poster URL: {result.rowcount} rows")
        
        # Dragnet
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE title LIKE '%Dragnet%'
        """), {
            'poster_url': f"{railway_url}/pecantv_series/dragnet/Dragnet1_poster.jpg"
        })
        print(f"✅ Updated Dragnet poster URL: {result.rowcount} rows")
        
        # Count of Monte Cristo
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE title LIKE '%Count of Monte Cristo%'
        """), {
            'poster_url': f"{railway_url}/pecantv_series/the_count_of_monte_cristo/count_of_monte_cristo/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png"
        })
        print(f"✅ Updated Count of Monte Cristo poster URL: {result.rowcount} rows")
        
        # Films - use default poster for now
        print("\n📺 5. Setting default poster for films...")
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE type = 'FILM' AND poster_url LIKE '%default_poster%'
        """), {
            'poster_url': f"{railway_url}/pecantv_series/default_poster.jpg"
        })
        print(f"✅ Updated film poster URLs: {result.rowcount} rows")
        
        # Verify the changes
        print(f"\n🔍 Verifying changes...")
        
        # Check a few content items
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            ORDER BY id 
            LIMIT 5
        """))
        
        content_items = result.fetchall()
        for item in content_items:
            print(f"  - {item.title}: {item.poster_url}")
        
        total_updated = gcs_updated + localhost_updated + null_updated
        print(f"\n🎉 Successfully updated {total_updated} poster URLs for Railway deployment!")
        print(f"🌐 All poster URLs now point to: {railway_url}")
        
        return True

if __name__ == "__main__":
    fix_poster_urls_for_railway() 