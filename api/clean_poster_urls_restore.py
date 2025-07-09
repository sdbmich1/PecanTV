#!/usr/bin/env python3
"""
Clean poster URLs - restore proper poster URLs for each content item
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text
import os

def clean_poster_urls_restore():
    """Restore proper poster URLs for each content item"""
    
    with engine.begin() as conn:
        print("🧹 Cleaning poster URLs - restoring proper posters...")
        print("=" * 60)
        
        # Define the base URL for local server
        base_url = "http://localhost:8000/pecantv_series"
        
        # Get all content items
        result = conn.execute(text("""
            SELECT id, title, type, content_url 
            FROM content 
            ORDER BY id
        """))
        
        content_items = result.fetchall()
        print(f"Processing {len(content_items)} content items...")
        
        updated_count = 0
        
        for content_id, title, content_type, content_url in content_items:
            poster_url = None
            
            # For series, check if specific poster exists
            if content_type == "SERIES":
                series_name = title.lower().replace(" ", "").replace("'", "").replace("-", "")
                
                # Check for specific series posters
                if "dragnet" in series_name:
                    poster_path = f"../pecantv_series/dragnet/Dragnet1_poster.jpg"
                    if os.path.exists(poster_path):
                        poster_url = f"{base_url}/dragnet/Dragnet1_poster.jpg"
                elif "petrocelli" in series_name:
                    poster_path = f"../pecantv_series/petrocelli/Petrocelli1_poster.jpg"
                    if os.path.exists(poster_path):
                        poster_url = f"{base_url}/petrocelli/Petrocelli1_poster.jpg"
                elif "longstreet" in series_name:
                    poster_path = f"../pecantv_series/longstreet/Longstreet1_poster.jpg"
                    if os.path.exists(poster_path):
                        poster_url = f"{base_url}/longstreet/Longstreet1_poster.jpg"
                elif "christie" in title.lower():
                    poster_path = f"../pecantv_series/christie_love/ChristieLove1_poster.jpg"
                    if os.path.exists(poster_path):
                        poster_url = f"{base_url}/christie_love/ChristieLove1_poster.jpg"
                
                # If no specific poster found, use default
                if not poster_url:
                    poster_url = f"{base_url}/default_poster.jpg"
            
            # For films, check for specific posters
            elif content_type == "FILM":
                film_name = title.lower().replace(" ", "").replace("'", "").replace("-", "")
                
                # Check for specific film posters
                if "black brigade" in title.lower():
                    poster_path = f"../pecantv_series/black_brigade/BlackBrigade_poster.jpg"
                    if os.path.exists(poster_path):
                        poster_url = f"{base_url}/black_brigade/BlackBrigade_poster.jpg"
                elif "christie love" in title.lower():
                    poster_path = f"../pecantv_series/christie_love/ChristieLove_poster.jpg"
                    if os.path.exists(poster_path):
                        poster_url = f"{base_url}/christie_love/ChristieLove_poster.jpg"
                
                # If no specific poster found, use default
                if not poster_url:
                    poster_url = f"{base_url}/default_poster.jpg"
            
            # Update the poster URL
            if poster_url:
                conn.execute(text("""
                    UPDATE content 
                    SET poster_url = :poster_url
                    WHERE id = :content_id
                """), {
                    'poster_url': poster_url,
                    'content_id': content_id
                })
                
                if content_id in [3, 7, 21, 68]:  # Show specific items
                    print(f"  ✅ {title} ({content_type}): {poster_url}")
                
                updated_count += 1
        
        # Verify the changes
        print(f"\n🔍 Verifying changes...")
        
        # Check specific content items
        result = conn.execute(text("""
            SELECT id, title, type, poster_url 
            FROM content 
            WHERE id IN (3, 7, 21, 68)
        """))
        
        special_items = result.fetchall()
        print(f"\nKey content items:")
        for item_id, title, item_type, poster_url in special_items:
            print(f"  {title} ({item_type}): {poster_url}")
        
        # Check total content with posters
        result = conn.execute(text("SELECT COUNT(*) FROM content WHERE poster_url IS NOT NULL"))
        content_with_posters = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM content"))
        total_content = result.scalar()
        
        print(f"\n📊 Summary:")
        print(f"  Total content: {total_content}")
        print(f"  Content with posters: {content_with_posters}")
        print(f"  Updated: {updated_count} items")
        
        print("\n✅ Poster URLs cleaned and restored!")

if __name__ == "__main__":
    clean_poster_urls_restore() 