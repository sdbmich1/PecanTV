from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

class ContentType(str, enum.Enum):
    FILM = "FILM"
    SERIES = "SERIES"

# User model for authentication
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

# Junction table for many-to-many relationship between content and genres
content_genres = Table(
    'content_genres',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('content_id', Integer, ForeignKey('content.id', ondelete='CASCADE')),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE')),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-many relationship with content
    content_items = relationship("Content", secondary=content_genres, back_populates="genres")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    description = Column(Text)
    min_age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    content = relationship("Content", back_populates="rating")

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    poster_url = Column(Text, nullable=False)
    trailer_url = Column(Text, nullable=False)
    content_url = Column(Text, nullable=False)
    description = Column(Text)
    type = Column(Enum(ContentType), nullable=False)
    runtime = Column(Integer, nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"))  # Keep for backward compatibility
    rating_id = Column(Integer, ForeignKey("ratings.id"))
    release_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-many relationship with genres
    genres = relationship("Genre", secondary=content_genres, back_populates="content_items")
    # Keep single genre relationship for backward compatibility
    genre = relationship("Genre", foreign_keys=[genre_id])
    rating = relationship("Rating", back_populates="content") 