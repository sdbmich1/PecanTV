#!/usr/bin/env python3
"""
Script to update Mike Hammer episodes with correct titles and content URLs
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
        print("🔧 Updating Mike Hammer episodes...")
        
        # Get Mike Hammer series info
        result = db.execute(text("""
            SELECT id, uuid FROM content 
            WHERE title = 'Mike Hammer' AND type = 'SERIES'
        """))
        
        series = result.fetchone()
        if not series:
            print("❌ Mike Hammer series not found!")
            return
        
        mike_hammer_id = series.id
        mike_hammer_uuid = series.uuid
        print(f"✅ Found Mike Hammer series - ID: {mike_hammer_id}, UUID: {mike_hammer_uuid}")
        
        # Mike Hammer episodes with correct titles and URLs
        episodes_data = [
            {
                "title": "Music To Die By",
                "episode_number": 1,
                "content_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-Music-To-Die-By_with-credits.mp4",
                "poster_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-Music-To-Die-By_poster.jpg"
            },
            {
                "title": "The New York Rock",
                "episode_number": 2,
                "content_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-The-New-York-Rock_with-credits.mp4",
                "poster_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-The-New-York-Rock_poster.jpg"
            },
            {
                "title": "Shots in the Dark",
                "episode_number": 3,
                "content_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-Shots-in-the-Dark_with-credits.mp4",
                "poster_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-Shots-in-the-Dark_poster.jpg"
            },
            {
                "title": "The Girl in the Red Bikini",
                "episode_number": 4,
                "content_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-The-Girl-in-the-Red-Bikini_with-credits.mp4",
                "poster_url": "https://storage.googleapis.com/pecantv_series/mike_hammer/MH-The-Girl-in-the-Red-Bikini_poster.jpg"
            }
        ]
        
        # Update each episode
        for episode_data in episodes_data:
            print(f"\n🔄 Updating Episode {episode_data['episode_number']}: {episode_data['title']}")
            
            # Update the episode
            result = db.execute(text("""
                UPDATE episodes 
                SET title = :title, content_url = :content_url, poster_url = :poster_url
                WHERE content_uuid = :content_uuid AND episode_number = :episode_number
            """), {
                "title": episode_data["title"],
                "content_url": episode_data["content_url"],
                "poster_url": episode_data["poster_url"],
                "content_uuid": mike_hammer_uuid,
                "episode_number": episode_data["episode_number"]
            })
            
            if result.rowcount > 0:
                print(f"  ✅ Updated: {episode_data['title']}")
            else:
                print(f"  ❌ Failed to update: {episode_data['title']}")
        
        # Commit changes
        db.commit()
        print(f"\n✅ Successfully updated {len(episodes_data)} Mike Hammer episodes!")

if __name__ == "__main__":
    main() 