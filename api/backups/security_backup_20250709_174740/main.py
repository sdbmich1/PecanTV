from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse
import requests
import io
import urllib.parse
import logging

from database import get_db
import models
import schemas
import crud
from subscription_routes import router as subscription_router
from auth_service import AuthService
from security_middleware import security_middleware

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PecanTV API",
    description="API for PecanTV streaming service",
    version="1.0.0"
)

# Add security middleware
app.middleware("http")(security_middleware)

# Configure CORS with more restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative dev port
        "https://pecantv.com",    # Production domain (replace with actual domain)
        "https://www.pecantv.com" # Production domain with www
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Minute-Remaining", "X-RateLimit-Hour-Remaining"]
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

@app.get("/security/stats")
def get_security_stats():
    """Get security statistics and monitoring data"""
    return security_middleware.get_security_stats()

# @app.get("/security/test")
# def test_security():
#     """Test security endpoint"""
#     return {"message": "Security test endpoint working"}

# @app.get("/test-security")
# def test_security_alt():
#     """Test security endpoint with different path"""
#     return {"message": "Security test endpoint working (alt path)"}

@app.get("/test-cdn")
def test_cdn():
    return {"message": "CDN test endpoint working"}

# CDN-style image optimization endpoint
@app.get("/cdn-cgi/image/{params:path}")
@app.head("/cdn-cgi/image/{params:path}")
async def cdn_image_optimization(params: str, url: str = None, request: Request = None):
    """
    CDN-style image optimization endpoint
    Format: /cdn-cgi/image/format=webp,width=300,quality=85/?url=<original_url>
    Works for both local and production URLs.
    """
    try:
        # Parse optimization parameters
        param_parts = params.split(',')
        optimization_params = {}
        for part in param_parts:
            if '=' in part:
                key, value = part.split('=', 1)
                optimization_params[key] = value

        # Extract original URL from query parameter
        if not url:
            raise HTTPException(status_code=400, detail="URL parameter required")
        
        # Decode URL if percent-encoded
        url = urllib.parse.unquote(url)
        print(f"🔍 CDN endpoint requested for url: {url}")

        # Handle remote URLs (GCS, Cloudflare, Dropbox, etc)
        # Skip localhost URLs as they should be handled as local files
        if (url.startswith('http://') or url.startswith('https://')) and not url.startswith('http://localhost:') and not url.startswith('http://127.0.0.1:'):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return FileResponse(
                        io.BytesIO(response.content),
                        media_type=response.headers.get('content-type', 'image/jpeg'),
                        headers={
                            'Cache-Control': 'public, max-age=86400',  # 24 hours
                            'CDN-Optimized': 'true'
                        }
                    )
                else:
                    print(f"❌ Failed to fetch remote image: {url} (status {response.status_code})")
            except Exception as e:
                print(f"❌ Error fetching remote image: {url} ({e})")
                raise HTTPException(status_code=502, detail=f"Failed to fetch remote image: {e}")

        # Handle local URLs (relative to /pecantv_series)
        # Accepts both /pecantv_series/... and pecantv_series/...
        local_url = url
        if local_url.startswith("/pecantv_series/"):
            local_url = local_url[len("/pecantv_series/"):]
        elif local_url.startswith("pecantv_series/"):
            local_url = local_url[len("pecantv_series/"):]
        elif local_url.startswith("http://localhost:8000/pecantv_series/"):
            local_url = local_url[len("http://localhost:8000/pecantv_series/"):]
        elif local_url.startswith("http://127.0.0.1:8000/pecantv_series/"):
            local_url = local_url[len("http://127.0.0.1:8000/pecantv_series/"):]
        elif local_url.startswith("http://localhost:8001/pecantv_series/"):
            local_url = local_url[len("http://localhost:8001/pecantv_series/"):]
        elif local_url.startswith("http://127.0.0.1:8001/pecantv_series/"):
            local_url = local_url[len("http://127.0.0.1:8001/pecantv_series/"):]
        
        # Remove any leading slashes
        local_url = local_url.lstrip('/')
        local_path = os.path.join(static_path, local_url)
        print(f"🔍 Resolved local_path: {local_path}")
        print(f"🔍 Static path: {static_path}")
        print(f"🔍 File exists: {os.path.exists(local_path)}")
        
        if os.path.exists(local_path):
            # For HEAD requests, return headers only
            if request and request.method == "HEAD":
                return FileResponse(
                    local_path,
                    headers={
                        'Cache-Control': 'public, max-age=86400',  # 24 hours
                        'CDN-Optimized': 'true'
                    }
                )
            # For GET requests, return the full file
            return FileResponse(
                local_path,
                headers={
                    'Cache-Control': 'public, max-age=86400',  # 24 hours
                    'CDN-Optimized': 'true'
                }
            )

        # Not found
        print(f"❌ Image not found: {url} (resolved local path: {local_path})")
        raise HTTPException(status_code=404, detail="Image not found")

    except Exception as e:
        print(f"❌ Image optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Image optimization error: {str(e)}")

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
def get_user_favorites(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all favorites for a user"""
    # Authorization check
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only view your own favorites"
        )
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
    limit: int = 500,  # Increased from 100 to 500 to include all content
    type: str = None,
    genre: str = None,
    db: Session = Depends(get_db)
):
    """Get all content with optional filtering"""
    # Patch: serialize with by_alias=True to ensure posterURL is returned
    content_items = crud.get_content(db, skip=skip, limit=limit, type=type, genre=genre)
    return [schemas.Content.from_orm(item).dict(by_alias=True) for item in content_items]

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

@app.put("/content/{content_id}", response_model=schemas.Content)
def update_content(content_id: int, content_update: schemas.ContentUpdate, db: Session = Depends(get_db)):
    """Update specific content by ID"""
    updated_content = crud.update_content(db, content_id, content_update)
    if updated_content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return updated_content

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
    
    # Get series poster URL if we have episodes
    series_poster_url = None
    if episodes:
        # Get the series poster URL from the first episode's series
        from crud import get_content_by_id
        from database import get_db
        db = next(get_db())
        try:
            series = get_content_by_id(db, episodes[0].series_id)
            if series:
                series_poster_url = series.poster_url
        except:
            pass
        finally:
            db.close()
    
    for episode in episodes:
        # Determine which poster URL to use (priority order):
        # 1. Episode's own poster_url
        # 2. Episode's thumbnail_url  
        # 3. Series poster_url
        # 4. Fallback based on series title
        poster_url = episode.poster_url
        if not poster_url:
            poster_url = episode.thumbnail_url
        if not poster_url and series_poster_url:
            poster_url = series_poster_url
        if not poster_url:
            poster_url = get_fallback_poster_url(episode.title, series_title)
        
        episode_dict = {
            "id": episode.id,
            "uuid": str(episode.uuid),
            "title": episode.title,
            "description": episode.description or "",
            "seasonNumber": episode.season_number,
            "episodeNumber": episode.episode_number,
            "runtime": episode.runtime or 0,
            "contentURL": episode.content_url or "",
            "posterURL": poster_url,
            "airDate": None,  # Episode model doesn't have air_date field
            "seriesId": episode.series_id,
            "contentUuid": str(episode.content_uuid),
            "createdAt": episode.created_at.isoformat(),
            "updatedAt": episode.updated_at.isoformat()
        }
        processed_episodes.append(episode_dict)
    return processed_episodes

# @app.get("/debug/episodes/{series_id}")
# def debug_episodes(series_id: int, db: Session = Depends(get_db)):
#     """Debug endpoint to check episode poster URLs"""
#     episodes = crud.get_episodes(db, content_id=series_id, limit=3)
#     debug_data = []
#     for episode in episodes:
#         debug_data.append({
#             "id": episode.id,
#             "title": episode.title,
#             "poster_url": episode.poster_url,
#             "thumbnail_url": episode.thumbnail_url,
#             "has_poster_url": hasattr(episode, 'poster_url'),
#             "poster_url_type": type(episode.poster_url).__name__ if hasattr(episode, 'poster_url') else None
#         })
#     return debug_data

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    
    uvicorn.run(app, host="0.0.0.0", port=args.port) 