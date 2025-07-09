#!/usr/bin/env python3
"""
Script to set ALL content poster URLs to the white placeholder image
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_all_posters_to_white():
    """Set all content poster URLs to white placeholder"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    placeholder_url = "http://localhost:8001/pecantv_series/white_placeholder.jpg"
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Update all content to use white placeholder
            result = conn.execute(text("""
                UPDATE content
                SET poster_url = :placeholder_url
            """), {"placeholder_url": placeholder_url})
            print(f"✅ Updated {result.rowcount} content items to use white placeholder poster.")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    return True

if __name__ == "__main__":
    fix_all_posters_to_white() 