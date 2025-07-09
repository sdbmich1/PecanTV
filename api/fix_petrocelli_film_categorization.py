#!/usr/bin/env python3
"""
Script to fix Petrocelli episode categorization issues
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
        print("🔧 Fixing Petrocelli episode categorization...")
        
        # Get Petrocelli series ID and UUID
        result = db.execute(text("""
            SELECT id, uuid FROM content 
            WHERE title ILIKE '%petrocelli%' AND type = 'SERIES'
        """))
        petrocelli_series = result.fetchone()
        
        if not petrocelli_series:
            print("❌ Petrocelli series not found!")
            return
        
        petrocelli_id = petrocelli_series[0]
        petrocelli_uuid = petrocelli_series[1]
        print(f"✅ Found Petrocelli series ID: {petrocelli_id}, UUID: {petrocelli_uuid}")
        
        # Get current episodes to avoid conflicts
        result = db.execute(text("""
            SELECT title, episode_number FROM episodes 
            WHERE content_uuid = :petrocelli_uuid 
            ORDER BY episode_number
        """), {"petrocelli_uuid": petrocelli_uuid})
        
        existing_episodes = result.fetchall()
        existing_titles = [row[0] for row in existing_episodes]
        existing_numbers = [row[1] for row in existing_episodes]
        print(f"📺 Existing episode numbers: {existing_numbers}")
        print(f"📺 Existing episode titles: {existing_titles}")
        
        # Find next available episode numbers
        next_episode = max(existing_numbers) + 1 if existing_numbers else 1
        
        # 1. Remove duplicate films that are already episodes
        print("\n🗑️  Removing duplicate films that are already episodes...")
        
        # Deadly Journey (already episode 1)
        result = db.execute(text("""
            DELETE FROM content 
            WHERE title ILIKE '%deadly journey%' AND type = 'FILM'
        """))
        print(f"  - Removed Deadly Journey film (already episode 1)")
        
        # Shadow of Fear (already episode 4)
        result = db.execute(text("""
            DELETE FROM content 
            WHERE title ILIKE '%shadow of fear%' AND type = 'FILM'
        """))
        print(f"  - Removed Shadow of Fear film (already episode 4)")
        
        # 2. Add missing episodes to episodes table
        print(f"\n➕ Adding missing episodes to episodes table...")
        
        # Black Brigade
        if "Black Brigade" not in existing_titles:
            black_brigade_uuid = str(uuid.uuid4())
            db.execute(text("""
                INSERT INTO episodes (uuid, title, episode_number, content_uuid, series_id, season_number, content_url, poster_url)
                VALUES (:uuid, :title, :episode_number, :content_uuid, :series_id, :season_number, :content_url, :poster_url)
            """), {
                "uuid": black_brigade_uuid,
                "title": "Black Brigade",
                "episode_number": next_episode,
                "content_uuid": petrocelli_uuid,
                "series_id": petrocelli_id,
                "season_number": 1,
                "content_url": "https://storage.googleapis.com/pecantv_series/petrocelli/Black_Brigade.mp4",
                "poster_url": "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli1_poster.jpg"
            })
            print(f"  - Added Black Brigade as episode {next_episode}")
            next_episode += 1
        
        # Get Christie Love
        if "Get Christie Love" not in existing_titles:
            christie_love_uuid = str(uuid.uuid4())
            db.execute(text("""
                INSERT INTO episodes (uuid, title, episode_number, content_uuid, series_id, season_number, content_url, poster_url)
                VALUES (:uuid, :title, :episode_number, :content_uuid, :series_id, :season_number, :content_url, :poster_url)
            """), {
                "uuid": christie_love_uuid,
                "title": "Get Christie Love",
                "episode_number": next_episode,
                "content_uuid": petrocelli_uuid,
                "series_id": petrocelli_id,
                "season_number": 1,
                "content_url": "https://storage.googleapis.com/pecantv_series/petrocelli/Get_Christie_Love.mp4",
                "poster_url": "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli1_poster.jpg"
            })
            print(f"  - Added Get Christie Love as episode {next_episode}")
            next_episode += 1
        
        # 3. Remove the remaining films from content table
        print(f"\n🗑️  Removing remaining Petrocelli films from content table...")
        
        # Black Brigade film
        result = db.execute(text("""
            DELETE FROM content 
            WHERE title ILIKE '%black brigade%' AND type = 'FILM'
        """))
        print(f"  - Removed Black Brigade film")
        
        # Get Christie Love film
        result = db.execute(text("""
            DELETE FROM content 
            WHERE title ILIKE '%get christie love%' AND type = 'FILM'
        """))
        print(f"  - Removed Get Christie Love film")
        
        # Commit changes
        db.commit()
        print(f"\n✅ Petrocelli episode categorization fixed!")
        
        # Verify the fix
        print(f"\n🔍 Verification:")
        result = db.execute(text("""
            SELECT title, type FROM content 
            WHERE title ILIKE '%petrocelli%' 
               OR title ILIKE '%deadly journey%' 
               OR title ILIKE '%shadow of fear%' 
               OR title ILIKE '%black brigade%' 
               OR title ILIKE '%christie love%'
            ORDER BY title
        """))
        
        remaining_content = result.fetchall()
        print(f"📺 Remaining content entries:")
        for row in remaining_content:
            print(f"  - {row.title} (Type: {row.type})")
        
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