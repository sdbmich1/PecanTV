#!/usr/bin/env python3
"""
Script to fix poster images by creating proper poster files
"""

import os
import shutil
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_poster_images():
    """Fix poster images by creating proper poster files"""
    
    # Get the path to pecantv_series directory
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pecantv_series")
    default_poster = os.path.join(static_path, "default_poster.jpg")
    
    if not os.path.exists(default_poster):
        print(f"❌ Default poster not found: {default_poster}")
        return False
    
    print(f"✅ Found default poster: {default_poster}")
    
    # Database connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Get content with poster URLs
            result = conn.execute(text("""
                SELECT id, title, poster_url 
                FROM content 
                WHERE poster_url IS NOT NULL 
                AND poster_url != ''
                ORDER BY title
            """))
            
            content_items = result.fetchall()
            print(f"📋 Found {len(content_items)} content items with poster URLs")
            
            fixed_count = 0
            
            for item in content_items:
                content_id, title, poster_url = item
                
                # Extract local path from URL
                if poster_url.startswith('http://localhost:8001/pecantv_series/'):
                    local_path = poster_url.replace('http://localhost:8001/pecantv_series/', '')
                elif poster_url.startswith('http://localhost:8000/pecantv_series/'):
                    local_path = poster_url.replace('http://localhost:8000/pecantv_series/', '')
                else:
                    continue
                
                full_path = os.path.join(static_path, local_path)
                
                # Check if poster file exists and is valid
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    if file_size < 1000:  # Less than 1KB, likely corrupted/empty
                        print(f"🔧 Fixing corrupted poster for '{title}' ({file_size} bytes)")
                        
                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        
                        # Copy default poster
                        shutil.copy2(default_poster, full_path)
                        fixed_count += 1
                    else:
                        print(f"✅ Poster for '{title}' is valid ({file_size} bytes)")
                else:
                    print(f"🔧 Creating missing poster for '{title}'")
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Copy default poster
                    shutil.copy2(default_poster, full_path)
                    fixed_count += 1
            
            print(f"🎉 Fixed {fixed_count} poster images")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing poster images: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Fixing poster images...")
    success = fix_poster_images()
    
    if success:
        print("✅ Poster image fix completed successfully!")
    else:
        print("❌ Poster image fix failed!")
        sys.exit(1) 