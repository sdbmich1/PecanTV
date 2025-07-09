#!/usr/bin/env python3
"""
Script to update poster URLs to use specific posters for each content item
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_specific_posters():
    """Update poster URLs to use specific posters for each content item"""
    
    # Database connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Get all content items
            result = conn.execute(text("""
                SELECT id, title, series_name, episode_number, poster_url 
                FROM content 
                ORDER BY title
            """))
            
            content_items = result.fetchall()
            print(f"📋 Found {len(content_items)} content items")
            
            updates = 0
            
            for item in content_items:
                content_id, title, series_name, episode_number, current_poster = item
                
                # Skip if already has a specific poster (not default)
                if current_poster and not current_poster.endswith('default_poster.jpg'):
                    continue
                
                # Determine the correct poster URL based on content type
                new_poster_url = None
                
                if series_name and episode_number:
                    # Episode - use series poster
                    series_poster = f"http://localhost:8001/pecantv_series/{series_name.lower()}/{series_name}{episode_number}_poster.jpg"
                    new_poster_url = series_poster
                elif series_name:
                    # Series - use first episode poster
                    series_poster = f"http://localhost:8001/pecantv_series/{series_name.lower()}/{series_name}1_poster.jpg"
                    new_poster_url = series_poster
                else:
                    # Film - use title-based poster
                    # Clean title for filename
                    clean_title = title.replace(" ", "").replace("-", "").replace("'", "").replace(":", "")
                    film_poster = f"http://localhost:8001/pecantv_series/{clean_title.lower()}/{clean_title}_poster.jpg"
                    new_poster_url = film_poster
                
                if new_poster_url:
                    # Update the poster URL
                    conn.execute(text("""
                        UPDATE content 
                        SET poster_url = :poster_url 
                        WHERE id = :content_id
                    """), {
                        "poster_url": new_poster_url,
                        "content_id": content_id
                    })
                    
                    updates += 1
                    print(f"✅ Updated {title}: {new_poster_url}")
            
            # Commit changes
            conn.commit()
            print(f"\n🎉 Updated {updates} poster URLs")
            return True
            
    except Exception as e:
        print(f"❌ Error updating poster URLs: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing specific poster URLs...")
    success = fix_specific_posters()
    if success:
        print("✅ Poster URLs updated successfully!")
    else:
        print("❌ Failed to update poster URLs")
        sys.exit(1) 