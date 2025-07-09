#!/usr/bin/env python3
"""
Script to check all film poster URLs and identify broken ones
"""

import requests
from database import get_db
from models import Content, ContentType

def check_poster_urls():
    """Check all film poster URLs for 404 errors"""
    
    db = next(get_db())
    
    try:
        # Get all films
        films = db.query(Content).filter(Content.type == ContentType.FILM).all()
        
        print(f"🔍 Checking {len(films)} films for broken poster URLs...")
        print("=" * 80)
        
        broken_posters = []
        working_posters = []
        
        for film in films:
            if not film.poster_url or film.poster_url == 'NONE':
                continue
                
            print(f"Checking: {film.title}")
            print(f"  URL: {film.poster_url}")
            
            try:
                response = requests.head(film.poster_url, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ Status: {response.status_code}")
                    working_posters.append(film)
                else:
                    print(f"  ❌ Status: {response.status_code}")
                    broken_posters.append(film)
            except Exception as e:
                print(f"  ❌ Error: {e}")
                broken_posters.append(film)
            
            print()
        
        # Summary
        print("=" * 80)
        print(f"📊 SUMMARY:")
        print(f"  ✅ Working posters: {len(working_posters)}")
        print(f"  ❌ Broken posters: {len(broken_posters)}")
        
        if broken_posters:
            print(f"\n🔧 BROKEN POSTERS NEEDING FIX:")
            for film in broken_posters:
                print(f"  - {film.title} (ID: {film.id})")
                print(f"    URL: {film.poster_url}")
        
    except Exception as e:
        print(f"❌ Error checking posters: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_poster_urls() 