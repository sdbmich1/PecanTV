#!/usr/bin/env python3
"""
Script to set all content to use the default poster since specific poster files don't exist yet
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_default_posters():
    """Set all content to use the default poster"""
    
    # Database connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Update all content to use default poster
            result = conn.execute(text("""
                UPDATE content 
                SET poster_url = 'http://localhost:8001/pecantv_series/default_poster.jpg'
                WHERE poster_url != 'http://localhost:8001/pecantv_series/default_poster.jpg'
            """))
            
            # Commit changes
            conn.commit()
            print(f"✅ Updated all content to use default poster")
            return True
            
    except Exception as e:
        print(f"❌ Error updating poster URLs: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting all content to use default poster...")
    success = fix_default_posters()
    if success:
        print("✅ Default poster URLs updated successfully!")
    else:
        print("❌ Failed to update poster URLs")
        sys.exit(1) 