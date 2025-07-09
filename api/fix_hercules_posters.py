#!/usr/bin/env python3
"""
Script to fix Hercules poster mismatches with correct URLs.
"""

import sys
from sqlalchemy.orm import Session

# Add the current directory to Python path
sys.path.append('.')

from database import SessionLocal
from models import Content

def fix_hercules_posters():
    """Fix Hercules poster mismatches"""
    db = SessionLocal()
    try:
        print("🔧 Fixing Hercules poster mismatches...")
        print()
        
        # Define the Hercules fixes
        hercules_fixes = [
            {
                'id': 59,
                'title': 'Hercules Against the Moon Men',
                'current_poster': 'https://storage.googleapis.com/pecantv_title_images/Hercules_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Hercules-against-the-Moon-Men_Title-Img.png',
                'reason': 'Should have Moon Men specific poster'
            },
            {
                'id': 58,
                'title': 'Hercules in the Haunted World',
                'current_poster': 'https://storage.googleapis.com/pecantv_title_images/Hercules_title-img.jpg',
                'correct_poster': 'https://storage.googleapis.com/pecantv_title_images/Hercules-in-the-Haunted-World_Title-Img.png',
                'reason': 'Should have Haunted World specific poster'
            }
        ]
        
        # Fix each Hercules film
        for fix in hercules_fixes:
            film = db.query(Content).filter(Content.id == fix['id']).first()
            if film:
                print(f"✅ Fixed {film.title} (ID: {film.id})")
                print(f"   Old: {film.poster_url}")
                print(f"   New: {fix['correct_poster']}")
                print(f"   Reason: {fix['reason']}")
                print()
                film.poster_url = fix['correct_poster']
            else:
                print(f"❌ Film not found: {fix['title']} (ID: {fix['id']})")
        
        # Commit changes
        db.commit()
        print(f"🎉 Successfully fixed {len(hercules_fixes)} Hercules poster mismatches!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_hercules_posters() 