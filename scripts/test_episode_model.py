#!/usr/bin/env python3
"""
Test script to check Episode model poster_url loading
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Episode

# Database connection
DATABASE_URL = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def test_episode_model():
    """Test if Episode model loads poster_url correctly"""
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Query episodes directly
        episodes = db.query(Episode).filter(Episode.series_id == 78).limit(3).all()
        
        print("Episode model test:")
        for episode in episodes:
            print(f"  Title: {episode.title}")
            print(f"    poster_url: {episode.poster_url}")
            print(f"    thumbnail_url: {episode.thumbnail_url}")
            print(f"    hasattr poster_url: {hasattr(episode, 'poster_url')}")
            print(f"    episode.__dict__ keys: {list(episode.__dict__.keys())}")
            print()
        
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_episode_model() 