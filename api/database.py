from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - handle both Docker and local development
# If running locally, use localhost:5433, otherwise use Docker hostname
if os.getenv("RUNNING_LOCALLY"):
    DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5433/pecantv"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@postgres:5432/pecantv"
    )

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 