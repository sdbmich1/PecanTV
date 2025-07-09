#!/usr/bin/env python3
"""
Script to update poster URLs in the database to use port 8001 instead of 8000
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_poster_urls():
    """Update poster URLs to use port 8001"""
    
    # Database connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Update content table poster URLs
            result = conn.execute(text("""
                UPDATE content 
                SET poster_url = REPLACE(poster_url, 'localhost:8000', 'localhost:8001')
                WHERE poster_url LIKE '%localhost:8000%'
            """))
            
            content_updated = result.rowcount
            print(f"✅ Updated {content_updated} content poster URLs")
            
            # Update episodes table poster URLs
            result = conn.execute(text("""
                UPDATE episodes 
                SET poster_url = REPLACE(poster_url, 'localhost:8000', 'localhost:8001')
                WHERE poster_url LIKE '%localhost:8000%'
            """))
            
            episodes_updated = result.rowcount
            print(f"✅ Updated {episodes_updated} episode poster URLs")
            
            conn.commit()
            
            total_updated = content_updated + episodes_updated
            print(f"🎉 Successfully updated {total_updated} poster URLs to use port 8001")
            
            return True
            
    except Exception as e:
        print(f"❌ Error updating poster URLs: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Updating poster URLs to use port 8001...")
    success = update_poster_urls()
    
    if success:
        print("✅ Poster URL update completed successfully!")
    else:
        print("❌ Poster URL update failed!")
        sys.exit(1) 