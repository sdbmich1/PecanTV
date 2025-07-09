#!/usr/bin/env python3
"""
Test script to verify image performance improvements
"""

import requests
import time
import json

def test_image_performance():
    """Test image loading performance"""
    
    print("🔍 Testing image performance improvements...\n")
    
    # Test URLs from the database
    test_urls = [
        "https://storage.googleapis.com/pecantv_series/the_count_of_monte_cristo/count_of_monte_cristo/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png",
        "https://storage.googleapis.com/pecantv_series/mike_hammer/MikeHammer1_poster.jpg",
        "https://storage.googleapis.com/pecantv_series/petrocelli/petrocelli_poster.jpg"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"Test {i}: {url}")
        
        # Test original URL
        start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            original_time = time.time() - start_time
            original_size = len(response.content)
            print(f"  Original: {original_time:.2f}s, {original_size} bytes")
        except Exception as e:
            print(f"  Original: Error - {e}")
            continue
        
        # Test with optimization parameters
        optimized_url = f"{url}?size=medium&format=webp&quality=85"
        start_time = time.time()
        try:
            response = requests.get(optimized_url, timeout=10)
            optimized_time = time.time() - start_time
            optimized_size = len(response.content)
            print(f"  Optimized: {optimized_time:.2f}s, {optimized_size} bytes")
            
            if optimized_size < original_size:
                compression_ratio = (1 - optimized_size / original_size) * 100
                print(f"  ✅ Compression: {compression_ratio:.1f}% smaller")
            else:
                print(f"  ⚠️  No compression benefit")
                
        except Exception as e:
            print(f"  Optimized: Error - {e}")
        
        print()

def test_api_endpoints():
    """Test API endpoints for content and episodes"""
    
    print("🔍 Testing API endpoints...\n")
    
    base_url = "http://localhost:8000"
    
    # Test content endpoint
    print("1. Testing content endpoint:")
    try:
        response = requests.get(f"{base_url}/content")
        if response.status_code == 200:
            content = response.json()
            films = [c for c in content if c['type'] == 'FILM']
            series = [c for c in content if c['type'] == 'SERIES']
            print(f"   ✅ Content loaded: {len(content)} total, {len(films)} films, {len(series)} series")
            
            # Check for specific content
            monte_cristo = [c for c in content if 'Monte Cristo' in c['title']]
            mike_hammer = [c for c in content if 'Mike Hammer' in c['title']]
            christie_love = [c for c in content if 'Christie Love' in c['title']]
            
            print(f"   📺 Monte Cristo: {len(monte_cristo)} found")
            print(f"   📺 Mike Hammer: {len(mike_hammer)} found")
            print(f"   📺 Christie Love: {len(christie_love)} found")
        else:
            print(f"   ❌ Content endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Content endpoint error: {e}")
    
    print()
    
    # Test episodes endpoint for Count of Monte Cristo
    print("2. Testing episodes endpoint for Count of Monte Cristo:")
    try:
        response = requests.get(f"{base_url}/series/72/episodes")
        if response.status_code == 200:
            episodes = response.json()
            print(f"   ✅ Episodes loaded: {len(episodes)} episodes")
            
            # Check first few episodes
            for i, episode in enumerate(episodes[:3]):
                print(f"   📺 Episode {i+1}: {episode['title']} (S{episode['seasonNumber']}E{episode['episodeNumber']})")
        else:
            print(f"   ❌ Episodes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Episodes endpoint error: {e}")
    
    print()
    
    # Test episodes endpoint for Mike Hammer
    print("3. Testing episodes endpoint for Mike Hammer:")
    try:
        response = requests.get(f"{base_url}/series/45/episodes")
        if response.status_code == 200:
            episodes = response.json()
            print(f"   ✅ Episodes loaded: {len(episodes)} episodes")
            
            # Check first few episodes
            for i, episode in enumerate(episodes[:3]):
                print(f"   📺 Episode {i+1}: {episode['title']} (S{episode['seasonNumber']}E{episode['episodeNumber']})")
        else:
            print(f"   ❌ Episodes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Episodes endpoint error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    print("\n" + "="*50 + "\n")
    test_image_performance() 