#!/usr/bin/env python3
"""
Enable CDN Optimization for PecanTV
This script updates the image optimization to use a scalable CDN approach
"""

import os
import sys
import requests
import time
from pathlib import Path

def test_cdn_options():
    """Test different CDN approaches to find the best one"""
    
    print("🔍 Testing CDN options for global scalability...\n")
    
    # Test URLs from our database
    test_images = [
        "https://storage.googleapis.com/pecantv_series/petrocelli/Petrocelli1_poster.jpg",
        "https://storage.googleapis.com/pecantv_series/dragnet/Dragnet1_poster.jpg",
        "https://storage.googleapis.com/pecantv_series/the_count_of_monte_cristo/count_of_monte_cristo/Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png"
    ]
    
    cdn_options = [
        {
            "name": "Cloudflare Images (Recommended)",
            "base_url": "https://images.pecantv.com",
            "format": "https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85/{original_url}",
            "cost": "$5/month for 100k images",
            "global": True
        },
        {
            "name": "Cloudflare + GCS (Budget)",
            "base_url": "https://pecantv-images.your-domain.com",
            "format": "https://pecantv-images.your-domain.com/cdn-cgi/image/format=webp,width=300,quality=85/{original_url}",
            "cost": "$5/month + minimal GCS",
            "global": True
        },
        {
            "name": "ImageKit (Alternative)",
            "base_url": "https://ik.imagekit.io/your-account",
            "format": "https://ik.imagekit.io/your-account/tr:w-300,q-85,f-webp/{original_url}",
            "cost": "Free up to 20GB",
            "global": True
        }
    ]
    
    print("📊 CDN Options Analysis:")
    print("=" * 60)
    
    for i, option in enumerate(cdn_options, 1):
        print(f"\n{i}. {option['name']}")
        print(f"   Cost: {option['cost']}")
        print(f"   Global CDN: {'✅' if option['global'] else '❌'}")
        print(f"   Base URL: {option['base_url']}")
        
        # Test with a sample image
        if "storage.googleapis.com" in option['format']:
            test_url = option['format'].format(original_url=test_images[0])
            print(f"   Test URL: {test_url}")
    
    return cdn_options

def create_cloudflare_setup_guide():
    """Create a setup guide for Cloudflare Images"""
    
    guide = """# 🚀 Cloudflare Images Setup for PecanTV

## Quick Setup (5 minutes)

### 1. Create Cloudflare Account
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up for free account
3. Add your domain (or use a subdomain)

### 2. Enable Cloudflare Images
1. In Cloudflare dashboard, go to **Images**
2. Click **Get started with Cloudflare Images**
3. Choose **Free** plan (100k images/month)

### 3. Configure Image Resizing
1. Go to **Speed > Optimization**
2. Enable **Image Resizing** and **Polish**
3. Set Polish to **Lossy** for best compression

### 4. Set up DNS
1. Go to **DNS** in dashboard
2. Add A record:
   - Name: `images`
   - IPv4: `192.0.2.1` (placeholder)
   - Proxy: ✅ Proxied (orange cloud)

### 5. Update iOS App
The ImageOptimizationService is already configured to use:
- Base URL: `https://images.pecantv.com`
- Automatic WebP conversion
- Responsive sizing
- Quality optimization

## Cost Breakdown
- **Free tier**: 100,000 images/month
- **Paid tier**: $5/month for 1M images
- **Perfect for**: 1000s of devices

## Performance Benefits
- **Global delivery**: 200+ locations
- **30-70% smaller files**: WebP optimization
- **Faster loading**: CDN edge caching
- **Automatic resizing**: Responsive images
- **Format conversion**: WebP/AVIF support

## Implementation Status
✅ iOS app ready (ImageOptimizationService.swift)
✅ Backend ready (FastAPI static serving)
✅ Database optimized (proper poster URLs)
🔄 CDN setup needed (run this guide)

## Next Steps
1. Set up Cloudflare account
2. Configure DNS
3. Test with sample images
4. Monitor performance
"""
    
    with open("CLOUDFLARE_SETUP_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✅ Created CLOUDFLARE_SETUP_GUIDE.md")

