#!/usr/bin/env python3
"""
Fix The Master and Petrocelli episodes issues:
1. The Master should not be associated with Master of the Flying Guillotine (via API)
2. Petrocelli episodes 9-22 have incorrect runtime (3600 min) and wrong posters (via direct SQL)
"""

import requests
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "api"))

from database import engine
from sqlalchemy import text

# API base URL
BASE_URL = "http://localhost:8000"

def get_content_by_title(title: str):
    """Get content by title via API"""
    response = requests.get(f"{BASE_URL}/content")
    if response.status_code == 200:
        content = response.json()
        for item in content:
            if item.get('title') == title:
                return item
    return None

def update_content_via_api(content_id: int, updates: dict) -> bool:
    """Update content via API"""
    url = f"{BASE_URL}/content/{content_id}"
    response = requests.put(url, json=updates)
    return response.status_code == 200

def fix_the_master():
    """Fix The Master - remove incorrect content URL via API"""
    print("🔧 Fixing The Master via API...")
    
    master = get_content_by_title("The Master")
    if not master:
        print("❌ The Master not found")
        return False
    
    print(f"📽️ Found The Master (ID: {master['id']})")
    print(f"   Current content URL: {master.get('contentURL', 'NONE')}")
    
    # Clear the incorrect content URL
    updates = {
        "contentURL": None,
        "runtime": 0,
        "description": ""
    }
    
    if update_content_via_api(master['id'], updates):
        print("✅ The Master fixed - content URL cleared")
        return True
    else:
        print("❌ Failed to update The Master via API")
        return False

def fix_petrocelli_episodes():
    """Fix Petrocelli episodes 9-22 runtime and posters via direct SQL"""
    print("\n🔧 Fixing Petrocelli episodes via direct SQL...")
    
    with engine.connect() as conn:
        # Get Petrocelli episodes with runtime 3600
        result = conn.execute(text("""
            SELECT id, episode_number, title, runtime, poster_url 
            FROM episodes 
            WHERE series_id = 21 AND runtime = 3600
            ORDER BY episode_number
        """))
        
        episodes = result.fetchall()
        print(f"📺 Found {len(episodes)} Petrocelli episodes with incorrect runtime (3600 min)")
        
        if not episodes:
            print("ℹ️  No episodes found with runtime 3600")
            return True
        
        # Correct poster URL for episodes 9-22
        correct_poster = "https://storage.googleapis.com/pecantv_title_images/Petrocelli_title-img.jpg"
        
        fixed_count = 0
        for episode in episodes:
            episode_id, episode_num, title, runtime, poster = episode
            
            print(f"🔧 Fixing Episode {episode_num}: {title}")
            print(f"   Current runtime: {runtime} min")
            print(f"   Current poster: {poster}")
            
            # Update runtime to 60 minutes and fix poster
            update_result = conn.execute(text("""
                UPDATE episodes 
                SET runtime = 60, poster_url = :poster_url, updated_at = NOW()
                WHERE id = :episode_id
            """), {
                "poster_url": correct_poster,
                "episode_id": episode_id
            })
            
            if update_result.rowcount > 0:
                print(f"   ✅ Fixed: runtime 3600 → 60 min, poster updated")
                fixed_count += 1
            else:
                print(f"   ❌ Failed to update episode {episode_num}")
        
        # Commit all changes
        conn.commit()
        print(f"\n🎯 Fixed {fixed_count} Petrocelli episodes")
        return True

def verify_fixes():
    """Verify the fixes were applied correctly"""
    print("\n🔍 Verifying fixes...")
    
    # Verify The Master
    master = get_content_by_title("The Master")
    if master:
        print(f"📽️ The Master verification:")
        print(f"   Content URL: {master.get('contentURL', 'NONE')}")
        print(f"   Runtime: {master.get('runtime', 'NONE')} min")
    
    # Verify Petrocelli episodes
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT episode_number, title, runtime, poster_url 
            FROM episodes 
            WHERE series_id = 21 AND episode_number >= 9
            ORDER BY episode_number
        """))
        
        episodes = result.fetchall()
        print(f"\n📺 Petrocelli episodes 9-22 verification:")
        
        for episode in episodes:
            episode_num, title, runtime, poster = episode
            print(f"   Episode {episode_num}: {title}")
            print(f"      Runtime: {runtime} min")
            print(f"      Poster: {poster}")
            print()

def main():
    """Main function"""
    print("🚀 Starting fixes for The Master and Petrocelli episodes...")
    print("=" * 60)
    
    success = True
    
    # Fix The Master via API
    if not fix_the_master():
        success = False
    
    # Fix Petrocelli episodes via direct SQL
    if not fix_petrocelli_episodes():
        success = False
    
    # Verify fixes
    verify_fixes()
    
    if success:
        print("\n✅ All fixes completed successfully!")
    else:
        print("\n⚠️  Some fixes may have failed. Please check the output above.")

if __name__ == "__main__":
    main() 