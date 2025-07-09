#!/usr/bin/env python3
"""
Script to fix Black Brigade description and trailer URLs for both films
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
        print("🔧 Fixing Black Brigade and Get Christie Love metadata...")
        
        # Update Black Brigade description and trailer URL
        print("\n🎬 Updating Black Brigade...")
        result = db.execute(text("""
            UPDATE content 
            SET description = :description, trailer_url = :trailer_url
            WHERE title = 'Black Brigade' AND type = 'FILM'
        """), {
            "description": "A World War II film about a racist captain taking over an all-black regiment to secure a bridge.",
            "trailer_url": "https://storage.googleapis.com/pecantv_features/black_brigade/Black_Brigade_trailer.mp4"
        })
        print(f"  - Updated Black Brigade description and trailer URL")
        
        # Update Get Christie Love trailer URL
        print("\n🎬 Updating Get Christie Love...")
        result = db.execute(text("""
            UPDATE content 
            SET trailer_url = :trailer_url
            WHERE title = 'Get Christie Love' AND type = 'FILM'
        """), {
            "trailer_url": "https://storage.googleapis.com/pecantv_features/christie_love/Get_Christie_Love_trailer.mp4"
        })
        print(f"  - Updated Get Christie Love trailer URL")
        
        # Commit changes
        db.commit()
        print("\n✅ All updates completed successfully!")

if __name__ == "__main__":
    main() 