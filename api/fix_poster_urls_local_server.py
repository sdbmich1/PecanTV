#!/usr/bin/env python3
"""
Fix poster URLs to use local server with GCS-style paths for iOS app compatibility
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_poster_urls_local_server():
    """Fix poster URLs to use local server with GCS-style paths"""
    
    with engine.begin() as conn:
        print("🔧 Fixing poster URLs to use local server with GCS-style paths...")
        print("=" * 60)
        
        # Use local server with GCS-style paths
        local_server_url = "http://localhost:8000"
        gcs_style_base = f"{local_server_url}/storage.googleapis.com/pecantv_series"
        
        # Update all poster URLs to use local server
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :new_poster_url
            WHERE poster_url LIKE '%storage.googleapis.com%'
        """), {
            'new_poster_url': f"{gcs_style_base}/default_poster.jpg"
        })
        
        updated_count = result.rowcount
        print(f"✅ Updated {updated_count} poster URLs to use local server")
        
        # Also update any NULL poster URLs
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :default_poster_url
            WHERE poster_url IS NULL
        """), {
            'default_poster_url': f"{gcs_style_base}/default_poster.jpg"
        })
        
        null_updated = result.rowcount
        if null_updated > 0:
            print(f"✅ Updated {null_updated} NULL poster URLs to use default")
        
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
        
        print(f"\n🌐 Local server poster URL format:")
        print(f"  {gcs_style_base}/default_poster.jpg")
        
        print("\n✅ Poster URLs updated to use local server!")

if __name__ == "__main__":
    fix_poster_urls_local_server() 