#!/usr/bin/env python3
"""
Example script demonstrating how to post new content and episodes to the PecanTV API
"""

import requests
import json
from datetime import date
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your API URL
API_ENDPOINTS = {
    "content": f"{API_BASE_URL}/content",
    "episodes": f"{API_BASE_URL}/episodes",
    "genres": f"{API_BASE_URL}/genres",
    "ratings": f"{API_BASE_URL}/ratings"
}

def get_available_genres() -> Dict[int, str]:
    """Get available genres from the API"""
    try:
        response = requests.get(API_ENDPOINTS["genres"])
        response.raise_for_status()
        genres = response.json()
        return {genre["id"]: genre["name"] for genre in genres}
    except Exception as e:
        print(f"Error fetching genres: {e}")
        return {}

def get_available_ratings() -> Dict[int, str]:
    """Get available ratings from the API"""
    try:
        response = requests.get(API_ENDPOINTS["ratings"])
        response.raise_for_status()
        ratings = response.json()
        return {rating["id"]: rating["code"] for rating in ratings}
    except Exception as e:
        print(f"Error fetching ratings: {e}")
        return {}

def create_new_film() -> Dict[str, Any]:
    """Example: Create a new film"""
    print("🎬 Creating a new film...")
    
    # Get available genres and ratings
    genres = get_available_genres()
    ratings = get_available_ratings()
    
    # Example film data
    film_data = {
        "title": "Example Film Title",
        "posterURL": "https://storage.googleapis.com/pecantv_title_images/example-poster.jpg",
        "trailerURL": "https://storage.googleapis.com/pecantv_trailers/example-trailer.mp4",
        "contentURL": "https://storage.googleapis.com/pecantv_features/example-film.mp4",
        "description": "This is an example film description.",
        "type": "FILM",  # or "SERIES"
        "runtime": 120,  # in minutes
        "genreId": list(genres.keys())[0] if genres else None,  # Use first available genre
        "ratingId": list(ratings.keys())[0] if ratings else None,  # Use first available rating
        "releaseDate": "2024-01-01"  # YYYY-MM-DD format
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS["content"],
            json=film_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        created_film = response.json()
        print(f"✅ Film created successfully!")
        print(f"   ID: {created_film['id']}")
        print(f"   Title: {created_film['title']}")
        print(f"   UUID: {created_film['uuid']}")
        return created_film
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating film: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return {}

def create_new_series() -> Dict[str, Any]:
    """Example: Create a new series"""
    print("📺 Creating a new series...")
    
    # Get available genres and ratings
    genres = get_available_genres()
    ratings = get_available_ratings()
    
    # Example series data
    series_data = {
        "title": "Example Series Title",
        "posterURL": "https://storage.googleapis.com/pecantv_title_images/example-series-poster.jpg",
        "trailerURL": "https://storage.googleapis.com/pecantv_trailers/example-series-trailer.mp4",
        "contentURL": None,  # Series don't have direct content URLs
        "description": "This is an example series description.",
        "type": "SERIES",
        "runtime": 60,  # Average episode runtime in minutes
        "genreId": list(genres.keys())[0] if genres else None,
        "ratingId": list(ratings.keys())[0] if ratings else None,
        "releaseDate": "2024-01-01"
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS["content"],
            json=series_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        created_series = response.json()
        print(f"✅ Series created successfully!")
        print(f"   ID: {created_series['id']}")
        print(f"   Title: {created_series['title']}")
        print(f"   UUID: {created_series['uuid']}")
        return created_series
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating series: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return {}

def create_new_episode(series_id: int, series_uuid: str) -> Dict[str, Any]:
    """Example: Create a new episode for a series"""
    print(f"🎬 Creating a new episode for series ID {series_id}...")
    
    # Example episode data
    episode_data = {
        "title": "Example Episode Title",
        "description": "This is an example episode description.",
        "seasonNumber": 1,
        "episodeNumber": 1,
        "runtime": 45,  # in minutes
        "contentURL": "https://storage.googleapis.com/pecantv_series/example_series/Episode1.mp4",
        "posterURL": "https://storage.googleapis.com/pecantv_title_images/example-episode-poster.jpg",
        "thumbnailURL": "https://storage.googleapis.com/pecantv_title_images/example-episode-thumbnail.jpg",
        "airDate": "2024-01-01",  # YYYY-MM-DD format
        "seriesId": series_id,
        "contentUuid": series_uuid
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS["episodes"],
            json=episode_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        created_episode = response.json()
        print(f"✅ Episode created successfully!")
        print(f"   ID: {created_episode['id']}")
        print(f"   Title: {created_episode['title']}")
        print(f"   Season {created_episode['seasonNumber']}, Episode {created_episode['episodeNumber']}")
        print(f"   UUID: {created_episode['uuid']}")
        return created_episode
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating episode: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return {}

def main():
    """Main function to demonstrate API usage"""
    print("🚀 PecanTV API Content Creation Examples")
    print("=" * 50)
    
    # Show available genres and ratings
    print("\n📋 Available Genres:")
    genres = get_available_genres()
    for genre_id, genre_name in genres.items():
        print(f"   {genre_id}: {genre_name}")
    
    print("\n📋 Available Ratings:")
    ratings = get_available_ratings()
    for rating_id, rating_code in ratings.items():
        print(f"   {rating_id}: {rating_code}")
    
    # Create a new film
    print("\n" + "=" * 50)
    film = create_new_film()
    
    # Create a new series
    print("\n" + "=" * 50)
    series = create_new_series()
    
    # Create an episode for the series
    if series and "id" in series and "uuid" in series:
        print("\n" + "=" * 50)
        episode = create_new_episode(series["id"], series["uuid"])
    
    print("\n✅ API examples completed!")

if __name__ == "__main__":
    main() 