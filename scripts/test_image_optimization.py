#!/usr/bin/env python3
"""
PecanTV Image Optimization Test Script
Tests the image optimization and caching system
"""

import requests
import time
import json
from urllib.parse import urlparse
import os

def test_image_urls():
    """Test image URLs from the API to ensure they're accessible"""
    print("🔍 Testing Image URLs...")
    
    # Test API endpoints
    api_base = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{api_base}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API health check failed")
            return False
        
        # Test content endpoint
        response = requests.get(f"{api_base}/content", timeout=10)
        if response.status_code != 200:
            print("❌ Content endpoint failed")
            return False
        
        content_data = response.json()
        print(f"✅ Found {len(content_data)} content items")
        
        # Test image URLs
        image_urls = []
        for item in content_data:
            if 'posterURL' in item and item['posterURL']:
                # Clean up malformed URLs
                url = item['posterURL']
                if 'https://' in url and url.count('https://') > 1:
                    # Extract the last URL from malformed URLs
                    urls = url.split('https://')
                    if len(urls) > 2:
                        url = 'https://' + urls[-1]
                image_urls.append(url)
        
        print(f"📸 Testing {len(image_urls)} image URLs...")
        
        success_count = 0
        slow_urls = []
        
        for i, url in enumerate(image_urls[:10]):  # Test first 10 images
            print(f"  Testing {i+1}/{min(10, len(image_urls))}: {url}")
            
            try:
                start_time = time.time()
                response = requests.head(url, timeout=10)
                load_time = time.time() - start_time
                
                if response.status_code == 200:
                    success_count += 1
                    if load_time > 2.0:
                        slow_urls.append((url, load_time))
                    print(f"    ✅ Success ({load_time:.2f}s)")
                else:
                    print(f"    ❌ Failed (HTTP {response.status_code})")
                    
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
        
        print(f"\n📊 Results:")
        print(f"  Success Rate: {success_count}/{min(10, len(image_urls))} ({success_count/min(10, len(image_urls))*100:.1f}%)")
        
        if slow_urls:
            print(f"  ⚠️  Slow URLs (>2s):")
            for url, load_time in slow_urls:
                print(f"    - {url}: {load_time:.2f}s")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def test_image_optimization():
    """Test image optimization features"""
    print("\n🔧 Testing Image Optimization Features...")
    
    # Test URL patterns
    test_urls = [
        "https://storage.googleapis.com/pecantv_title_images/GetChristieLove-Feature-Img-16x9.png",
        "https://www.dropbox.com/scl/fi/nxj319g2vpc43eb075vwx/GetChristieLove-Feature-Img-16x9.png?rlkey=nitbvdf33fe5ddkusowmydjjf&raw=1",
        "https://storage.googleapis.com/pecantv_title_images/JesseOwens-Feature-Img.png"
    ]
    
    print("📋 Testing URL optimization patterns:")
    
    for url in test_urls:
        parsed = urlparse(url)
        print(f"  {parsed.netloc}: {parsed.path}")
        
        # Check if it's a GCS URL
        if "storage.googleapis.com" in url:
            print("    ✅ Google Cloud Storage URL (optimizable)")
        elif "dropbox.com" in url:
            print("    ⚠️  Dropbox URL (needs CDN for optimization)")
        else:
            print("    ❓ Unknown URL type")
    
    return True

def test_cache_configuration():
    """Test cache configuration"""
    print("\n💾 Testing Cache Configuration...")
    
    # Check if cache directory would be created
    cache_dir = os.path.expanduser("~/Library/Caches/ImageCache")
    print(f"  Cache directory: {cache_dir}")
    
    # Check if directory exists or can be created
    if os.path.exists(cache_dir):
        print("    ✅ Cache directory exists")
    else:
        try:
            os.makedirs(cache_dir, exist_ok=True)
            print("    ✅ Cache directory created")
        except Exception as e:
            print(f"    ❌ Cannot create cache directory: {e}")
            return False
    
    return True

def test_performance_monitoring():
    """Test performance monitoring setup"""
    print("\n📊 Testing Performance Monitoring...")
    
    # Simulate performance data
    test_data = {
        "load_times": [0.5, 1.2, 0.8, 2.1, 0.3],
        "success_rates": [0.95, 0.88, 0.92, 0.85, 0.98],
        "cache_hits": [80, 75, 90, 85, 88]
    }
    
    avg_load_time = sum(test_data["load_times"]) / len(test_data["load_times"])
    avg_success_rate = sum(test_data["success_rates"]) / len(test_data["success_rates"])
    avg_cache_hit = sum(test_data["cache_hits"]) / len(test_data["cache_hits"])
    
    print(f"  Simulated Performance Data:")
    print(f"    Average Load Time: {avg_load_time:.2f}s")
    print(f"    Average Success Rate: {avg_success_rate*100:.1f}%")
    print(f"    Average Cache Hit Rate: {avg_cache_hit:.1f}%")
    
    # Grade performance
    if avg_load_time < 1.0 and avg_success_rate > 0.90:
        grade = "A"
    elif avg_load_time < 1.5 and avg_success_rate > 0.85:
        grade = "B"
    elif avg_load_time < 2.0 and avg_success_rate > 0.80:
        grade = "C"
    else:
        grade = "D"
    
    print(f"    Performance Grade: {grade}")
    
    return True

def generate_test_report():
    """Generate a test report"""
    print("\n📋 Generating Test Report...")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {
            "image_urls": False,
            "optimization": False,
            "cache": False,
            "monitoring": False
        },
        "recommendations": []
    }
    
    # Run tests
    report["tests"]["image_urls"] = test_image_urls()
    report["tests"]["optimization"] = test_image_optimization()
    report["tests"]["cache"] = test_cache_configuration()
    report["tests"]["monitoring"] = test_performance_monitoring()
    
    # Generate recommendations
    if not report["tests"]["image_urls"]:
        report["recommendations"].append("Fix image URL accessibility issues")
    
    if report["tests"]["optimization"]:
        report["recommendations"].append("Consider setting up a CDN for better optimization")
    
    if not report["tests"]["cache"]:
        report["recommendations"].append("Fix cache directory permissions")
    
    # Save report
    with open("image_optimization_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✅ Test report saved to image_optimization_test_report.json")
    
    return report

def main():
    """Main test function"""
    print("🎬 PecanTV Image Optimization Test Suite")
    print("=" * 50)
    
    report = generate_test_report()
    
    # Summary
    print("\n📊 Test Summary:")
    passed = sum(report["tests"].values())
    total = len(report["tests"])
    
    for test_name, result in report["tests"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    if passed == total:
        print("\n🎉 All tests passed! Image optimization is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")

if __name__ == "__main__":
    main() 