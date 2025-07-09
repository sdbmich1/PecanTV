#!/usr/bin/env python3
"""
Script to set all content with missing or null poster_url to use the white placeholder image
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_white_placeholder_posters():
    """Set all content with missing/null poster_url to white placeholder"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    placeholder_url = "http://localhost:8001/pecantv_series/white_placeholder.jpg"
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Update content with null or empty poster_url
            result = conn.execute(text("""
                UPDATE content
                SET poster_url = :placeholder_url
                WHERE poster_url IS NULL OR poster_url = ''
            """), {"placeholder_url": placeholder_url})
            print(f"✅ Updated {result.rowcount} content items to use white placeholder poster.")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    return True

if __name__ == "__main__":
    fix_white_placeholder_posters() 