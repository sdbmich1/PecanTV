from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List
import uuid
from models import ContentType

# Authentication schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int  # Keep for backward compatibility
    uuid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class GenreBase(BaseModel):
    name: str
    description: Optional[str] = None

class GenreCreate(GenreBase):
    pass

class Genre(GenreBase):
    id: int  # Keep for backward compatibility
    uuid: uuid.UUID
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True

class RatingBase(BaseModel):
    code: str
    description: Optional[str] = None
    min_age: Optional[int] = Field(None, alias="minAge")

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int  # Keep for backward compatibility
    uuid: uuid.UUID
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True

class ContentBase(BaseModel):
    title: str
    poster_url: str = Field(alias="posterURL")
    trailer_url: str = Field(alias="trailerURL")
    content_url: str = Field(alias="contentURL")
    description: Optional[str] = None
    type: ContentType
    runtime: int
    genre_id: Optional[int] = Field(None, alias="genreId")  # Keep for backward compatibility
    rating_id: Optional[int] = Field(None, alias="ratingId")
    release_date: Optional[date] = Field(None, alias="releaseDate")

class ContentCreate(ContentBase):
    genre_ids: Optional[List[int]] = Field(None, alias="genreIds")  # New field for multiple genres

class Content(ContentBase):
    id: int  # Keep for backward compatibility
    uuid: uuid.UUID
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    genres: List[Genre] = []  # Multiple genres
    genre: Optional[Genre] = None  # Keep for backward compatibility
    rating: Optional[Rating] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class ContentGenreBase(BaseModel):
    content_id: int = Field(alias="contentId")  # Keep for backward compatibility
    genre_id: int = Field(alias="genreId")  # Keep for backward compatibility
    content_uuid: uuid.UUID = Field(alias="contentUuid")
    genre_uuid: uuid.UUID = Field(alias="genreUuid")

class ContentGenreCreate(ContentGenreBase):
    pass

class ContentGenre(ContentGenreBase):
    id: int
    created_at: datetime = Field(alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True

# Episode schemas
class EpisodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    season_number: int = Field(alias="seasonNumber")
    episode_number: int = Field(alias="episodeNumber")
    runtime: Optional[int] = None
    content_url: str = Field(alias="contentURL")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailURL")  # Database column name
    poster_url: Optional[str] = Field(None, alias="posterURL")  # This column exists in database
    air_date: Optional[date] = Field(None, alias="airDate")  # Database column name
    series_id: int = Field(alias="seriesId")  # Database column name
    content_uuid: uuid.UUID = Field(alias="contentUuid")

class EpisodeCreate(EpisodeBase):
    pass

class Episode(EpisodeBase):
    id: int  # Keep for backward compatibility
    uuid: uuid.UUID
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    content: Optional[Content] = None

    class Config:
        from_attributes = True
        populate_by_name = True 