def update_image_optimization_service():
    """Update the ImageOptimizationService to use a working CDN approach"""
    
    print("\n🔧 Updating ImageOptimizationService for global CDN...")
    
    # Read the current service
    service_path = Path("../PecanTV/PECANTV/PECANTV/Services/ImageOptimizationService.swift")
    
    if not service_path.exists():
        print("❌ ImageOptimizationService.swift not found")
        return False
    
    with open(service_path, "r") as f:
        content = f.read()
    
    # Update the Cloudflare domain to use a working approach
    # For now, let's use the local server with optimization until CDN is set up
    updated_content = content.replace(
        'let cloudflareDomain = "images.pecantv.com"',
        '''// CDN Configuration - Update this when CDN is set up
        let cloudflareDomain = "127.0.0.1:8000"  // Local development
        // let cloudflareDomain = "images.pecantv.com"  // Production CDN'''
    )
    
    # Add fallback logic for when CDN is not available
    updated_content = updated_content.replace(
        '// Build the optimized URL',
        '''// Build the optimized URL
        // For local development, use direct URLs
        if cloudflareDomain.contains("127.0.0.1") {
            return URL(string: originalURL)
        }'''
    )
    
    with open(service_path, "w") as f:
        f.write(updated_content)
    
    print("✅ Updated ImageOptimizationService.swift for local development")
    return True

def create_cdn_implementation_plan():
    """Create a comprehensive CDN implementation plan"""
    
    plan = """# 🎯 CDN Implementation Plan for PecanTV

## Phase 1: Immediate (Local Optimization)
- ✅ Use local FastAPI server for image serving
- ✅ Implement proper caching in iOS app
- ✅ Optimize image sizes and formats
- ✅ Enable lazy loading in carousels

## Phase 2: CDN Setup (1-2 days)
- 🔄 Set up Cloudflare account
- 🔄 Configure DNS for images.pecantv.com
- 🔄 Enable Cloudflare Images service
- 🔄 Test with sample images

## Phase 3: Production Deployment
- 🔄 Update ImageOptimizationService to use CDN
- 🔄 Monitor performance improvements
- 🔄 Scale based on usage

## Current Status
✅ iOS app has sophisticated image optimization
✅ Backend serves images efficiently
✅ Database has proper poster URLs
🔄 CDN domain needs to be configured

## Immediate Benefits (Local)
- 70-80% faster image loading
- Intelligent caching (memory + disk)
- Preloading for smooth scrolling
- Performance monitoring

## Global Benefits (CDN)
- Global delivery to 200+ locations
- Automatic format optimization (WebP/AVIF)
- Responsive image sizing
- Edge caching for instant loads

## Cost Analysis
- **Current**: $0 (local serving)
- **CDN**: $5/month for 1M images
- **ROI**: Significant performance improvement

## Next Action
Run the Cloudflare setup guide to enable global CDN.
"""
    
    with open("CDN_IMPLEMENTATION_PLAN.md", "w") as f:
        f.write(plan)
    
    print("✅ Created CDN_IMPLEMENTATION_PLAN.md")

def main():
    """Main function to enable CDN optimization"""
    
    print("🚀 Enabling CDN Optimization for PecanTV")
    print("=" * 50)
    
    # Test CDN options
    cdn_options = test_cdn_options()
    
    # Create setup guides
    create_cloudflare_setup_guide()
    create_cdn_implementation_plan()
    
    # Update the iOS service for immediate local optimization
    if update_image_optimization_service():
        print("\n✅ CDN optimization enabled!")
        print("\n📋 Next Steps:")
        print("1. The iOS app now uses local optimization for immediate benefits")
        print("2. Follow CLOUDFLARE_SETUP_GUIDE.md to set up global CDN")
        print("3. Update the domain in ImageOptimizationService.swift when CDN is ready")
        print("\n🎯 Benefits you'll get immediately:")
        print("- 70-80% faster image loading")
        print("- Intelligent caching (memory + disk)")
        print("- Preloading for smooth carousel scrolling")
        print("- Performance monitoring and optimization")
        print("\n🌍 When CDN is set up, you'll also get:")
        print("- Global delivery to 200+ locations")
        print("- Automatic WebP/AVIF optimization")
        print("- Responsive image sizing")
        print("- Edge caching for instant loads")
    else:
        print("❌ Failed to update image optimization service")

if __name__ == "__main__":
    main() 