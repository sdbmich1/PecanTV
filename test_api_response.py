#!/usr/bin/env python3
"""
Script to test API response and check for missing genre/rating data.
"""

import requests
import json

def test_api_response():
    """Test the API response and check for missing data."""
    base_url = "https://77b9-192-69-240-171.ngrok-free.app"
    
    try:
        # Test content endpoint
        response = requests.get(f"{base_url}/content")
        print(f"GET /content: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content returned: {len(data)} items")
            
            # Check first few items for genre and rating data
            print("\n🔍 Checking first 5 items for genre and rating data:")
            print("=" * 80)
            
            for i, item in enumerate(data[:5]):
                print(f"\nItem {i+1}: {item.get('title', 'Unknown')}")
                print(f"  Type: {item.get('type', 'Unknown')}")
                print(f"  Runtime: {item.get('runtime', 'Unknown')}")
                
                # Check genre data
                genre = item.get('genre')
                if genre and genre.get('name'):
                    print(f"  Genre: {genre['name']}")
                else:
                    print(f"  Genre: MISSING or EMPTY")
                
                # Check rating data
                rating = item.get('rating')
                if rating and rating.get('code'):
                    print(f"  Rating: {rating['code']}")
                else:
                    print(f"  Rating: MISSING or EMPTY")
                
                # Check genres array
                genres = item.get('genres', [])
                if genres:
                    genre_names = [g.get('name', 'Unknown') for g in genres]
                    print(f"  Genres Array: {genre_names}")
                else:
                    print(f"  Genres Array: EMPTY")
            
            # Check for items with missing genre or rating
            print(f"\n🔍 Checking all items for missing data:")
            print("=" * 80)
            
            missing_genre = 0
            missing_rating = 0
            
            for item in data:
                genre = item.get('genre')
                if not genre or not genre.get('name'):
                    missing_genre += 1
                
                rating = item.get('rating')
                if not rating or not rating.get('code'):
                    missing_rating += 1
            
            print(f"Items with missing genre: {missing_genre}")
            print(f"Items with missing rating: {missing_rating}")
            print(f"Total items: {len(data)}")
            
            # Show a few examples of items with missing data
            if missing_genre > 0 or missing_rating > 0:
                print(f"\n⚠️  Examples of items with missing data:")
                for item in data:
                    genre = item.get('genre')
                    rating = item.get('rating')
                    
                    if (not genre or not genre.get('name')) or (not rating or not rating.get('code')):
                        print(f"  • {item.get('title', 'Unknown')}")
                        if not genre or not genre.get('name'):
                            print(f"    - Missing genre")
                        if not rating or not rating.get('code'):
                            print(f"    - Missing rating")
                        break  # Just show first example
            
        else:
            print(f"❌ Content error: {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    test_api_response() 