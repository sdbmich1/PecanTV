from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import List, Optional
import hashlib
import models
import schemas

# Authentication CRUD operations
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # Use enhanced auth service for secure password handling
    from enhanced_auth_service import EnhancedAuthService, PasswordValidator
    from fastapi import HTTPException, status
    
    auth_service = EnhancedAuthService()
    
    # Validate password strength
    password_validation = PasswordValidator.validate_password_strength(user.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
        )
    
    # Hash password securely
    password_hash = auth_service.get_password_hash(user.password)
    
    db_user = models.User(
        email=user.email,
        password_hash=password_hash,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_password(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if user:
        auth_service = EnhancedAuthService()
        if auth_service.verify_password(password, user.password_hash):
            return user
    return None

def get_content(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    genre: Optional[str] = None
) -> List[models.Content]:
    # Always join with genre and rating tables to ensure data is populated
    query = db.query(models.Content).options(
        joinedload(models.Content.genre),
        joinedload(models.Content.rating)
    )
    
    if type:
        query = query.filter(models.Content.type == type)
    if genre:
        query = query.join(models.content_genres).join(models.Genre).filter(
            func.lower(models.Genre.name) == func.lower(genre)
        )
    
    return query.offset(skip).limit(limit).all()

def get_content_by_id(db: Session, content_id: int) -> Optional[models.Content]:
    return db.query(models.Content).options(
        joinedload(models.Content.genre),
        joinedload(models.Content.rating)
    ).filter(models.Content.id == content_id).first()

def get_genres(db: Session, skip: int = 0, limit: int = 100) -> List[models.Genre]:
    return db.query(models.Genre).offset(skip).limit(limit).all()

def get_genre_by_id(db: Session, genre_id: int) -> Optional[models.Genre]:
    return db.query(models.Genre).filter(models.Genre.id == genre_id).first()

def get_genre_by_name(db: Session, name: str) -> Optional[models.Genre]:
    return db.query(models.Genre).filter(func.lower(models.Genre.name) == func.lower(name)).first()

def get_ratings(db: Session, skip: int = 0, limit: int = 100) -> List[models.Rating]:
    return db.query(models.Rating).offset(skip).limit(limit).all()

def get_rating_by_id(db: Session, rating_id: int) -> Optional[models.Rating]:
    return db.query(models.Rating).filter(models.Rating.id == rating_id).first()

def create_content(db: Session, content: schemas.ContentCreate) -> models.Content:
    db_content = models.Content(
        title=content.title,
        poster_url=content.poster_url,
        trailer_url=content.trailer_url,
        content_url=content.content_url,
        description=content.description,
        type=content.type,
        runtime=content.runtime,
        genre_id=content.genre_id,
        rating_id=content.rating_id,
        release_date=content.release_date
    )
    
    if content.genre_ids:
        genres = db.query(models.Genre).filter(models.Genre.id.in_(content.genre_ids)).all()
        db_content.genres = genres
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def update_content(db: Session, content_id: int, content_update: schemas.ContentUpdate) -> Optional[models.Content]:
    """Update a content item by ID"""
    db_content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if not db_content:
        return None
    
    # Update fields if provided
    if content_update.title is not None:
        db_content.title = content_update.title
    if content_update.poster_url is not None:
        db_content.poster_url = content_update.poster_url
    if content_update.trailer_url is not None:
        db_content.trailer_url = content_update.trailer_url
    if content_update.content_url is not None:
        db_content.content_url = content_update.content_url
    if content_update.description is not None:
        db_content.description = content_update.description
    if content_update.type is not None:
        db_content.type = content_update.type
    if content_update.runtime is not None:
        db_content.runtime = content_update.runtime
    if content_update.genre_id is not None:
        db_content.genre_id = content_update.genre_id
    if content_update.rating_id is not None:
        db_content.rating_id = content_update.rating_id
    if content_update.release_date is not None:
        db_content.release_date = content_update.release_date
    
    db.commit()
    db.refresh(db_content)
    return db_content

def update_content_genres(db: Session, content_id: int, genre_ids: List[int]) -> models.Content:
    content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if content:
        genres = db.query(models.Genre).filter(models.Genre.id.in_(genre_ids)).all()
        content.genres = genres
        db.commit()
        db.refresh(content)
    return content

def search_content(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.Content]:
    # Input validation
    from security_middleware import InputValidator
    from fastapi import HTTPException, status
    
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    if len(query) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query too long (max 100 characters)"
        )
    
    # Sanitize input
    is_valid, error_msg = InputValidator.validate_input(query, "search_query")
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search query: {error_msg}"
        )
    
    # Sanitize the query
    sanitized_query = InputValidator.sanitize_input(query)
    
    return db.query(models.Content).filter(
        or_(
            models.Content.title.ilike(f"%{sanitized_query}%"),
            models.Content.description.ilike(f"%{sanitized_query}%")
        )
    ).offset(skip).limit(limit).all()

