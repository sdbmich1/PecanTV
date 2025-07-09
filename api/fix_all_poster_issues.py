#!/usr/bin/env python3
"""
Comprehensive script to fix all poster issues:
1. Convert local paths to Google Cloud Storage URLs
2. Fix mismatched posters
3. Ensure all posters point to pecantv_title_images folder
"""

import sys
from sqlalchemy.orm import Session

# Add the current directory to Python path
sys.path.append('.')

from database import SessionLocal
from models import Content

def fix_poster_urls():
    """Fix all poster URL issues"""
    db = SessionLocal()
    try:
        films = db.query(Content).filter(Content.type == "FILM").all()
        
        print("🎬 Starting comprehensive poster URL fixes...")
        print(f"📊 Processing {len(films)} films")
        print()
        
        # Define the mismatches to fix
        mismatches_to_fix = [
            {
                'id': 655,
                'title': 'A Lonely Victim',
                'current_poster': '/pecantv_series/Petrocelli_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/A-Lonely-Victim_title-img.png',
                'reason': 'Has Petrocelli poster (wrong series)'
            },
            {
                'id': 647,
                'title': 'Terror on Wheels',
                'current_poster': '/pecantv_series/Dick-Tracy_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Terror-on-Wheels_title-img.png',
                'reason': 'Has Dick Tracy poster (wrong film)'
            },
            {
                'id': 646,
                'title': 'The Gamblers',
                'current_poster': '/pecantv_series/GetChristieLove_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/The-Gamblers_title-img.png',
                'reason': 'Has GetChristieLove poster (wrong series)'
            },
            {
                'id': 643,
                'title': 'Jubilee Jones',
                'current_poster': '/pecantv_series/Black-Brigade_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Jubilee-Jones_title-img.png',
                'reason': 'Has Black Brigade poster (wrong film)'
            },
            {
                'id': 641,
                'title': 'Any Number Can Die',
                'current_poster': '/pecantv_series/Frederick-Douglass_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Any-Number-Can-Die_title-img.png',
                'reason': 'Has Frederick Douglass poster (wrong film)'
            },
            {
                'id': 640,
                'title': 'Blood Money',
                'current_poster': '/pecantv_series/Ghost-Squad_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Blood-Money_title-img.png',
                'reason': 'Has Ghost Squad poster (wrong series)'
            },
            {
                'id': 624,
                'title': 'Mirror, Mirror on the Wall',
                'current_poster': '/pecantv_series/dementia-13_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Mirror-Mirror-on-the-Wall_title-img.png',
                'reason': 'Has dementia-13 poster (wrong film)'
            },
            {
                'id': 621,
                'title': 'Death in High Places',
                'current_poster': '/pecantv_series/Brother-from-Another-Planet_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Death-in-High-Places_title-img.png',
                'reason': 'Has Brother from Another Planet poster (wrong film)'
            },
            {
                'id': 620,
                'title': 'The Golden Cage',
                'current_poster': '/pecantv_series/Beyond-Christmas_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/The-Golden-Cage_title-img.png',
                'reason': 'Has Beyond Christmas poster (wrong film)'
            },
            {
                'id': 618,
                'title': 'Night Games',
                'current_poster': '/pecantv_series/Petrocelli_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Night-Games_title-img.png',
                'reason': 'Has Petrocelli poster (wrong series)'
            },
            {
                'id': 457,
                'title': 'Sherlock Holmes: The Sign of Four',
                'current_poster': '/pecantv_series/Sherlock-Holmes_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-The-Sign-of-Four_title-img.png',
                'reason': 'Has generic Sherlock Holmes poster (wrong episode)'
            },
            {
                'id': 459,
                'title': 'Sherlock Holmes: The Hound of the Baskervilles',
                'current_poster': '/pecantv_series/Sherlock-Holmes_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-The-Hound-of-the-Baskervilles_title-img.png',
                'reason': 'Has generic Sherlock Holmes poster (wrong episode)'
            },
            {
                'id': 460,
                'title': 'Sherlock Holmes: The Red-Headed League',
                'current_poster': '/pecantv_series/Sherlock-Holmes_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Sherlock-Holmes-The-Red-Headed-League_title-img.png',
                'reason': 'Has generic Sherlock Holmes poster (wrong episode)'
            }
        ]
        
        # Fix specific mismatches
        print("🔧 Fixing specific poster mismatches...")
        for mismatch in mismatches_to_fix:
            film = db.query(Content).filter(Content.id == mismatch['id']).first()
            if film:
                print(f"✅ Fixed {film.title} (ID: {film.id})")
                print(f"   Old: {film.poster_url}")
                print(f"   New: {mismatch['correct_poster']}")
                print(f"   Reason: {mismatch['reason']}")
                print()
                film.poster_url = mismatch['correct_poster']
        
        # Convert all local paths to Google Cloud Storage URLs
        print("🌐 Converting local paths to Google Cloud Storage URLs...")
        converted_count = 0
        
        for film in films:
            if film.poster_url and film.poster_url.startswith('/pecantv_series/'):
                # Extract filename from local path
                filename = film.poster_url.replace('/pecantv_series/', '')
                
                # Convert to Google Cloud Storage URL
                new_url = f"https://storage.googleapis.com/pecantv_title_images/{filename}"
                
                print(f"✅ Converted {film.title} (ID: {film.id})")
                print(f"   Old: {film.poster_url}")
                print(f"   New: {new_url}")
                print()
                
                film.poster_url = new_url
                converted_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"🎉 Successfully fixed {len(mismatches_to_fix)} mismatches and converted {converted_count} local paths!")
        print("✅ All poster URLs now point to Google Cloud Storage pecantv_title_images folder")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_poster_urls() 