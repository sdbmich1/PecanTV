#!/usr/bin/env python3
"""
Script to check Petrocelli episodes and fix categorization issues
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
        print("🔍 Checking Petrocelli episodes in database...")
        
        # Check content table for Petrocelli-related entries
        print("\n📺 Content table (films and series):")
        result = db.execute(text("""
            SELECT id, title, type, content_url 
            FROM content 
            WHERE title ILIKE '%petrocelli%' 
               OR title ILIKE '%deadly journey%' 
               OR title ILIKE '%shadow of fear%' 
               OR title ILIKE '%black brigade%' 
               OR title ILIKE '%christie love%'
            ORDER BY title
        """))
        
        content_entries = result.fetchall()
        for row in content_entries:
            print(f"  - {row.title} (ID: {row.id}, Type: {row.type})")
        
        # Check episodes table for Petrocelli episodes
        print("\n🎬 Episodes table:")
        result = db.execute(text("""
            SELECT e.id, e.title, e.episode_number, e.content_uuid, c.title as series_title
            FROM episodes e
            JOIN content c ON e.content_uuid = c.uuid
            WHERE c.title ILIKE '%petrocelli%'
            ORDER BY e.episode_number
        """))
        
        episodes = result.fetchall()
        for row in episodes:
            print(f"  - {row.title} (Episode {row.episode_number}, Series: {row.series_title})")
        
        # Check for episodes that should be Petrocelli but are in content table as films
        print("\n⚠️  Episodes incorrectly in content table as films:")
        result = db.execute(text("""
            SELECT id, title, type, content_url
            FROM content 
            WHERE type = 'FILM' 
              AND (title ILIKE '%deadly journey%' 
                   OR title ILIKE '%shadow of fear%'
                   OR title ILIKE '%black brigade%'
                   OR title ILIKE '%christie love%')
        """))
        
        film_episodes = result.fetchall()
        for row in film_episodes:
            print(f"  - {row.title} (ID: {row.id}) - Should be Petrocelli episode")
        
        # Check Petrocelli series entry
        print("\n📺 Petrocelli series entry:")
        result = db.execute(text("""
            SELECT id, title, type, content_url
            FROM content 
            WHERE title ILIKE '%petrocelli%' AND type = 'SERIES'
        """))
        
        series_entry = result.fetchone()
        if series_entry:
            print(f"  - {series_entry.title} (ID: {series_entry.id})")
        else:
            print("  - No Petrocelli series entry found!")
        
        print(f"\n📊 Summary:")
        print(f"  - Content entries: {len(content_entries)}")
        print(f"  - Episodes in episodes table: {len(episodes)}")
        print(f"  - Episodes incorrectly as films: {len(film_episodes)}")

if __name__ == "__main__":
    main() 