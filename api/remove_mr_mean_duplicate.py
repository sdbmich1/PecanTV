#!/usr/bin/env python3
"""
Script to remove the duplicate "Mr. Mean: the animated movie" entry
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
        print("🗑️  Removing duplicate 'Mr. Mean: the animated movie' entry...")
        
        # Remove the specific duplicate entry
        result = db.execute(text("""
            DELETE FROM content
            WHERE title = 'Mr. Mean: the animated movie' AND type = 'FILM'
        """))
        
        if result.rowcount > 0:
            print(f"✅ Successfully removed {result.rowcount} duplicate 'Mr. Mean: the animated movie' entry")
        else:
            print("❌ No 'Mr. Mean: the animated movie' entry found to remove")
        
        db.commit()
        print("✅ Cleanup completed!")

if __name__ == "__main__":
    main() 