from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

from database import Base

class ContentType(str, enum.Enum):
    FILM = "FILM"
    SERIES = "SERIES"
    EPISODE = "EPISODE"

# User model for authentication
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Keep for backward compatibility
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
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
    Column('content_id', Integer, ForeignKey('content.id', ondelete='CASCADE')),  # Keep for backward compatibility
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE')),    # Keep for backward compatibility
    Column('content_uuid', UUID(as_uuid=True), ForeignKey('content.uuid', ondelete='CASCADE')),
    Column('genre_uuid', UUID(as_uuid=True), ForeignKey('genres.uuid', ondelete='CASCADE')),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)  # Keep for backward compatibility
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-many relationship with content - temporarily commented out
    # content_items = relationship(
    #     "Content",
    #     secondary=content_genres,
    #     back_populates="genres",
    #     foreign_keys="[content_genres.c.genre_uuid, content_genres.c.content_uuid]"
    # )

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)  # Keep for backward compatibility
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    code = Column(String(10), unique=True, nullable=False)
    description = Column(Text)
    min_age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    content = relationship("Content", back_populates="rating")

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)  # Keep for backward compatibility
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    poster_url = Column(Text, nullable=False)
    trailer_url = Column(Text, nullable=False)
    content_url = Column(Text, nullable=False)
    description = Column(Text)
    type = Column(Enum(ContentType), nullable=False)
    runtime = Column(Integer, nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"))  # Keep for backward compatibility
    rating_id = Column(Integer, ForeignKey("ratings.id"))  # Keep for backward compatibility
    release_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-many relationship with genres - temporarily commented out
    # genres = relationship(
    #     "Genre",
    #     secondary=content_genres,
    #     back_populates="content_items",
    #     foreign_keys="[content_genres.c.content_uuid, content_genres.c.genre_uuid]"
    # )
    # Keep single genre relationship for backward compatibility
    genre = relationship("Genre", foreign_keys=[genre_id])
    rating = relationship("Rating", back_populates="content")
    # One-to-many relationship with episodes - use UUID foreign key
    episodes = relationship(
        "Episode", 
        back_populates="content", 
        cascade="all, delete-orphan",
        foreign_keys="[Episode.content_uuid]"
    )

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)  # Keep for backward compatibility
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    season_number = Column(Integer, nullable=False)
    episode_number = Column(Integer, nullable=False)
    runtime = Column(Integer)
    content_url = Column(Text, nullable=False)
    poster_url = Column(Text)  # Keep this column
    series_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)  # Database has series_id
    content_uuid = Column(UUID(as_uuid=True), ForeignKey("content.uuid", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with content - specify which foreign key to use
    content = relationship("Content", back_populates="episodes", foreign_keys=[content_uuid])

    # Composite unique constraint for season/episode within a series
    __table_args__ = (
        # This would be added via migration: UniqueConstraint('content_uuid', 'season_number', 'episode_number', name='unique_episode')
    )

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    content = relationship("Content") 