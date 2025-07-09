#!/usr/bin/env python3
"""
Script to fix Black Brigade and Get Christie Love - remove from Petrocelli episodes and re-add as films
"""

import os
import sys
import uuid
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
        print("🔧 Fixing Black Brigade and Get Christie Love categorization...")
        
        # 1. Remove from Petrocelli episodes table
        print("\n🗑️  Removing from Petrocelli episodes table...")
        
        # Remove Black Brigade from episodes
        result = db.execute(text("""
            DELETE FROM episodes 
            WHERE title ILIKE '%black brigade%'
        """))
        print(f"  - Removed Black Brigade from episodes")
        
        # Remove Get Christie Love from episodes
        result = db.execute(text("""
            DELETE FROM episodes 
            WHERE title ILIKE '%get christie love%'
        """))
        print(f"  - Removed Get Christie Love from episodes")
        
        # 2. Add as films to content table
        print(f"\n➕ Adding as films to content table...")
        
        # Remove all Black Brigade and Get Christie Love entries from content table
        print("\n🗑️  Removing all 'Black Brigade' and 'Get Christie Love' entries from content table...")
        result = db.execute(text("""
            DELETE FROM content WHERE (title ILIKE '%black brigade%' OR title ILIKE '%get christie love%') AND type = 'FILM'
        """))
        print(f"  - Removed all 'Black Brigade' and 'Get Christie Love' entries from content table")
        
        # Black Brigade film
        black_brigade_uuid = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO content (uuid, title, type, content_url, poster_url, trailer_url, description, genre_id, rating_id, runtime)
            VALUES (:uuid, :title, :type, :content_url, :poster_url, :trailer_url, :description, :genre_id, :rating_id, :runtime)
        """), {
            "uuid": black_brigade_uuid,
            "title": "Black Brigade",
            "type": "FILM",
            "content_url": "https://storage.googleapis.com/pecantv_series/black_brigade/Black_Brigade.mp4",
            "poster_url": "https://storage.googleapis.com/pecantv_series/black_brigade/Black_Brigade_poster.jpg",
            "trailer_url": "https://storage.googleapis.com/pecantv_series/black_brigade/Black_Brigade_trailer.mp4",
            "description": "A crime drama film about a special police unit.",
            "genre_id": 1,  # Assuming 1 is Action/Drama
            "rating_id": 1,  # Assuming 1 is PG-13
            "runtime": 120   # Assuming 120 minutes runtime
        })
        print(f"  - Added Black Brigade as film")
        
        # Get Christie Love film
        christie_love_uuid = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO content (uuid, title, type, content_url, poster_url, trailer_url, description, genre_id, rating_id, runtime)
            VALUES (:uuid, :title, :type, :content_url, :poster_url, :trailer_url, :description, :genre_id, :rating_id, :runtime)
        """), {
            "uuid": christie_love_uuid,
            "title": "Get Christie Love",
            "type": "FILM",
            "content_url": "https://storage.googleapis.com/pecantv_series/christie_love/Get_Christie_Love.mp4",
            "poster_url": "https://storage.googleapis.com/pecantv_series/christie_love/Get_Christie_Love_poster.jpg",
            "trailer_url": "https://storage.googleapis.com/pecantv_series/christie_love/Get_Christie_Love_trailer.mp4",
            "description": "A crime drama film about an undercover police officer.",
            "genre_id": 1,  # Assuming 1 is Action/Drama
            "rating_id": 1,  # Assuming 1 is PG-13
            "runtime": 120   # Assuming 120 minutes runtime
        })
        print(f"  - Added Get Christie Love as film")
        
        # Remove stray Get Christie Love (with non-breaking space)
        print("\n🗑️  Removing stray 'Get Christie Love' (with non-breaking space) from content table...")
        result = db.execute(text("""
            DELETE FROM content WHERE title LIKE 'Get\u00a0Christie Love' AND type = 'FILM'
        """))
        print(f"  - Removed stray 'Get Christie Love' entry")
        
        # Commit changes
        db.commit()
        print(f"\n✅ Black Brigade and Get Christie Love fixed!")
        
        # Verify the fix
        print(f"\n🔍 Verification:")
        
        # Check content table
        result = db.execute(text("""
            SELECT title, type FROM content 
            WHERE title ILIKE '%black brigade%' OR title ILIKE '%christie love%'
            ORDER BY title
        """))
        
        content_entries = result.fetchall()
        print(f"📺 Content table entries:")
        for row in content_entries:
            print(f"  - {row.title} (Type: {row.type})")
        
        # Check episodes table
        result = db.execute(text("""
            SELECT e.title, e.episode_number
            FROM episodes e
            JOIN content c ON e.content_uuid = c.uuid
            WHERE c.title ILIKE '%petrocelli%'
            ORDER BY e.episode_number
        """))
        
        episodes = result.fetchall()
        print(f"\n🎬 Petrocelli episodes:")
        for row in episodes:
            print(f"  - {row.title} (Episode {row.episode_number})")

if __name__ == "__main__":
    main() 