#!/usr/bin/env python3
"""
Script to convert misclassified Petrocelli films into episodes
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import urllib.parse

# Load environment variables
load_dotenv()

def get_database_url():
    """
    Get database URL from environment variables.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("📝 Please ensure .env file contains DATABASE_URL")
        sys.exit(1)
    
    # Handle Neon database URL transformation
    if "neon.tech" in database_url:
        parsed = urllib.parse.urlparse(database_url)
        if "pooler" not in parsed.netloc:
            netloc = parsed.netloc.replace(".neon.tech", "-pooler.neon.tech")
            database_url = urllib.parse.urlunparse((
                parsed.scheme, netloc, parsed.path,
                parsed.params, parsed.query, parsed.fragment
            ))
            print(f"🔄 Using Neon pooled connection: {netloc}")
    
    return database_url

def main():
    print("🔧 Starting Petrocelli episode conversion...")
    
    # Get database connection
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        connect_args={
            "connect_timeout": 10,
            "application_name": "petrocelli_fix_script",
            "sslmode": "require"
        }
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Find films that should be Petrocelli episodes
        print("🔍 Finding misclassified Petrocelli films...")
        
        # Query to find films with Petrocelli content URLs
        query = text("""
            SELECT id, title, content_url, poster_url, description, release_date, 
                   runtime, genre_id, rating_id, created_at, updated_at, uuid
            FROM content 
            WHERE type = 'FILM' 
            AND content_url LIKE '%petrocelli%'
            ORDER BY title
        """)
        
        result = db.execute(query)
        films = result.fetchall()
        
        print(f"📺 Found {len(films)} misclassified Petrocelli films")
        
        if not films:
            print("❌ No misclassified films found")
            return
        
        # Get the Petrocelli series ID
        series_query = text("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'series'")
        series_result = db.execute(series_query)
        series_row = series_result.fetchone()
        
        if not series_row:
            print("❌ Petrocelli series not found in database")
            return
        
        series_id = series_row[0]
        print(f"📺 Petrocelli series ID: {series_id}")
        
        # Get current episode numbers to determine new episode numbers
        episode_query = text("""
            SELECT episode_number 
            FROM episodes 
            WHERE series_id = :series_id 
            ORDER BY episode_number DESC 
            LIMIT 1
        """)
        
        episode_result = db.execute(episode_query, {"series_id": series_id})
        last_episode_row = episode_result.fetchone()
        
        next_episode_number = 14  # Start from episode 14
        if last_episode_row:
            next_episode_number = last_episode_row[0] + 1
            print(f"📺 Next episode number will be: {next_episode_number}")
        
        # Convert each film to an episode
        converted_count = 0
        for film in films:
            film_id, title, content_url, poster_url, description, release_date, \
            runtime, genre_id, rating_id, created_at, updated_at, content_uuid = film
            
            print(f"🔄 Converting film '{title}' to episode {next_episode_number}")
            
            # Generate new UUID for the episode
            episode_uuid = str(uuid.uuid4())
            
            # Insert new episode
            insert_query = text("""
                INSERT INTO episodes (
                    uuid, series_id, episode_number, title, description, 
                    content_url, poster_url, runtime, genre_id, rating_id, 
                    release_date, content_uuid, created_at, updated_at
                ) VALUES (
                    :uuid, :series_id, :episode_number, :title, :description,
                    :content_url, :poster_url, :runtime, :genre_id, :rating_id,
                    :release_date, :content_uuid, :created_at, :updated_at
                )
            """)
            
            db.execute(insert_query, {
                "uuid": episode_uuid,
                "series_id": series_id,
                "episode_number": next_episode_number,
                "title": title,
                "description": description,
                "content_url": content_url,
                "poster_url": poster_url,
                "runtime": runtime,
                "genre_id": genre_id,
                "rating_id": rating_id,
                "release_date": release_date,
                "content_uuid": content_uuid,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Delete the original film
            delete_query = text("DELETE FROM content WHERE id = :film_id")
            db.execute(delete_query, {"film_id": film_id})
            
            print(f"✅ Converted '{title}' to episode {next_episode_number}")
            next_episode_number += 1
            converted_count += 1
        
        # Commit all changes
        db.commit()
        print(f"🎉 Successfully converted {converted_count} films to episodes")
        
        # Verify the changes
        verify_query = text("""
            SELECT episode_number, title 
            FROM episodes 
            WHERE series_id = :series_id 
            ORDER BY episode_number
        """)
        
        verify_result = db.execute(verify_query, {"series_id": series_id})
        episodes = verify_result.fetchall()
        
        print(f"📊 Petrocelli now has {len(episodes)} episodes:")
        for episode_number, title in episodes:
            print(f"   Episode {episode_number}: {title}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 