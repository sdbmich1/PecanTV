#!/usr/bin/env python3
"""
Script to update Black Brigade trailer URL to the correct one
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
        print("🎬 Updating Black Brigade trailer URL...")
        
        # Show current trailer URL
        print("\n📺 Current Black Brigade trailer URL:")
        result = db.execute(text("""
            SELECT title, trailer_url FROM content 
            WHERE title = 'Black Brigade' AND type = 'FILM'
        """))
        
        current = result.fetchone()
        if current:
            print(f"  - {current.title}: {current.trailer_url}")
        
        # Update to the correct trailer URL
        print("\n🔄 Updating to correct trailer URL...")
        result = db.execute(text("""
            UPDATE content 
            SET trailer_url = :trailer_url
            WHERE title = 'Black Brigade' AND type = 'FILM'
        """), {
            "trailer_url": "https://storage.googleapis.com/pecantv_trailers/BlackBrigade_Trailer_35sFinal.mp4"
        })
        
        print(f"  - Updated Black Brigade trailer URL")
        
        # Commit changes
        db.commit()
        
        # Verify the update
        print("\n✅ Verification - Updated trailer URL:")
        result = db.execute(text("""
            SELECT title, trailer_url FROM content 
            WHERE title = 'Black Brigade' AND type = 'FILM'
        """))
        
        updated = result.fetchone()
        if updated:
            print(f"  - {updated.title}: {updated.trailer_url}")
        
        print("\n✅ Black Brigade trailer URL updated successfully!")

if __name__ == "__main__":
    main() 