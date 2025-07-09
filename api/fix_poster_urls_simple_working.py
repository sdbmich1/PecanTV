#!/usr/bin/env python3
"""
Fix poster URLs to use the existing working endpoint
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_poster_urls_simple_working():
    """Fix poster URLs to use the existing working endpoint"""
    
    with engine.begin() as conn:
        print("🔧 Fixing poster URLs to use existing working endpoint...")
        print("=" * 60)
        
        # Use the existing working endpoint
        working_poster_url = "http://localhost:8000/pecantv_series/default_poster.jpg"
        
        # Update all poster URLs to use the working endpoint
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :working_poster_url
            WHERE poster_url IS NOT NULL
        """), {
            'working_poster_url': working_poster_url
        })
        
        updated_count = result.rowcount
        print(f"✅ Updated {updated_count} poster URLs to use working endpoint")
        
        # Also update any NULL poster URLs
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :working_poster_url
            WHERE poster_url IS NULL
        """), {
            'working_poster_url': working_poster_url
        })
        
        null_updated = result.rowcount
        if null_updated > 0:
            print(f"✅ Updated {null_updated} NULL poster URLs to use working endpoint")
        
        # Verify the changes
        print(f"\n🔍 Verifying changes...")
        
        # Check Black Brigade and Christie Love
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE title LIKE '%Black Brigade%' OR title LIKE '%Christie Love%'
        """))
        
        special_items = result.fetchall()
        print(f"\nBlack Brigade and Christie Love:")
        for item_id, title, poster_url in special_items:
            print(f"  {title}: {poster_url}")
        
        # Check total content with posters
        result = conn.execute(text("SELECT COUNT(*) FROM content WHERE poster_url IS NOT NULL"))
        content_with_posters = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM content"))
        total_content = result.scalar()
        
        print(f"\n📊 Summary:")
        print(f"  Total content: {total_content}")
        print(f"  Content with posters: {content_with_posters}")
        print(f"  Updated: {updated_count + null_updated} items")
        
        print(f"\n🌐 Working poster URL:")
        print(f"  {working_poster_url}")
        
        print("\n✅ Poster URLs updated to use working endpoint!")

if __name__ == "__main__":
    fix_poster_urls_simple_working() 