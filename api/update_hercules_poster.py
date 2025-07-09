#!/usr/bin/env python3
"""
Script to update poster URL for Hercules film
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
        print("🔧 Updating Hercules poster URL...")
        poster_url = "https://storage.googleapis.com/pecantv_title_images/Hercules_title-img.jpg"
        result = db.execute(text("""
            UPDATE content
            SET poster_url = :poster_url
            WHERE title ILIKE '%hercules%' AND type = 'FILM'
        """), {"poster_url": poster_url})
        if result.rowcount > 0:
            print(f"✅ Updated Hercules poster URL to: {poster_url}")
        else:
            print("❌ Hercules film not found or not updated.")
        db.commit()

if __name__ == "__main__":
    main() 