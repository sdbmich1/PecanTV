#!/usr/bin/env python3
"""
Script to update poster URLs for Mr Mean and Dick Tracy films
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
        print("🔧 Updating poster URLs for Mr Mean and Dick Tracy...")
        
        # Update Mr Mean poster
        mr_mean_poster_url = "https://storage.googleapis.com/pecantv_title_images/MrMean_feature-Img.jpg"
        result = db.execute(text("""
            UPDATE content
            SET poster_url = :poster_url
            WHERE title ILIKE '%mr mean%' AND type = 'FILM'
        """), {"poster_url": mr_mean_poster_url})
        
        if result.rowcount > 0:
            print(f"✅ Updated Mr Mean poster URL to: {mr_mean_poster_url}")
        else:
            print("❌ Mr Mean film not found or not updated.")
        
        # Update Dick Tracy poster
        dick_tracy_poster_url = "https://storage.googleapis.com/pecantv_title_images/Dick-Tracy_Title-Img.jpg"
        result = db.execute(text("""
            UPDATE content
            SET poster_url = :poster_url
            WHERE title ILIKE '%dick tracy%' AND type = 'FILM'
        """), {"poster_url": dick_tracy_poster_url})
        
        if result.rowcount > 0:
            print(f"✅ Updated Dick Tracy poster URL to: {dick_tracy_poster_url}")
        else:
            print("❌ Dick Tracy film not found or not updated.")
        
        db.commit()
        print("\n✅ Poster updates completed!")

if __name__ == "__main__":
    main() 