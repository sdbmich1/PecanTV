from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

def get_database_url():
    """
    Get database URL from environment variables.
    For Neon, we need to handle both direct and pooled connections.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Fallback for development - you should set DATABASE_URL in .env
        print("⚠️  DATABASE_URL not found in environment variables")
        print("📝 Please create a .env file in the api/ directory with:")
        print("   DATABASE_URL=your_neon_database_url_here")
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Handle Neon database URL transformation
    if "neon.tech" in database_url:
        # Parse the URL to handle Neon's connection requirements
        parsed = urllib.parse.urlparse(database_url)
        
        # For Neon, we might need to use the pooled connection
        if "pooler" not in parsed.netloc:
            # Convert to pooled connection if not already
            netloc = parsed.netloc.replace(".neon.tech", "-pooler.neon.tech")
            database_url = urllib.parse.urlunparse((
                parsed.scheme, netloc, parsed.path,
                parsed.params, parsed.query, parsed.fragment
            ))
            print(f"🔄 Using Neon pooled connection: {netloc}")
    
    return database_url

# Get database URL
DATABASE_URL = get_database_url()

# Create SQLAlchemy engine with optimized settings for Neon
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Additional connections that can be created
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections after 5 minutes (Neon recommendation)
    connect_args={
        "connect_timeout": 10,
        "application_name": "pecantv_api",
        "sslmode": "require"  # Required for Neon
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        # Test connection with proper SQLAlchemy text() function
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_database_connection():
    """
    Test database connection and print status
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful")
            print(f"📊 Database version: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# Test connection on module load
if __name__ == "__main__":
    test_database_connection() 