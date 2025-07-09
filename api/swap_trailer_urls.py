#!/usr/bin/env python3
"""
Script to swap trailer URLs between Black Brigade and Get Christie Love
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    return database_url

def main():
    # Create database connection
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        print("🔄 Swapping trailer URLs between Black Brigade and Get Christie Love...")
        
        # First, let's see what the current trailer URLs are
        print("\n📺 Current trailer URLs:")
        result = db.execute(text("""
            SELECT title, trailer_url FROM content 
            WHERE title IN ('Black Brigade', 'Get Christie Love') AND type = 'FILM'
            ORDER BY title
        """))
        
        current_urls = result.fetchall()
        for row in current_urls:
            print(f"  - {row.title}: {row.trailer_url}")
        
        # Now swap the URLs
        print("\n🔄 Swapping URLs...")
        
        # Update Black Brigade to use the first trailer (Christie Love's current URL)
        result = db.execute(text("""
            UPDATE content 
            SET trailer_url = :trailer_url
            WHERE title = 'Black Brigade' AND type = 'FILM'
        """), {
            "trailer_url": "https://storage.googleapis.com/pecantv_features/christie_love/Get_Christie_Love_trailer.mp4"
        })
        print(f"  - Updated Black Brigade trailer URL")
        
        # Update Get Christie Love to use the second trailer (Black Brigade's current URL)
        result = db.execute(text("""
            UPDATE content 
            SET trailer_url = :trailer_url
            WHERE title = 'Get Christie Love' AND type = 'FILM'
        """), {
            "trailer_url": "https://storage.googleapis.com/pecantv_features/black_brigade/Black_Brigade_trailer.mp4"
        })
        print(f"  - Updated Get Christie Love trailer URL")
        
        # Commit changes
        db.commit()
        
        # Verify the changes
        print("\n✅ Verification - Updated trailer URLs:")
        result = db.execute(text("""
            SELECT title, trailer_url FROM content 
            WHERE title IN ('Black Brigade', 'Get Christie Love') AND type = 'FILM'
            ORDER BY title
        """))
        
        updated_urls = result.fetchall()
        for row in updated_urls:
            print(f"  - {row.title}: {row.trailer_url}")
        
        print("\n✅ Trailer URLs swapped successfully!")

if __name__ == "__main__":
    main() 