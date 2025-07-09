#!/usr/bin/env python3
"""
Fix remaining malformed image URLs that still have double URLs
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_remaining_malformed_urls():
    """Fix remaining malformed image URLs"""
    
    with engine.connect() as conn:
        print("🔧 Fixing remaining malformed image URLs...")
        print("=" * 50)
        
        # Check for any remaining malformed URLs in content table
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url LIKE '%https://%https://%'
        """))
        
        malformed_content = result.fetchall()
        print(f"Found {len(malformed_content)} content entries with malformed poster URLs")
        
        for content_id, title, poster_url in malformed_content:
            print(f"  - ID: {content_id}, Title: '{title}'")
            print(f"    Malformed URL: {poster_url}")
            
            # Fix the URL by removing the duplicate part
            if poster_url and 'https://' in poster_url:
                # Find the second occurrence and keep only the first part
                parts = poster_url.split('https://')
                if len(parts) > 2:
                    # Keep only the first https:// part
                    fixed_url = 'https://' + parts[1]
                    print(f"    Fixed URL: {fixed_url}")
                    
                    conn.execute(text("""
                        UPDATE content 
                        SET poster_url = :poster_url
                        WHERE id = :content_id
                    """), {
                        "poster_url": fixed_url,
                        "content_id": content_id
                    })
                    print(f"    ✅ Updated")
        
        # Also check for any URLs that end with just a path (no filename)
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url LIKE '%/pecantv_series/%' AND poster_url NOT LIKE '%.jpg' AND poster_url NOT LIKE '%.png' AND poster_url NOT LIKE '%.jpeg'
        """))
        
        incomplete_urls = result.fetchall()
        print(f"\nFound {len(incomplete_urls)} content entries with incomplete poster URLs")
        
        for content_id, title, poster_url in incomplete_urls:
            print(f"  - ID: {content_id}, Title: '{title}'")
            print(f"    Incomplete URL: {poster_url}")
            
            # Add a default image filename
            if poster_url and not poster_url.endswith('/'):
                fixed_url = poster_url + '/title-image.png'
                print(f"    Fixed URL: {fixed_url}")
                
                conn.execute(text("""
                    UPDATE content 
                    SET poster_url = :poster_url
                    WHERE id = :content_id
                """), {
                    "poster_url": fixed_url,
                    "content_id": content_id
                })
                print(f"    ✅ Updated")
        
        conn.commit()
        print(f"\n🎉 Successfully fixed remaining malformed URLs!")

if __name__ == "__main__":
    fix_remaining_malformed_urls() 