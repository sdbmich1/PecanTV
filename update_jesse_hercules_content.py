#!/usr/bin/env python3
"""
Script to update content URLs for Jesse Owens and Hercules films
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# Content URL mappings
content_updates = {
    "Jesse Owens: The Fastest Man in the World Part I": "https://storage.googleapis.com/pecantv_features/Jesse-Owens-Part-I_2P-720p-fullCredits.mp4",
    "Jesse Owens: The Fastest Man in the World Part II": "https://storage.googleapis.com/pecantv_features/Jesse-Owens-Part-II_2P-720p-fullCredits.mp4",
    "Hercules": "https://storage.googleapis.com/pecantv_features/Hercules_2p-1080-credit-role.mp4"
}

def get_all_content():
    """Get all content from the API"""
    try:
        response = requests.get(f"{BASE_URL}/content")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching content: {e}")
        return None

def update_content_url(content_id, new_content_url):
    """Update the content URL for a specific content item"""
    try:
        update_data = {"contentURL": new_content_url}
        response = requests.patch(f"{BASE_URL}/content/{content_id}", json=update_data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error updating content {content_id}: {e}")
        return None

def main():
    print("🔍 Fetching all content...")
    content = get_all_content()
    
    if not content:
        print("❌ Failed to fetch content")
        return
    
    print(f"📋 Found {len(content)} content items")
    
    # Find and update the specified films
    updated_count = 0
    
    for item in content:
        title = item.get('title', '')
        
        if title in content_updates:
            content_id = item.get('id')
            current_url = item.get('contentURL', '')
            new_url = content_updates[title]
            
            print(f"\n🎬 Found: {title}")
            print(f"   Current URL: {current_url}")
            print(f"   New URL: {new_url}")
            
            if current_url != new_url:
                print(f"   🔄 Updating...")
                result = update_content_url(content_id, new_url)
                if result:
                    print(f"   ✅ Successfully updated!")
                    updated_count += 1
                else:
                    print(f"   ❌ Failed to update")
            else:
                print(f"   ℹ️  URL already correct")
    
    print(f"\n📊 Summary: Updated {updated_count} content items")
    
    # Verify the updates
    print("\n🔍 Verifying updates...")
    updated_content = get_all_content()
    
    for item in updated_content:
        title = item.get('title', '')
        if title in content_updates:
            content_url = item.get('contentURL', '')
            expected_url = content_updates[title]
            status = "✅" if content_url == expected_url else "❌"
            print(f"{status} {title}: {content_url}")

if __name__ == "__main__":
    main() 