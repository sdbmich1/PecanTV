#!/usr/bin/env python3
"""
Fix image URLs by removing Cloudflare optimization and using direct GCS URLs
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_image_urls_remove_cloudflare():
    """Fix image URLs by removing Cloudflare optimization"""
    
    with engine.connect() as conn:
        print("🔧 Fixing image URLs by removing Cloudflare optimization...")
        print("=" * 50)
        
        # Find all content with Cloudflare URLs
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url LIKE '%images.pecantv.com%'
        """))
        
        cloudflare_content = result.fetchall()
        print(f"Found {len(cloudflare_content)} content entries with Cloudflare URLs")
        
        for content_id, title, poster_url in cloudflare_content:
            print(f"  - ID: {content_id}, Title: '{title}'")
            print(f"    Cloudflare URL: {poster_url}")
            
            # Extract the original GCS URL from the Cloudflare URL
            if poster_url and 'https://storage.googleapis.com/' in poster_url:
                # Find the GCS part and use it directly
                gcs_start = poster_url.find('https://storage.googleapis.com/')
                if gcs_start != -1:
                    fixed_url = poster_url[gcs_start:]
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
        
        # Also fix any URLs that end with just a path (no filename)
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE poster_url LIKE '%storage.googleapis.com/pecantv_series/%' 
            AND poster_url NOT LIKE '%.jpg' 
            AND poster_url NOT LIKE '%.png' 
            AND poster_url NOT LIKE '%.jpeg'
            AND poster_url NOT LIKE '%.gif'
        """))
        
        incomplete_urls = result.fetchall()
        print(f"\nFound {len(incomplete_urls)} content entries with incomplete poster URLs")
        
        for content_id, title, poster_url in incomplete_urls:
            print(f"  - ID: {content_id}, Title: '{title}'")
            print(f"    Incomplete URL: {poster_url}")
            
            # Add a default image filename
            if poster_url and not poster_url.endswith('/'):
                fixed_url = poster_url + '/poster.jpg'
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
        print(f"\n🎉 Successfully fixed image URLs!")

if __name__ == "__main__":
    fix_image_urls_remove_cloudflare() 