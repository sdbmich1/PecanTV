#!/usr/bin/env python3
"""
Fix poster URLs to use proper GCS URLs instead of local URLs
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_poster_urls_properly():
    """Fix poster URLs to use GCS URLs"""
    
    with engine.begin() as conn:
        print("🔧 Fixing poster URLs to use GCS URLs...")
        print("=" * 50)
        
        # First, let's see what content we have and their current poster URLs
        result = conn.execute(text("""
            SELECT id, title, type, poster_url, content_url 
            FROM content 
            WHERE poster_url IS NOT NULL
            ORDER BY id
        """))
        
        content_items = result.fetchall()
        print(f"Found {len(content_items)} content items with poster URLs")
        
        # Define the GCS base URL for posters
        gcs_base_url = "https://storage.googleapis.com/pecantv_series"
        default_poster_url = f"{gcs_base_url}/default_poster.jpg"
        
        updated_count = 0
        
        for content_id, title, content_type, current_poster_url, content_url in content_items:
            new_poster_url = None
            
            # For series, use the first episode's poster
            if content_type == "SERIES":
                # Get the series name from the title
                series_name = title.lower().replace(" ", "").replace("'", "")
                
                # Check if we have a specific poster for this series
                if "dragnet" in series_name:
                    new_poster_url = f"{gcs_base_url}/dragnet/Dragnet1_poster.jpg"
                elif "petrocelli" in series_name:
                    new_poster_url = f"{gcs_base_url}/petrocelli/Petrocelli1_poster.jpg"
                elif "longstreet" in series_name:
                    new_poster_url = f"{gcs_base_url}/longstreet/Longstreet1_poster.jpg"
                elif "christie" in title.lower():
                    new_poster_url = f"{gcs_base_url}/christie_love/ChristieLove1_poster.jpg"
                else:
                    # Use default poster for series without specific posters
                    new_poster_url = default_poster_url
            
            # For films, use specific poster if available
            elif content_type == "FILM":
                if "black brigade" in title.lower():
                    new_poster_url = f"{gcs_base_url}/black_brigade/BlackBrigade_poster.jpg"
                elif "christie love" in title.lower():
                    new_poster_url = f"{gcs_base_url}/christie_love/ChristieLove_poster.jpg"
                else:
                    # Use default poster for films without specific posters
                    new_poster_url = default_poster_url
            
            # Update the poster URL if it's different
            if new_poster_url and new_poster_url != current_poster_url:
                conn.execute(text("""
                    UPDATE content 
                    SET poster_url = :poster_url
                    WHERE id = :content_id
                """), {
                    'poster_url': new_poster_url,
                    'content_id': content_id
                })
                
                print(f"  ✅ {title} ({content_type}): {new_poster_url}")
                updated_count += 1
        
        # Also update any content with NULL poster URLs to use default
        result = conn.execute(text("""
            UPDATE content 
            SET poster_url = :default_poster_url
            WHERE poster_url IS NULL
        """), {
            'default_poster_url': default_poster_url
        })
        
        null_updated = result.rowcount
        if null_updated > 0:
            print(f"  ✅ Updated {null_updated} items with NULL poster URLs to use default")
            updated_count += null_updated
        
        print(f"\n🔍 Verifying fixes...")
        
        # Check Black Brigade and Christie Love specifically
        result = conn.execute(text("""
            SELECT id, title, type, poster_url 
            FROM content 
            WHERE title LIKE '%Black Brigade%' OR title LIKE '%Christie Love%'
        """))
        
        special_items = result.fetchall()
        print(f"\nBlack Brigade and Christie Love:")
        for item_id, title, item_type, poster_url in special_items:
            print(f"  {title} ({item_type}): {poster_url}")
        
        # Check total content count
        result = conn.execute(text("SELECT COUNT(*) FROM content"))
        total_content = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM content WHERE poster_url IS NOT NULL"))
        content_with_posters = result.scalar()
        
        print(f"\n📊 Summary:")
        print(f"  Total content: {total_content}")
        print(f"  Content with posters: {content_with_posters}")
        print(f"  Updated: {updated_count} items")
        
        print("\n✅ Poster URLs fixed!")

if __name__ == "__main__":
    fix_poster_urls_properly() 