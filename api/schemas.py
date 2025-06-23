from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List
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
    id: int
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
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    code: str
    description: Optional[str] = None
    min_age: Optional[int] = None

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentBase(BaseModel):
    title: str
    poster_url: str
    trailer_url: str
    content_url: str
    description: Optional[str] = None
    type: ContentType
    runtime: int
    genre_id: Optional[int] = None  # Keep for backward compatibility
    rating_id: Optional[int] = None
    release_date: Optional[date] = None

class ContentCreate(ContentBase):
    genre_ids: Optional[List[int]] = None  # New field for multiple genres

class Content(ContentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    genres: List[Genre] = []  # Multiple genres
    genre: Optional[Genre] = None  # Keep for backward compatibility
    rating: Optional[Rating] = None

    class Config:
        from_attributes = True

class ContentGenreBase(BaseModel):
    content_id: int
    genre_id: int

class ContentGenreCreate(ContentGenreBase):
    pass

class ContentGenre(ContentGenreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 