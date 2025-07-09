#!/usr/bin/env python3
"""
Fix content type categorization issues
"""

from database import get_db
from models import Content, Episode, ContentType
from sqlalchemy.orm import Session

def fix_content_types():
    """Fix content types that are incorrectly categorized"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔧 Fixing content type categorization issues...\n")
        
        # 1. Find all content that has episodes but is marked as SERIES
        # These should remain as SERIES
        series_with_episodes = db.query(Content).filter(
            Content.type == ContentType.SERIES
        ).all()
        
        print("1. Checking series with episodes:")
        for content in series_with_episodes:
            episodes = db.query(Episode).filter(Episode.series_id == content.id).all()
            if episodes:
                print(f"   ✅ {content.title} (ID: {content.id}): {len(episodes)} episodes - CORRECT")
            else:
                print(f"   ❌ {content.title} (ID: {content.id}): 0 episodes - NEEDS FIX")
        
        print()
        
        # 2. Find content marked as SERIES but has no episodes
        # These should be changed to FILM or EPISODE
        series_without_episodes = db.query(Content).filter(
            Content.type == ContentType.SERIES
        ).all()
        
        series_to_fix = []
        for content in series_without_episodes:
            episodes = db.query(Episode).filter(Episode.series_id == content.id).all()
            if not episodes:
                series_to_fix.append(content)
        
        print(f"2. Found {len(series_to_fix)} series without episodes that need fixing:")
        for content in series_to_fix:
            print(f"   - {content.title} (ID: {content.id})")
        
        print()
        
        # 3. Check if these are actually individual episodes that should be FILM
        print("3. Checking if these are individual episodes:")
        for content in series_to_fix:
            # Check if the title looks like an episode title
            if any(keyword in content.title.lower() for keyword in [
                'shadow of fear', 'night visitor', 'deadly journey', 'face of evil',
                'episode', 'part', 'chapter', 'act'
            ]):
                print(f"   - {content.title} looks like an individual episode")
                # Change to FILM
                content.type = ContentType.FILM
                print(f"     ✅ Changed to FILM")
            else:
                print(f"   - {content.title} - keeping as SERIES for now")
        
        # 4. Commit changes
        db.commit()
        print(f"\n✅ Fixed {len([c for c in series_to_fix if c.type == ContentType.FILM])} content items")
        
        # 5. Verify the fix
        print("\n4. Verification - checking series content after fix:")
        series_after_fix = db.query(Content).filter(Content.type == ContentType.SERIES).all()
        
        for content in series_after_fix:
            episodes = db.query(Episode).filter(Episode.series_id == content.id).all()
            if episodes:
                print(f"   ✅ {content.title} (ID: {content.id}): {len(episodes)} episodes")
            else:
                print(f"   ⚠️  {content.title} (ID: {content.id}): 0 episodes (may need manual review)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_content_types() 