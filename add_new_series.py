#!/usr/bin/env python3
"""
Script to add new series data to the database
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Add the api directory to the path to import database modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

try:
    from api.database import get_db_session
    from api.models import Content, Genre
except ImportError as e:
    print(f"❌ Error importing database modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def add_new_series(
    title: str,
    description: str,
    poster_url: str,
    content_url: str,
    trailer_url: Optional[str] = None,
    genre_name: str = "Drama",
    release_date: Optional[str] = None,
    runtime: Optional[int] = None
) -> bool:
    """
    Add a new series to the database
    
    Args:
        title: Series title
        description: Series description
        poster_url: URL to the poster image
        content_url: URL to the video content
        trailer_url: Optional trailer URL
        genre_name: Genre name (will be looked up or created)
        release_date: Optional release date (YYYY-MM-DD format)
        runtime: Optional runtime in minutes
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        session = get_db_session()
        
        # Check if series already exists
        existing = session.query(Content).filter(
            Content.title == title,
            Content.type == "SERIES"
        ).first()
        
        if existing:
            print(f"⚠️  Series '{title}' already exists in database")
            return False
        
        # Get or create genre
        genre = session.query(Genre).filter(Genre.name == genre_name).first()
        if not genre:
            print(f"⚠️  Genre '{genre_name}' not found, using 'Drama' as default")
            genre = session.query(Genre).filter(Genre.name == "Drama").first()
            if not genre:
                print("❌ Default genre 'Drama' not found in database")
                return False
        
        # Create new series
        new_series = Content(
            uuid=str(uuid.uuid4()),
            title=title,
            description=description,
            posterURL=poster_url,
            contentURL=content_url,
            trailerURL=trailer_url,
            type="SERIES",
            genreId=genre.id,
            ratingId=1,  # Default rating
            releaseDate=release_date,
            runtime=runtime,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )
        
        session.add(new_series)
        session.commit()
        
        print(f"✅ Successfully added series: {title}")
        print(f"   📷 Poster: {poster_url}")
        print(f"   🎭 Genre: {genre.name}")
        print(f"   🆔 UUID: {new_series.uuid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding series: {e}")
        if 'session' in locals():
            session.rollback()
        return False
    finally:
        if 'session' in locals():
            session.close()

def add_sample_series():
    """Add a sample series to demonstrate the functionality"""
    
    sample_series = {
        "title": "The Adventures of Sherlock Holmes",
        "description": "A classic detective series following the brilliant detective Sherlock Holmes and his loyal friend Dr. Watson as they solve mysterious cases in Victorian London.",
        "poster_url": "https://storage.googleapis.com/pecantv_title_images/sherlock-holmes-series.png",
        "content_url": "https://storage.googleapis.com/pecantv_series/sherlock-holmes-episode-1.mp4",
        "trailer_url": "https://storage.googleapis.com/pecantv_trailers/sherlock-holmes-trailer.mp4",
        "genre_name": "Mystery",
        "release_date": "1984-04-24",
        "runtime": 50
    }
    
    print("🎬 Adding sample series to database...")
    success = add_new_series(**sample_series)
    
    if success:
        print("\n✅ Sample series added successfully!")
        print("You can now use this script to add your own series.")
    else:
        print("\n❌ Failed to add sample series.")

def main():
    """Main function with interactive menu"""
    
    print("🎬 PECAN TV - ADD NEW SERIES")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == "--sample":
            add_sample_series()
        else:
            print("Usage: python add_new_series.py [--sample]")
            print("  --sample: Add a sample series to the database")
    else:
        # Interactive mode
        print("Choose an option:")
        print("1. Add sample series")
        print("2. Add custom series")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            add_sample_series()
        elif choice == "2":
            print("\n📝 Enter series details:")
            title = input("Title: ").strip()
            description = input("Description: ").strip()
            poster_url = input("Poster URL: ").strip()
            content_url = input("Content URL: ").strip()
            trailer_url = input("Trailer URL (optional): ").strip() or None
            genre_name = input("Genre (default: Drama): ").strip() or "Drama"
            release_date = input("Release Date YYYY-MM-DD (optional): ").strip() or None
            runtime_str = input("Runtime in minutes (optional): ").strip()
            runtime = int(runtime_str) if runtime_str.isdigit() else None
            
            success = add_new_series(
                title=title,
                description=description,
                poster_url=poster_url,
                content_url=content_url,
                trailer_url=trailer_url,
                genre_name=genre_name,
                release_date=release_date,
                runtime=runtime
            )
            
            if success:
                print("\n✅ Series added successfully!")
            else:
                print("\n❌ Failed to add series.")
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main() 