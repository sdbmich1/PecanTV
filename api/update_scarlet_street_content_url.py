#!/usr/bin/env python3
"""
Script to update content URL for Scarlet Street film
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
        print("🔧 Updating Scarlett Street content URL...")
        content_url = "https://storage.googleapis.com/pecantv_features/Scarlet-Street_2p-1080-full-credits.mp4"
        
        # First, let's check if Scarlett Street exists and show current content_url
        result = db.execute(text("""
            SELECT id, title, content_url, poster_url FROM content
            WHERE title ILIKE '%scarlett street%' AND type = 'FILM'
        """))
        
        scarlet_street = result.fetchone()
        if scarlet_street:
            content_id, title, current_content_url, poster_url = scarlet_street
            print(f"✅ Found Scarlett Street film (ID: {content_id})")
            print(f"   Current content URL: {current_content_url}")
            print(f"   Poster URL: {poster_url}")
            
            # Update the content URL
            update_result = db.execute(text("""
                UPDATE content
                SET content_url = :content_url, updated_at = NOW()
                WHERE id = :content_id
            """), {"content_url": content_url, "content_id": content_id})
            
            if update_result.rowcount > 0:
                print(f"✅ Updated Scarlett Street content URL to: {content_url}")
            else:
                print("❌ Failed to update Scarlett Street content URL.")
        else:
            print("❌ Scarlett Street film not found in database.")
        
        db.commit()

if __name__ == "__main__":
    main() 