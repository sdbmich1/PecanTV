#!/usr/bin/env python3
"""
Script to update poster URLs for Black Brigade and Get Christie Love films
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
        print("🎬 Updating poster URLs for Black Brigade and Get Christie Love...")
        
        # Show current poster URLs
        print("\n📺 Current poster URLs:")
        result = db.execute(text("""
            SELECT title, poster_url FROM content 
            WHERE title IN ('Black Brigade', 'Get Christie Love') AND type = 'FILM'
            ORDER BY title
        """))
        
        current_posters = result.fetchall()
        for row in current_posters:
            print(f"  - {row.title}: {row.poster_url}")
        
        # Update Black Brigade poster URL
        print("\n🔄 Updating Black Brigade poster URL...")
        result = db.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE title = 'Black Brigade' AND type = 'FILM'
        """), {
            "poster_url": "https://storage.googleapis.com/pecantv_title_images/Black-Brigade-Feature-Img.png"
        })
        print(f"  - Updated Black Brigade poster URL")
        
        # Update Get Christie Love poster URL
        print("\n🔄 Updating Get Christie Love poster URL...")
        result = db.execute(text("""
            UPDATE content 
            SET poster_url = :poster_url
            WHERE title = 'Get Christie Love' AND type = 'FILM'
        """), {
            "poster_url": "https://storage.googleapis.com/pecantv_title_images/GetChristieLove-Feature-Img-16x9.png"
        })
        print(f"  - Updated Get Christie Love poster URL")
        
        # Commit changes
        db.commit()
        
        # Verify the updates
        print("\n✅ Verification - Updated poster URLs:")
        result = db.execute(text("""
            SELECT title, poster_url FROM content 
            WHERE title IN ('Black Brigade', 'Get Christie Love') AND type = 'FILM'
            ORDER BY title
        """))
        
        updated_posters = result.fetchall()
        for row in updated_posters:
            print(f"  - {row.title}: {row.poster_url}")
        
        print("\n✅ Poster URLs updated successfully!")

if __name__ == "__main__":
    main() 