#!/usr/bin/env python3
"""
Script to update poster URL for Scarlet Street film
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
        print("🔧 Updating Scarlet Street poster URL...")
        poster_url = "https://storage.googleapis.com/pecantv_title_images/Scarlet-Street_Title-Img2.jpg"
        result = db.execute(text("""
            UPDATE content
            SET poster_url = :poster_url
            WHERE title ILIKE '%scarlet street%' AND type = 'FILM'
        """), {"poster_url": poster_url})
        if result.rowcount > 0:
            print(f"✅ Updated Scarlet Street poster URL to: {poster_url}")
        else:
            print("❌ Scarlet Street film not found or not updated.")
        db.commit()

if __name__ == "__main__":
    main() 