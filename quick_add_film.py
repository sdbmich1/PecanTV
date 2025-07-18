#!/usr/bin/env python3
"""
Quick script to add a film via command line arguments
Usage: python quick_add_film.py "Title" "Description" "poster_url" "content_url" [genre] [release_date]
"""

import os
import sys
import uuid
from datetime import datetime

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

try:
    from api.database import get_db_session
    from api.models import Content, Genre
except ImportError as e:
    print(f"❌ Error importing database modules: {e}")
    sys.exit(1)

def quick_add_film(title, description, poster_url, content_url, genre="Drama", release_date=None):
    """Quick add a film with minimal parameters"""
    
    try:
        session = get_db_session()
        
        # Check if film already exists
        existing = session.query(Content).filter(
            Content.title == title,
            Content.type == "FILM"
        ).first()
        
        if existing:
            print(f"⚠️  Film '{title}' already exists")
            return False
        
        # Get genre
        genre_obj = session.query(Genre).filter(Genre.name == genre).first()
        if not genre_obj:
            print(f"⚠️  Genre '{genre}' not found, using 'Drama'")
            genre_obj = session.query(Genre).filter(Genre.name == "Drama").first()
        
        # Create film
        new_film = Content(
            uuid=str(uuid.uuid4()),
            title=title,
            description=description,
            posterURL=poster_url,
            contentURL=content_url,
            type="FILM",  # Changed from "SERIES" to "FILM"
            genreId=genre_obj.id,
            ratingId=1,
            releaseDate=release_date,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )
        
        session.add(new_film)
        session.commit()
        
        print(f"✅ Added film: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python quick_add_film.py \"Title\" \"Description\" \"poster_url\" \"content_url\" [genre] [release_date]")
        print("Example: python quick_add_film.py \"My Film\" \"A great film\" \"https://example.com/poster.jpg\" \"https://example.com/video.mp4\" \"Action\" \"2024-01-01\"")
        sys.exit(1)
    
    title = sys.argv[1]
    description = sys.argv[2]
    poster_url = sys.argv[3]
    content_url = sys.argv[4]
    genre = sys.argv[5] if len(sys.argv) > 5 else "Drama"
    release_date = sys.argv[6] if len(sys.argv) > 6 else None
    
    success = quick_add_film(title, description, poster_url, content_url, genre, release_date)
    sys.exit(0 if success else 1) 