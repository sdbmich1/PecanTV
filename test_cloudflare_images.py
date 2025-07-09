#!/usr/bin/env python3
"""
Test Cloudflare image optimization
"""

import requests
import time
import json

def test_cloudflare_image_optimization():
    """Test Cloudflare image optimization with real image URLs"""
    
    print("🔍 Testing Cloudflare image optimization...\n")
    
    # Test URLs from the database
    test_images = [
        {
            "name": "Count of Monte Cristo Poster",
            "original": "https://storage.googleapis.com/pecantv_series/the_count_of_monte_cristo/count_of_monte_cristo/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png",
            "optimized": "https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85,fit=scale-down/https://storage.googleapis.com/pecantv_series/the_count_of_monte_cristo/count_of_monte_cristo/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png"
        },
        {
            "name": "Mike Hammer Poster",
            "original": "https://storage.googleapis.com/pecantv_series/mike_hammer/MikeHammer1_poster.jpg",
            "optimized": "https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85,fit=scale-down/https://storage.googleapis.com/pecantv_series/mike_hammer/MikeHammer1_poster.jpg"
        },
        {
            "name": "Petrocelli Poster",
            "original": "https://storage.googleapis.com/pecantv_series/petrocelli/petrocelli_poster.jpg",
            "optimized": "https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85,fit=scale-down/https://storage.googleapis.com/pecantv_series/petrocelli/petrocelli_poster.jpg"
        }
    ]
    
    for test in test_images:
        print(f"Testing: {test['name']}")
        
        # Test original URL
        try:
            start_time = time.time()
            response = requests.get(test['original'], timeout=10)
            original_time = time.time() - start_time
            original_size = len(response.content)
            print(f"  Original: {original_time:.2f}s, {original_size} bytes")
        except Exception as e:
            print(f"  Original: Error - {e}")
            continue
        
        # Test Cloudflare optimized URL
        try:
            start_time = time.time()
            response = requests.get(test['optimized'], timeout=10)
            optimized_time = time.time() - start_time
            optimized_size = len(response.content)
            print(f"  Cloudflare: {optimized_time:.2f}s, {optimized_size} bytes")
            
            if optimized_size < original_size:
                compression_ratio = (1 - optimized_size / original_size) * 100
                print(f"  ✅ Compression: {compression_ratio:.1f}% smaller")
            else:
                print(f"  ⚠️  No compression benefit")
                
            # Check if Cloudflare is working
            if "cloudflare" in response.headers.get("server", "").lower():
                print(f"  ✅ Served by Cloudflare")
            else:
                print(f"  ⚠️  Not served by Cloudflare")
                
        except Exception as e:
            print(f"  Cloudflare: Error - {e}")
        
        print()

def test_different_sizes():
    """Test different image sizes and formats"""
    
    print("🔍 Testing different image sizes and formats...\n")
    
    base_url = "https://storage.googleapis.com/pecantv_series/the_count_of_monte_cristo/count_of_monte_cristo/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png"
    
    # Test different sizes
    sizes = [
        ("thumbnail", "width=150,height=225"),
        ("small", "width=300,height=450"),
        ("medium", "width=600,height=900"),
        ("large", "width=1200,height=1800")
    ]
    
    formats = ["webp", "jpeg", "png"]
    
    for size_name, size_params in sizes:
        print(f"Size: {size_name}")
        for format in formats:
            optimized_url = f"https://images.pecantv.com/cdn-cgi/image/format={format},{size_params},quality=85,fit=scale-down/{base_url}"
            
            try:
                start_time = time.time()
                response = requests.get(optimized_url, timeout=10)
                load_time = time.time() - start_time
                file_size = len(response.content)
                
                print(f"  {format.upper()}: {load_time:.2f}s, {file_size} bytes")
            except Exception as e:
                print(f"  {format.upper()}: Error - {e}")
        
        print()

def test_cloudflare_status():
    """Test if Cloudflare domain is properly configured"""
    
    print("🔍 Testing Cloudflare domain configuration...\n")
    
    # Test basic domain
    try:
        response = requests.get("https://images.pecantv.com", timeout=10)
        print(f"Domain status: {response.status_code}")
        print(f"Server: {response.headers.get('server', 'Unknown')}")
    except Exception as e:
        print(f"Domain error: {e}")
    
    print()

if __name__ == "__main__":
    test_cloudflare_status()
    test_cloudflare_image_optimization()
    test_different_sizes() 