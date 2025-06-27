from sqlalchemy.orm import Session
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
    # Hash the password
    password_hash = hashlib.sha256(user.password.encode()).hexdigest()
    
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
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.password_hash == password_hash:
            return user
    return None

def get_content(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    genre: Optional[str] = None
) -> List[models.Content]:
    query = db.query(models.Content)
    
    if type:
        query = query.filter(models.Content.type == type)
    if genre:
        query = query.join(models.content_genres).join(models.Genre).filter(
            func.lower(models.Genre.name) == func.lower(genre)
        )
    
    return query.offset(skip).limit(limit).all()

def get_content_by_id(db: Session, content_id: int) -> Optional[models.Content]:
    return db.query(models.Content).filter(models.Content.id == content_id).first()

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
    return db.query(models.Content).filter(
        or_(
            models.Content.title.ilike(f"%{query}%"),
            models.Content.description.ilike(f"%{query}%")
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
    
    return query.order_by(models.Episode.season_number, models.Episode.episode_number).offset(skip).limit(limit).all()

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
        thumbnail_url=episode.thumbnail_url,
        poster_url=episode.poster_url,
        air_date=episode.air_date,
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