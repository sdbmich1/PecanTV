#!/usr/bin/env python3
"""
Final verification script to confirm all changes are working correctly.
"""

import requests
import json

def verify_all_changes():
    """Verify all the changes we made are working correctly."""
    base_url = "https://77b9-192-69-240-171.ngrok-free.app"
    
    try:
        print("🔍 Final Verification of All Changes")
        print("=" * 60)
        
        # Test content endpoint
        response = requests.get(f"{base_url}/content")
        print(f"GET /content: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content returned: {len(data)} items")
            
            # Check for Sherlock Holmes 1, 2, 3 (should be removed)
            sherlock_123 = [item for item in data if item.get('title') in ['Sherlock Holmes 1', 'Sherlock Holmes 2', 'Sherlock Holmes 3']]
            print(f"\n🔍 Sherlock Holmes 1,2,3 check:")
            if len(sherlock_123) == 0:
                print("✅ Sherlock Holmes 1, 2, 3 have been removed")
            else:
                print(f"❌ Found {len(sherlock_123)} Sherlock Holmes 1,2,3 items that should be removed")
            
            # Check for Beginnings as Longstreet episode
            beginnings = [item for item in data if item.get('title') == 'Beginnings']
            print(f"\n🔍 Beginnings episode check:")
            if beginnings:
                beginnings_item = beginnings[0]
                if beginnings_item.get('type') == 'SERIES':
                    print("✅ Beginnings is now a SERIES")
                else:
                    print(f"❌ Beginnings is still {beginnings_item.get('type')}")
            else:
                print("❌ Beginnings not found")
            
            # Check for Dragnet Animated episodes
            dragnet_animated = [item for item in data if 'Dragnet Animated' in item.get('title', '')]
            print(f"\n🔍 Dragnet Animated episodes check:")
            print(f"Found {len(dragnet_animated)} Dragnet Animated episodes")
            for item in dragnet_animated[:3]:  # Show first 3
                print(f"  • {item.get('title')} -> Type: {item.get('type')}")
            
            # Count content types
            films = [item for item in data if item.get('type') == 'FILM']
            series = [item for item in data if item.get('type') == 'SERIES']
            print(f"\n📊 Content Distribution:")
            print(f"  • Films: {len(films)}")
            print(f"  • Series: {len(series)}")
            print(f"  • Total: {len(data)}")
            
            # Check for missing genre/rating data
            missing_genre = [item for item in data if not item.get('genre') or not item.get('genre', {}).get('name')]
            missing_rating = [item for item in data if not item.get('rating') or not item.get('rating', {}).get('code')]
            print(f"\n🔍 Data Completeness:")
            print(f"  • Items missing genre: {len(missing_genre)}")
            print(f"  • Items missing rating: {len(missing_rating)}")
            
            if len(missing_genre) == 0 and len(missing_rating) == 0:
                print("✅ All content has genre and rating data!")
            else:
                print("❌ Some content still missing genre or rating data")
            
            # Test favorites endpoint
            response = requests.get(f"{base_url}/favorites/1")
            print(f"\n🌐 Favorites API Test:")
            print(f"GET /favorites/1: {response.status_code}")
            
            if response.status_code == 200:
                favorites_data = response.json()
                favorites = favorites_data.get('favorites', [])
                print(f"✅ Favorites returned: {len(favorites)} items")
                
                # Check if any favorites point to removed Sherlock Holmes items
                sherlock_favorites = [fav for fav in favorites if fav.get('title') in ['Sherlock Holmes 1', 'Sherlock Holmes 2', 'Sherlock Holmes 3']]
                if len(sherlock_favorites) == 0:
                    print("✅ No favorites pointing to removed Sherlock Holmes items")
                else:
                    print(f"❌ Found {len(sherlock_favorites)} favorites pointing to removed items")
            else:
                print(f"❌ Favorites error: {response.text}")
            
        else:
            print(f"❌ Content error: {response.text}")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    verify_all_changes() 