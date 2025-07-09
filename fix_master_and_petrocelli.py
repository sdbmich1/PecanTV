#!/usr/bin/env python3
"""
Fix The Master and Petrocelli episodes issues:
1. The Master should not be associated with Master of the Flying Guillotine
2. Petrocelli episodes 9-22 have incorrect runtime (3600 min) and wrong posters
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def get_content_by_title(title: str) -> Dict[str, Any]:
    """Get content by title"""
    response = requests.get(f"{BASE_URL}/content")
    if response.status_code == 200:
        content = response.json()
        for item in content:
            if item.get('title') == title:
                return item
    return None

def update_content(content_id: int, updates: Dict[str, Any]) -> bool:
    """Update content via API"""
    url = f"{BASE_URL}/content/{content_id}"
    response = requests.put(url, json=updates)
    return response.status_code == 200

def get_episodes_by_series(series_id: int) -> list:
    """Get episodes for a series"""
    response = requests.get(f"{BASE_URL}/series/{series_id}/episodes")
    if response.status_code == 200:
        return response.json()
    return []

def update_episode(episode_id: int, updates: Dict[str, Any]) -> bool:
    """Update episode via API"""
    url = f"{BASE_URL}/episodes/{episode_id}"
    response = requests.put(url, json=updates)
    return response.status_code == 200

def fix_the_master():
    """Fix The Master - remove incorrect content URL"""
    print("🔧 Fixing The Master...")
    
    master = get_content_by_title("The Master")
    if not master:
        print("❌ The Master not found")
        return
    
    print(f"📽️ Found The Master (ID: {master['id']})")
    print(f"   Current content URL: {master.get('contentURL', 'NONE')}")
    
    # Clear the incorrect content URL
    updates = {
        "contentURL": None,
        "runtime": 0,
        "description": ""
    }
    
    if update_content(master['id'], updates):
        print("✅ The Master fixed - content URL cleared")
    else:
        print("❌ Failed to update The Master")

def fix_petrocelli_episodes():
    """Fix Petrocelli episodes 9-22 runtime and posters"""
    print("\n🔧 Fixing Petrocelli episodes...")
    
    episodes = get_episodes_by_series(21)  # Petrocelli series ID
    if not episodes:
        print("❌ Petrocelli episodes not found")
        return
    
    print(f"📺 Found {len(episodes)} Petrocelli episodes")
    
    # Correct poster URL for episodes 9-22
    correct_poster = "https://storage.googleapis.com/pecantv_title_images/Petrocelli_title-img.jpg"
    
    fixed_count = 0
    for episode in episodes:
        episode_num = episode.get('episode_number', 0)
        runtime = episode.get('runtime', 0)
        poster = episode.get('posterURL', '')
        
        # Fix episodes 9-22 (runtime 3600 and wrong poster)
        if runtime == 3600 or (episode_num >= 9 and poster != correct_poster):
            updates = {
                "runtime": 60,  # Correct runtime for TV episodes
                "posterURL": correct_poster
            }
            
            if update_episode(episode['id'], updates):
                print(f"✅ Fixed Episode {episode_num}: {episode.get('title', 'N/A')}")
                print(f"   Runtime: 3600 → 60 min")
                print(f"   Poster: {poster} → {correct_poster}")
                fixed_count += 1
            else:
                print(f"❌ Failed to update Episode {episode_num}")
    
    print(f"\n🎯 Fixed {fixed_count} Petrocelli episodes")

def main():
    """Main function"""
    print("🚀 Starting fixes for The Master and Petrocelli episodes...")
    
    # Fix The Master
    fix_the_master()
    
    # Fix Petrocelli episodes
    fix_petrocelli_episodes()
    
    print("\n✅ All fixes completed!")

if __name__ == "__main__":
    main() 