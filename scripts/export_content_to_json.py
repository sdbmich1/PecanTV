#!/usr/bin/env python3
"""
Script to export all content data from Neon database as JSON
Usage: python3 scripts/export_content_to_json.py
"""

import os
import sys
import json
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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
        if parsed.scheme == "postgresql":
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
    
    return database_url

def export_content_to_json():
    """
    Export all content data from database to JSON format
    """
    print("🎬 Exporting PecanTV content data to JSON...")
    
    # Get database connection
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create session
        db = SessionLocal()
        
        # Get all content
        print("📊 Fetching content data...")
        content_result = db.execute(text("""
            SELECT 
                c.id,
                c.uuid,
                c.title,
                c.description,
                c.poster_url,
                c.trailer_url,
                c.content_url,
                c.type,
                c.runtime,
                c.genre_id,
                c.rating_id,
                c.created_at,
                c.updated_at,
                g.name as genre_name,
                r.name as rating_name
            FROM content c
            LEFT JOIN genres g ON c.genre_id = g.id
            LEFT JOIN ratings r ON c.rating_id = r.id
            ORDER BY c.id
        """))
        
        content_data = []
        for row in content_result:
            content_item = {
                "id": row.id,
                "uuid": str(row.uuid) if row.uuid else None,
                "title": row.title,
                "description": row.description,
                "posterURL": row.poster_url,
                "trailerURL": row.trailer_url,
                "contentURL": row.content_url,
                "type": row.type,
                "runtime": row.runtime,
                "genreId": row.genre_id,
                "ratingId": row.rating_id,
                "genre": row.genre_name,
                "rating": row.rating_name,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
                "updatedAt": row.updated_at.isoformat() if row.updated_at else None
            }
            content_data.append(content_item)
        
        # Get all episodes
        print("📺 Fetching episode data...")
        episodes_result = db.execute(text("""
            SELECT 
                e.id,
                e.uuid,
                e.title,
                e.description,
                e.poster_url,
                e.trailer_url,
                e.content_url,
                e.content_id,
                e.season_number,
                e.episode_number,
                e.runtime,
                e.created_at,
                e.updated_at,
                c.title as content_title
            FROM episodes e
            LEFT JOIN content c ON e.content_id = c.id
            ORDER BY e.content_id, e.season_number, e.episode_number
        """))
        
        episodes_data = []
        for row in episodes_result:
            episode_item = {
                "id": row.id,
                "uuid": str(row.uuid) if row.uuid else None,
                "title": row.title,
                "description": row.description,
                "posterURL": row.poster_url,
                "trailerURL": row.trailer_url,
                "contentURL": row.content_url,
                "contentId": row.content_id,
                "contentTitle": row.content_title,
                "seasonNumber": row.season_number,
                "episodeNumber": row.episode_number,
                "runtime": row.runtime,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
                "updatedAt": row.updated_at.isoformat() if row.updated_at else None
            }
            episodes_data.append(episode_item)
        
        # Get all series (content with episodes)
        print("📋 Fetching series data...")
        series_result = db.execute(text("""
            SELECT DISTINCT
                c.id,
                c.title,
                c.description,
                c.poster_url,
                c.trailer_url,
                c.content_url,
                c.type,
                c.runtime,
                c.genre_id,
                c.rating_id,
                g.name as genre_name,
                r.name as rating_name,
                COUNT(e.id) as episode_count
            FROM content c
            LEFT JOIN genres g ON c.genre_id = g.id
            LEFT JOIN ratings r ON c.rating_id = r.id
            LEFT JOIN episodes e ON c.id = e.content_id
            WHERE c.type = 'SERIES'
            GROUP BY c.id, c.title, c.description, c.poster_url, c.trailer_url, 
                     c.content_url, c.type, c.runtime, c.genre_id, c.rating_id, 
                     g.name, r.name
            ORDER BY c.title
        """))
        
        series_data = []
        for row in series_result:
            series_item = {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "posterURL": row.poster_url,
                "trailerURL": row.trailer_url,
                "contentURL": row.content_url,
                "type": row.type,
                "runtime": row.runtime,
                "genreId": row.genre_id,
                "ratingId": row.rating_id,
                "genre": row.genre_name,
                "rating": row.rating_name,
                "episodeCount": row.episode_count
            }
            series_data.append(series_item)
        
        # Get all films (content without episodes)
        print("🎬 Fetching film data...")
        films_result = db.execute(text("""
            SELECT 
                c.id,
                c.title,
                c.description,
                c.poster_url,
                c.trailer_url,
                c.content_url,
                c.type,
                c.runtime,
                c.genre_id,
                c.rating_id,
                g.name as genre_name,
                r.name as rating_name
            FROM content c
            LEFT JOIN genres g ON c.genre_id = g.id
            LEFT JOIN ratings r ON c.rating_id = r.id
            WHERE c.type = 'FILM'
            ORDER BY c.title
        """))
        
        films_data = []
        for row in films_result:
            film_item = {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "posterURL": row.poster_url,
                "trailerURL": row.trailer_url,
                "contentURL": row.content_url,
                "type": row.type,
                "runtime": row.runtime,
                "genreId": row.genre_id,
                "ratingId": row.rating_id,
                "genre": row.genre_name,
                "rating": row.rating_name
            }
            films_data.append(film_item)
        
        # Get genres
        print("🏷️ Fetching genre data...")
        genres_result = db.execute(text("SELECT * FROM genres ORDER BY name"))
        genres_data = [{"id": row.id, "name": row.name, "description": row.description} for row in genres_result]
        
        # Get ratings
        print("⭐ Fetching rating data...")
        ratings_result = db.execute(text("SELECT * FROM ratings ORDER BY name"))
        ratings_data = [{"id": row.id, "name": row.name, "description": row.description} for row in ratings_result]
        
        # Create comprehensive JSON structure
        export_data = {
            "exportInfo": {
                "timestamp": datetime.now().isoformat(),
                "totalContent": len(content_data),
                "totalEpisodes": len(episodes_data),
                "totalSeries": len(series_data),
                "totalFilms": len(films_data),
                "totalGenres": len(genres_data),
                "totalRatings": len(ratings_data)
            },
            "content": content_data,
            "episodes": episodes_data,
            "series": series_data,
            "films": films_data,
            "genres": genres_data,
            "ratings": ratings_data
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_exports/pecantv_content_{timestamp}.json"
        
        # Create directory if it doesn't exist
        os.makedirs("database_exports", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Content exported to: {filename}")
        print(f"📊 Summary:")
        print(f"   - Content: {len(content_data)} items")
        print(f"   - Episodes: {len(episodes_data)} items")
        print(f"   - Series: {len(series_data)} items")
        print(f"   - Films: {len(films_data)} items")
        print(f"   - Genres: {len(genres_data)} items")
        print(f"   - Ratings: {len(ratings_data)} items")
        
        # Also print a sample of content
        print(f"\n📋 Sample Content (first 3 items):")
        for i, item in enumerate(content_data[:3]):
            print(f"   {i+1}. {item['title']} ({item['type']}) - {item['genre']}")
            print(f"      Poster: {item['posterURL']}")
            print(f"      Trailer: {item['trailerURL']}")
            print()
        
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    export_content_to_json() 