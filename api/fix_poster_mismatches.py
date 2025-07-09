#!/usr/bin/env python3
"""
Script to fix specific poster mismatches identified in the review.
"""

import sys
from sqlalchemy.orm import Session

# Add the current directory to Python path
sys.path.append('.')

from database import SessionLocal
from models import Content

def fix_specific_mismatches():
    """Fix specific poster mismatches identified in the review"""
    
    # Define the mismatches to fix
    mismatches_to_fix = [
        {
            'id': 53,
            'title': 'Lady Frankenstein',
            'current_poster': 'https://storage.googleapis.com/pecantv_title_images/Hell-in-Normandy_title-Img-1920x1080.png',
            'correct_poster': '/pecantv_series/Lady-Frankenstein_title-img.jpg',
            'reason': 'Lady Frankenstein should not have Hell in Normandy poster'
        },
        {
            'id': 435,
            'title': 'A Fallen Idol',
            'current_poster': '/pecantv_series/Petrocelli_title-img.jpg',
            'correct_poster': '/pecantv_series/A-Fallen-Idol_title-img.jpg',
            'reason': 'A Fallen Idol should not have Petrocelli poster'
        },
        {
            'id': 433,
            'title': 'Counterploy',
            'current_poster': '/pecantv_series/Petrocelli_title-img.jpg',
            'correct_poster': '/pecantv_series/Counterploy_title-img.jpg',
            'reason': 'Counterploy should not have Petrocelli poster'
        },
        {
            'id': 618,
            'title': 'Night Games',
            'current_poster': '/pecantv_series/Petrocelli_title-img.jpg',
            'correct_poster': '/pecantv_series/Night-Games_title-img.jpg',
            'reason': 'Night Games should not have Petrocelli poster'
        }
    ]
    
    db = SessionLocal()
    try:
        print("🔧 Fixing Poster Mismatches")
        print("=" * 50)
        
        fixed_count = 0
        for mismatch in mismatches_to_fix:
            try:
                film = db.query(Content).filter(Content.id == mismatch['id']).first()
                if film:
                    old_poster = film.poster_url
                    film.poster_url = mismatch['correct_poster']
                    
                    print(f"✅ Fixed {mismatch['title']} (ID: {mismatch['id']})")
                    print(f"   Reason: {mismatch['reason']}")
                    print(f"   Old: {old_poster}")
                    print(f"   New: {mismatch['correct_poster']}")
                    print()
                    
                    fixed_count += 1
                else:
                    print(f"❌ Film not found: {mismatch['title']} (ID: {mismatch['id']})")
            except Exception as e:
                print(f"❌ Error fixing {mismatch['title']}: {e}")
        
        # Commit changes
        db.commit()
        print(f"🎉 Successfully fixed {fixed_count} poster mismatches")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def reset_to_default_poster(film_ids):
    """Reset specific films to use default poster"""
    db = SessionLocal()
    try:
        print("🔄 Resetting Films to Default Poster")
        print("=" * 40)
        
        default_poster = "/pecantv_series/default_poster.jpg"
        reset_count = 0
        
        for film_id in film_ids:
            try:
                film = db.query(Content).filter(Content.id == film_id).first()
                if film:
                    old_poster = film.poster_url
                    film.poster_url = default_poster
                    
                    print(f"✅ Reset {film.title} (ID: {film.id})")
                    print(f"   Old: {old_poster}")
                    print(f"   New: {default_poster}")
                    print()
                    
                    reset_count += 1
                else:
                    print(f"❌ Film not found: ID {film_id}")
            except Exception as e:
                print(f"❌ Error resetting film {film_id}: {e}")
        
        # Commit changes
        db.commit()
        print(f"🎉 Successfully reset {reset_count} films to default poster")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🔧 Poster Mismatch Fix Script")
    print("=" * 40)
    
    # Fix specific mismatches
    fix_specific_mismatches()
    
    # Optionally reset problematic films to default poster
    # Uncomment the line below and add film IDs that should use default poster
    # reset_to_default_poster([435, 433, 618])  # Films that had Petrocelli poster
    
    print("✅ Mismatch fixing complete!")

if __name__ == "__main__":
    main() 