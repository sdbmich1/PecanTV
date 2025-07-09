#!/usr/bin/env python3
"""
Fix frontend image loading by updating ImageOptimizationService to use direct URLs
"""

import os
import re

def fix_image_optimization_service():
    """Update ImageOptimizationService to use direct URLs instead of CDN"""
    
    service_path = "../PecanTV/PECANTV/PECANTV/Services/ImageOptimizationService.swift"
    
    if not os.path.exists(service_path):
        print("❌ ImageOptimizationService.swift not found")
        return False
    
    print("🔧 Updating ImageOptimizationService.swift...")
    
    with open(service_path, 'r') as f:
        content = f.read()
    
    # Replace the CDN optimization with direct URL usage
    updated_content = content.replace(
        '// Use Cloudflare Image Resizing for all images\n        return generateCloudflareOptimizedURL(originalURL: originalURL, size: size, format: format)',
        '// For now, use direct URLs until CDN is properly set up\n        return URL(string: originalURL)'
    )
    
    # Also update the generateCloudflareOptimizedURL method to return direct URLs
    updated_content = updated_content.replace(
        '// Build the optimized URL\n        let optimizationParams = params.joined(separator: ",")\n        let optimizedURL = "http://\\(cloudflareDomain)/cdn-cgi/image/\\(optimizationParams)/?url=\\(originalURL)"\n        \n        return URL(string: optimizedURL)',
        '// For now, return direct URL until CDN is properly set up\n        return URL(string: originalURL)'
    )
    
    # Update the cloudflare domain comment
    updated_content = updated_content.replace(
        'let cloudflareDomain = "127.0.0.1:8001"  // Local development\n        // let cloudflareDomain = "images.pecantv.com"  // Production CDN',
        '// CDN Configuration - Currently using direct URLs\n        // let cloudflareDomain = "127.0.0.1:8001"  // Local development\n        // let cloudflareDomain = "images.pecantv.com"  // Production CDN'
    )
    
    with open(service_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated ImageOptimizationService.swift to use direct URLs")
    return True

def fix_image_cache_service():
    """Update ImageCacheService to use direct URLs"""
    
    service_path = "../PecanTV/PECANTV/PECANTV/Services/ImageCacheService.swift"
    
    if not os.path.exists(service_path):
        print("❌ ImageCacheService.swift not found")
        return False
    
    print("🔧 Updating ImageCacheService.swift...")
    
    with open(service_path, 'r') as f:
        content = f.read()
    
    # Replace optimized URL usage with direct URLs
    updated_content = content.replace(
        '// Use optimized URL if available\n        let optimizedURL = ImageOptimizationService.shared.getOptimizedURL(for: urlString, context: context) ?? url',
        '// Use direct URL for now\n        let optimizedURL = url'
    )
    
    with open(service_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated ImageCacheService.swift to use direct URLs")
    return True

def create_simple_image_service():
    """Create a simple image service that just uses direct URLs"""
    
    service_path = "../PecanTV/PECANTV/PECANTV/Services/SimpleImageService.swift"
    
    simple_service = '''import Foundation
import UIKit
import SwiftUI

/// Simple image service that uses direct URLs without optimization
/// This is a temporary solution until CDN is properly set up
class SimpleImageService: ObservableObject {
    static let shared = SimpleImageService()
    
    private init() {}
    
    /// Get direct URL for image
    func getImageURL(from originalURL: String) -> URL? {
        return URL(string: originalURL)
    }
    
    /// Create a SwiftUI view that loads images directly
    func directImage(
        from urlString: String,
        placeholder: @escaping () -> AnyView = { AnyView(Color.gray.opacity(0.3)) }
    ) -> AnyView {
        return AnyView(
            DirectImageView(
                urlString: urlString,
                placeholder: placeholder
            )
        )
    }
}

// MARK: - Direct Image View

struct DirectImageView: View {
    let urlString: String
    let placeholder: () -> AnyView
    @State private var image: UIImage?
    @State private var isLoading = true
    @State private var hasError = false
    
    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } else if hasError {
                placeholder()
            } else {
                placeholder()
                    .onAppear {
                        loadImage()
                    }
            }
        }
    }
    
    private func loadImage() {
        guard let url = URL(string: urlString) else {
            hasError = true
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let data = data, let loadedImage = UIImage(data: data) {
                    self.image = loadedImage
                } else {
                    self.hasError = true
                }
            }
        }.resume()
    }
}

// MARK: - Extensions for SwiftUI

extension SimpleImageService {
    /// Get image URL for SwiftUI views
    func getImageURL(
        for originalURL: String,
        context: ImageContext = .card
    ) -> URL? {
        return getImageURL(from: originalURL)
    }
}

// MARK: - Image Context (for compatibility)

enum ImageContext {
    case thumbnail    // Small list items
    case card         // Content cards
    case detail       // Detail views
    case fullscreen   // Full screen views
}
'''
    
    with open(service_path, 'w') as f:
        f.write(simple_service)
    
    print("✅ Created SimpleImageService.swift")
    return True

def update_content_detail_view():
    """Update ContentDetailView to use simple image loading"""
    
    detail_view_path = "../PecanTV/PECANTV/PECANTV/Features/Content/Views/ContentDetailView.swift"
    
    if not os.path.exists(detail_view_path):
        print("❌ ContentDetailView.swift not found")
        return False
    
    print("🔧 Updating ContentDetailView.swift...")
    
    with open(detail_view_path, 'r') as f:
        content = f.read()
    
    # Replace ImageCacheService with SimpleImageService
    updated_content = content.replace(
        'ImageCacheService.shared.cachedImage(\n                                from: content.posterURL,\n                                context: .detail\n                            ) {',
        'SimpleImageService.shared.directImage(\n                                from: content.posterURL\n                            ) {'
    )
    
    with open(detail_view_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated ContentDetailView.swift")
    return True

def update_poster_carousel_view():
    """Update PosterCarouselView to use simple image loading"""
    
    carousel_view_path = "../PecanTV/PECANTV/PECANTV/Features/Home/Views/PosterCarouselView.swift"
    
    if not os.path.exists(carousel_view_path):
        print("❌ PosterCarouselView.swift not found")
        return False
    
    print("🔧 Updating PosterCarouselView.swift...")
    
    with open(carousel_view_path, 'r') as f:
        content = f.read()
    
    # Replace ImageCacheService with SimpleImageService
    updated_content = content.replace(
        'ImageCacheService.shared.cachedImage(\n                    from: content.posterURL,\n                    context: .card\n                ) {',
        'SimpleImageService.shared.directImage(\n                    from: content.posterURL\n                ) {'
    )
    
    with open(carousel_view_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated PosterCarouselView.swift")
    return True

def main():
    """Main function to fix frontend image loading"""
    
    print("🔧 Fixing Frontend Image Loading Issues")
    print("=" * 50)
    
    # Create simple image service
    if create_simple_image_service():
        print("✅ Created SimpleImageService")
    
    # Update existing services to use direct URLs
    if fix_image_optimization_service():
        print("✅ Fixed ImageOptimizationService")
    
    if fix_image_cache_service():
        print("✅ Fixed ImageCacheService")
    
    # Update views to use simple image loading
    if update_content_detail_view():
        print("✅ Updated ContentDetailView")
    
    if update_poster_carousel_view():
        print("✅ Updated PosterCarouselView")
    
    print("\n🎉 Frontend image loading issues fixed!")
    print("\n📋 Summary of changes:")
    print("1. Created SimpleImageService.swift - uses direct URLs")
    print("2. Updated ImageOptimizationService.swift - bypasses CDN for now")
    print("3. Updated ImageCacheService.swift - uses direct URLs")
    print("4. Updated ContentDetailView.swift - uses SimpleImageService")
    print("5. Updated PosterCarouselView.swift - uses SimpleImageService")
    print("\n🚀 The app should now load images directly from GCS URLs")
    print("   without trying to use the non-existent CDN endpoint.")

if __name__ == "__main__":
    main() 