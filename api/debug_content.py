#!/usr/bin/env python3
"""
Debug script to check content database for specific issues
"""

from database import get_db
from models import Content, Episode, ContentType
from sqlalchemy.orm import Session
from sqlalchemy import text

def check_content_issues():
    """Check for the specific content issues mentioned"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔍 Checking for specific content issues...\n")
        
        # Check total content count
        total_content = db.query(Content).count()
        print(f"Total content in database: {total_content}")
        
        # Check if Get Christie Love exists
        print("\nChecking for 'Get Christie Love':")
        christie_love = db.query(Content).filter(
            Content.title.ilike("%Christie Love%")
        ).all()
        
        for content in christie_love:
            print(f"   - ID: {content.id}, Title: {content.title}, Type: {content.type}")
        
        # Check content by ID range to see what's being returned
        print("\nChecking content by ID range:")
        for i in range(0, total_content, 100):
            content_batch = db.query(Content).offset(i).limit(100).all()
            print(f"   IDs {i}-{i+99}: {len(content_batch)} items")
            
            # Check if Get Christie Love is in this batch
            christie_in_batch = [c for c in content_batch if 'Christie' in c.title]
            if christie_in_batch:
                print(f"     ✅ Get Christie Love found in batch {i//100 + 1}")
                for c in christie_in_batch:
                    print(f"       - {c.title} (ID: {c.id})")
        
        # 1. Check for Count of Monte Cristo
        print("\n1. Checking for 'Count of Monte Cristo':")
        monte_cristo = db.query(Content).filter(
            Content.title.ilike("%Monte Cristo%")
        ).all()
        
        for content in monte_cristo:
            print(f"   - ID: {content.id}, Title: {content.title}, Type: {content.type}")
            if content.type == ContentType.SERIES:
                episodes = db.query(Episode).filter(Episode.series_id == content.id).all()
                print(f"     Episodes: {len(episodes)}")
                for ep in episodes[:3]:  # Show first 3 episodes
                    print(f"       S{ep.season_number}E{ep.episode_number}: {ep.title}")
        
        print()
        
        # 2. Check for Mike Hammer
        print("2. Checking for 'Mike Hammer':")
        mike_hammer = db.query(Content).filter(
            Content.title.ilike("%Mike Hammer%")
        ).all()
        
        for content in mike_hammer:
            print(f"   - ID: {content.id}, Title: {content.title}, Type: {content.type}")
            if content.type == ContentType.SERIES:
                episodes = db.query(Episode).filter(Episode.series_id == content.id).all()
                print(f"     Episodes: {len(episodes)}")
                for ep in episodes[:3]:  # Show first 3 episodes
                    print(f"       S{ep.season_number}E{ep.episode_number}: {ep.title}")
        
        print()
        
        # 3. Check for Petrocelli episodes showing up as series
        print("4. Checking for Petrocelli episodes in series:")
        petrocelli_episodes = db.query(Episode).filter(
            Episode.title.ilike("%Petrocelli%")
        ).all()
        
        for episode in petrocelli_episodes:
            series = db.query(Content).filter(Content.id == episode.series_id).first()
            print(f"   - Episode: {episode.title}")
            print(f"     Series: {series.title if series else 'Unknown'}")
            print(f"     S{episode.season_number}E{episode.episode_number}")
        
        print()
        
        # 4. Check all series content
        print("5. All series content:")
        series_content = db.query(Content).filter(Content.type == ContentType.SERIES).all()
        
        for content in series_content:
            episodes = db.query(Episode).filter(Episode.series_id == content.id).all()
            print(f"   - {content.title} (ID: {content.id}): {len(episodes)} episodes")
        
        print()
        
        # 5. Check for episodes with missing content URLs
        print("6. Episodes with missing content URLs:")
        episodes_no_url = db.query(Episode).filter(
            (Episode.content_url.is_(None)) | (Episode.content_url == "")
        ).all()
        
        for episode in episodes_no_url[:10]:  # Show first 10
            series = db.query(Content).filter(Content.id == episode.series_id).first()
            print(f"   - {episode.title} (Series: {series.title if series else 'Unknown'})")
        
        print(f"\nTotal episodes without content URLs: {len(episodes_no_url)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_content_issues() 