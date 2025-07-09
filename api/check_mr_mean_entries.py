#!/usr/bin/env python3
"""
Script to check what Mr Mean entries exist in the database
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
        print("🔍 Checking for Mr Mean entries in the database...")
        
        # Find all Mr Mean entries
        result = db.execute(text("""
            SELECT id, title, type, poster_url FROM content
            WHERE title ILIKE '%mr mean%' OR title ILIKE '%mr. mean%'
            ORDER BY title
        """))
        
        entries = result.fetchall()
        if entries:
            print(f"\n📺 Found {len(entries)} Mr Mean entries:")
            for entry in entries:
                print(f"  - ID: {entry.id}, Title: '{entry.title}', Type: {entry.type}")
                print(f"    Poster: {entry.poster_url}")
        else:
            print("❌ No Mr Mean entries found in the database")

if __name__ == "__main__":
    main() 