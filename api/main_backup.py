from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

from database import get_db
import models
import schemas
import crud
from subscription_routes import router as subscription_router
from auth_service import AuthService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PecanTV API",
    description="API for PecanTV streaming service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include subscription routes
app.include_router(subscription_router, prefix="/subscriptions", tags=["subscriptions"])

# Mount static files for media serving
# Get the path to the pecantv_series directory relative to the API directory
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pecantv_series")
if os.path.exists(static_path):
    app.mount("/pecantv_series", StaticFiles(directory=static_path), name="pecantv_series")
    print(f"✅ Static files mounted at /pecantv_series from {static_path}")
else:
    print(f"⚠️  Static files directory not found: {static_path}")

@app.get("/")
async def root():
    return {"message": "Welcome to PecanTV API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Enhanced Authentication endpoints with Stripe integration
@app.post("/auth/register", response_model=schemas.AuthResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with Stripe customer creation and subscription status"""
    return AuthService.register_user(db, user)

@app.post("/auth/login", response_model=schemas.AuthResponse)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user with subscription status check"""
    return AuthService.login_user(db, user_credentials)

@app.get("/auth/me", response_model=schemas.UserWithSubscription)
def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user with subscription status"""
    user = AuthService.get_current_user(db, token)
    
    # Get subscription status
    subscription_status = AuthService.get_user_subscription_status(db, user.id)
    
    # Create user with subscription info
    user_with_subscription = schemas.UserWithSubscription(
        id=user.id,
        uuid=user.uuid,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        stripe_customer_id=user.stripe_customer_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        **subscription_status
    )
    
    return user_with_subscription

# Favorites endpoints
@app.get("/favorites/{user_id}")
def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    """Get all favorites for a user"""
    favorites = crud.get_user_favorites(db, user_id=user_id)
    
    # Manually serialize to ensure genre is a string and ageRating is present
    serialized_favorites = []
    for fav in favorites:
        genre_name = fav.genre.name if fav.genre else None
        rating_code = fav.rating.code if fav.rating else None
        age_rating = str(fav.rating.min_age) if fav.rating and fav.rating.min_age is not None else ""
        serialized_fav = {
            "id": fav.id,
            "uuid": str(fav.uuid),
            "title": fav.title,
            "posterURL": fav.poster_url,
            "trailerURL": fav.trailer_url,
            "contentURL": fav.content_url,
            "description": fav.description,
            "type": fav.type.value,
            "runtime": fav.runtime,
            "genreId": fav.genre_id,
            "ratingId": fav.rating_id,
            "releaseDate": fav.release_date.isoformat() if fav.release_date else None,
            "createdAt": fav.created_at.isoformat(),
            "updatedAt": fav.updated_at.isoformat(),
            "genre": genre_name,
            "rating": rating_code,
            "ageRating": age_rating
        }
        serialized_favorites.append(serialized_fav)
    
    return {
        "favorites": serialized_favorites,
        "total_count": len(favorites)
    }

@app.post("/favorites/{user_id}/toggle/{content_id}")
def toggle_favorite(user_id: int, content_id: int, db: Session = Depends(get_db)):
    """Toggle favorite status for a content item"""
    result = crud.toggle_user_favorite(db, user_id=user_id, content_id=content_id)
    return {
        "success": True,
        "message": f"Favorite {'added' if result['is_favorited'] else 'removed'} successfully",
        "is_favorited": result['is_favorited']
    }

@app.get("/content", response_model=List[schemas.Content])
def get_content(
    skip: int = 0,
    limit: int = 100,
    type: str = None,
    genre: str = None,
    db: Session = Depends(get_db)
):
    """Get all content with optional filtering"""
    return crud.get_content(db, skip=skip, limit=limit, type=type, genre=genre)

@app.get("/content/{content_id}", response_model=schemas.Content)
def get_content_by_id(content_id: int, db: Session = Depends(get_db)):
    """Get specific content by ID"""
    content = crud.get_content_by_id(db, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@app.get("/content/{content_id}/episodes")
def get_content_episodes(
    content_id: int,
    season_number: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get episodes for a specific content item"""
    # Verify content exists
    content = crud.get_content_by_id(db, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    
    episodes = crud.get_episodes(db, skip=skip, limit=limit, content_id=content_id, season_number=season_number)
    return process_episodes_with_fallbacks(episodes, content.title)

@app.get("/episodes")
def get_episodes(
    skip: int = 0,
    limit: int = 100,
    content_id: int = None,
    season_number: int = None,
    db: Session = Depends(get_db)
):
    """Get all episodes with optional filtering"""
    episodes = crud.get_episodes(db, skip=skip, limit=limit, content_id=content_id, season_number=season_number)
    return process_episodes_with_fallbacks(episodes)

@app.get("/episodes/{episode_id}", response_model=schemas.Episode)
def get_episode_by_id(episode_id: int, db: Session = Depends(get_db)):
    """Get specific episode by ID"""
    episode = crud.get_episode_by_id(db, episode_id)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode

@app.get("/series", response_model=List[schemas.Content])
def get_series_content(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all series content (content with episodes)"""
    return crud.get_series_content(db, skip=skip, limit=limit)

@app.get("/series/{series_id}/episodes")
def get_series_episodes(
    series_id: int,
    season_number: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get episodes for a specific series"""
    # Verify series exists
    series = crud.get_content_by_id(db, series_id)
    if series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    
    if series.type != models.ContentType.SERIES:
        raise HTTPException(status_code=400, detail="Content is not a series")
    
    episodes = crud.get_episodes(db, skip=skip, limit=limit, content_id=series_id, season_number=season_number)
    return process_episodes_with_fallbacks(episodes, series.title)

@app.get("/genres", response_model=List[schemas.Genre])
def get_genres(db: Session = Depends(get_db)):
    """Get all genres"""
    return crud.get_genres(db)

@app.get("/ratings", response_model=List[schemas.Rating])
def get_ratings(db: Session = Depends(get_db)):
    """Get all ratings"""
    return crud.get_ratings(db)

@app.get("/search", response_model=List[schemas.Content])
def search_content(
    q: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search content by title or description"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    return crud.search_content(db, query=q.strip(), skip=skip, limit=limit)

def get_fallback_poster_url(episode_title: str, series_title: str = None) -> str:
    """Provide fallback poster URLs for episodes that don't have poster URLs"""
    # Default fallback poster URL
    default_poster = "https://storage.googleapis.com/pecantv_title_images/default-episode-poster.png"
    
    # If no episode title, return default
    if not episode_title:
        return default_poster
    
    # Try to get a series-specific poster if series title is provided
    if series_title:
        series_lower = series_title.lower().replace(" ", "_")
        if "commando_cody" in series_lower or "sky_marshal" in series_lower:
            return "https://storage.googleapis.com/pecantv_title_images/Commando-Cody-Sky-Marshal-of-the-Universe.png"
        elif "petrocelli" in series_lower:
            return "https://storage.googleapis.com/pecantv_title_images/Petrocelli.png"
        elif "dragnet" in series_lower:
            return "https://storage.googleapis.com/pecantv_title_images/Dragnet.png"
        elif "longstreet" in series_lower:
            return "https://storage.googleapis.com/pecantv_title_images/Longstreet.png"
    
    return default_poster

def process_episodes_with_fallbacks(episodes: List[models.Episode], series_title: str = None) -> List[dict]:
    """Process episodes and add fallback poster URLs where needed"""
    processed_episodes = []
    for episode in episodes:
        episode_dict = {
            "id": episode.id,
            "uuid": str(episode.uuid),
            "title": episode.title,
            "description": episode.description or "",
            "seasonNumber": episode.season_number,
            "episodeNumber": episode.episode_number,
            "runtime": episode.runtime or 0,
            "contentURL": episode.content_url or "",
            "posterURL": episode.poster_url or get_fallback_poster_url(episode.title, series_title),
            "airDate": episode.air_date.isoformat() if episode.air_date else None,
            "seriesId": episode.series_id,
            "contentUuid": str(episode.content_uuid),
            "createdAt": episode.created_at.isoformat(),
            "updatedAt": episode.updated_at.isoformat()
        }
        processed_episodes.append(episode_dict)
    return processed_episodes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 