# Episode CRUD operations
def get_episodes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    content_id: Optional[int] = None,
    season_number: Optional[int] = None
) -> List[models.Episode]:
    query = db.query(models.Episode)
    
    if content_id:
        query = query.filter(models.Episode.series_id == content_id)
    if season_number:
        query = query.filter(models.Episode.season_number == season_number)
    
    episodes = query.order_by(models.Episode.season_number, models.Episode.episode_number).offset(skip).limit(limit).all()
    
    # Debug logging
    for episode in episodes[:3]:
        print(f"CRUD Episode {episode.title}: poster_url={episode.poster_url}, thumbnail_url={episode.thumbnail_url}")
    
    return episodes

def get_episode_by_id(db: Session, episode_id: int) -> Optional[models.Episode]:
    return db.query(models.Episode).filter(models.Episode.id == episode_id).first()

def get_episode_by_content_and_number(
    db: Session,
    content_id: int,
    season_number: int,
    episode_number: int
) -> Optional[models.Episode]:
    return db.query(models.Episode).filter(
        models.Episode.series_id == content_id,
        models.Episode.season_number == season_number,
        models.Episode.episode_number == episode_number
    ).first()

def create_episode(db: Session, episode: schemas.EpisodeCreate) -> models.Episode:
    db_episode = models.Episode(
        title=episode.title,
        description=episode.description,
        season_number=episode.season_number,
        episode_number=episode.episode_number,
        runtime=episode.runtime,
        content_url=episode.content_url,
        poster_url=episode.poster_url,
        thumbnail_url=episode.thumbnail_url,
        series_id=episode.series_id,
        content_uuid=episode.content_uuid
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode

def get_content_with_episodes(db: Session, content_id: int) -> Optional[models.Content]:
    return db.query(models.Content).filter(models.Content.id == content_id).first()

def get_series_content(db: Session, skip: int = 0, limit: int = 100) -> List[models.Content]:
    """Get all content that has episodes (series)"""
    return db.query(models.Content).filter(
        models.Content.type == models.ContentType.SERIES
    ).offset(skip).limit(limit).all()

# Favorites CRUD operations
def get_user_favorites(db: Session, user_id: int) -> List[models.Content]:
    """Get all content favorited by a user"""
    return db.query(models.Content).join(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).all()

def toggle_user_favorite(db: Session, user_id: int, content_id: int) -> dict:
    """Toggle favorite status for a content item"""
    # Check if favorite already exists
    existing_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.content_id == content_id
    ).first()
    
    if existing_favorite:
        # Remove favorite
        db.delete(existing_favorite)
        db.commit()
        return {"is_favorited": False}
    else:
        # Add favorite
        new_favorite = models.Favorite(
            user_id=user_id,
            content_id=content_id
        )
        db.add(new_favorite)
        db.commit()
        return {"is_favorited": True}

def is_content_favorited_by_user(db: Session, user_id: int, content_id: int) -> bool:
    """Check if a content item is favorited by a user"""
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.content_id == content_id
    ).first()
    return favorite is not None 