#!/usr/bin/env python3
"""
Debug script to check content serialization issues
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "api"))

from database import get_db
from models import Content
from schemas import Content as ContentSchema
from sqlalchemy.orm import Session

def debug_content_serialization():
    """Debug content serialization to see why poster_url is not showing up"""
    
    db = next(get_db())
    
    try:
        print("🔍 Debugging content serialization...")
        print("=" * 50)
        
        # Get Count Duckula and Inframan specifically
        count_duckula = db.query(Content).filter(Content.id == 82).first()
        inframan = db.query(Content).filter(Content.id == 84).first()
        
        if count_duckula:
            print(f"\n📺 Count Duckula (ID: {count_duckula.id}):")
            print(f"   Title: {count_duckula.title}")
            print(f"   Raw poster_url: {repr(count_duckula.poster_url)}")
            print(f"   poster_url type: {type(count_duckula.poster_url)}")
            print(f"   poster_url is None: {count_duckula.poster_url is None}")
            print(f"   poster_url == '': {count_duckula.poster_url == ''}")
            
            # Try to serialize using the schema
            try:
                content_schema = ContentSchema.from_orm(count_duckula)
                print(f"   Schema posterURL: {content_schema.posterURL}")
                print(f"   Schema dict: {content_schema.dict()}")
            except Exception as e:
                print(f"   Schema serialization error: {e}")
        
        if inframan:
            print(f"\n📺 Inframan (ID: {inframan.id}):")
            print(f"   Title: {inframan.title}")
            print(f"   Raw poster_url: {repr(inframan.poster_url)}")
            print(f"   poster_url type: {type(inframan.poster_url)}")
            print(f"   poster_url is None: {inframan.poster_url is None}")
            print(f"   poster_url == '': {inframan.poster_url == ''}")
            
            # Try to serialize using the schema
            try:
                content_schema = ContentSchema.from_orm(inframan)
                print(f"   Schema posterURL: {content_schema.posterURL}")
                print(f"   Schema dict: {content_schema.dict()}")
            except Exception as e:
                print(f"   Schema serialization error: {e}")
        
        # Check a few other content items for comparison
        print(f"\n📋 Checking other content items for comparison:")
        other_content = db.query(Content).filter(Content.id.in_([1, 2, 3])).all()
        
        for content in other_content:
            print(f"\n   {content.title} (ID: {content.id}):")
            print(f"      Raw poster_url: {repr(content.poster_url)}")
            print(f"      poster_url is None: {content.poster_url is None}")
            
            try:
                content_schema = ContentSchema.from_orm(content)
                print(f"      Schema posterURL: {content_schema.posterURL}")
            except Exception as e:
                print(f"      Schema serialization error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_content_serialization() 