import Foundation
import UIKit

class ImageOptimizationService: ObservableObject {
    static let shared = ImageOptimizationService()
    
    // Image size presets for different use cases
    enum ImageSize: String, CaseIterable {
        case thumbnail = "thumbnail"      // 150x225 for lists
        case small = "small"              // 300x450 for cards
        case medium = "medium"            // 600x900 for detail views
        case large = "large"              // 1200x1800 for full screen
        case original = "original"        // Original size
        
        var dimensions: (width: Int, height: Int) {
            switch self {
            case .thumbnail: return (150, 225)
            case .small: return (300, 450)
            case .medium: return (600, 900)
            case .large: return (1200, 1800)
            case .original: return (0, 0) // Original size
            }
        }
        
        var quality: Int {
            switch self {
            case .thumbnail: return 70
            case .small: return 80
            case .medium: return 85
            case .large: return 90
            case .original: return 95
            }
        }
    }
    
    // Image format options
    enum ImageFormat: String, CaseIterable {
        case webp = "webp"    // Best compression
        case jpeg = "jpeg"    // Widest compatibility
        case png = "png"      // For transparency
    }
    
    private init() {}
    
    // MARK: - URL Generation
    
    /// Generate optimized image URL for a given size and format
    func getOptimizedImageURL(
        originalURL: String,
        size: ImageSize = .medium,
        format: ImageFormat = .webp
    ) -> URL? {
        // For now, use direct URLs until CDN is properly set up
        return URL(string: originalURL)
    }
    
    /// Generate optimized URL using Cloudflare Image Resizing
    private func generateCloudflareOptimizedURL(
        originalURL: String,
        size: ImageSize,
        format: ImageFormat
    ) -> URL? {
        // Cloudflare Image Resizing URL format:
        // https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85/https://original-url.com/image.jpg
        
        // CDN Configuration - Update this when CDN is set up
        // CDN Configuration - Currently using direct URLs
        // let cloudflareDomain = "127.0.0.1:8001"  // Local development
        // let cloudflareDomain = "images.pecantv.com"  // Production CDN
        
        // Build optimization parameters
        var params: [String] = []
        
        // Add format
        params.append("format=\(format.rawValue)")
        
        // Add size if not original
        if size != .original {
            params.append("width=\(size.dimensions.width)")
            if size.dimensions.height > 0 {
                params.append("height=\(size.dimensions.height)")
            }
        }
        
        // Add quality
        params.append("quality=\(size.quality)")
        
        // Add fit mode for better results
        params.append("fit=scale-down")
        
        // For now, return direct URL until CDN is properly set up
        return URL(string: originalURL)
    }
    
    // MARK: - Size-Specific URL Helpers
    
    /// Get thumbnail URL for list views
    func getThumbnailURL(from originalURL: String) -> URL? {
        return getOptimizedImageURL(originalURL: originalURL, size: .thumbnail)
    }
    
    /// Get small URL for card views
    func getSmallURL(from originalURL: String) -> URL? {
        return getOptimizedImageURL(originalURL: originalURL, size: .small)
    }
    
    /// Get medium URL for detail views
    func getMediumURL(from originalURL: String) -> URL? {
        return getOptimizedImageURL(originalURL: originalURL, size: .medium)
    }
    
    /// Get large URL for full-screen views
    func getLargeURL(from originalURL: String) -> URL? {
        return getOptimizedImageURL(originalURL: originalURL, size: .large)
    }
    
    // MARK: - Format Detection
    
    /// Detect best format based on image content and device capabilities
    func getBestFormat(for imageURL: String) -> ImageFormat {
        // Check if device supports WebP
        if supportsWebP() {
            return .webp
        }
        
        // Check if image has transparency (PNG)
        if imageURL.lowercased().contains(".png") {
            return .png
        }
        
        // Default to JPEG
        return .jpeg
    }
    
    /// Check if device supports WebP
    private func supportsWebP() -> Bool {
        // iOS 14+ supports WebP natively
        if #available(iOS 14.0, *) {
            return true
        }
        return false
    }
    
    // MARK: - Performance Monitoring
    
    /// Track image load performance
    func trackImageLoad(url: String, loadTime: TimeInterval, success: Bool) {
        // In production, you might want to send this to analytics
        print("📊 Image Load: \(url)")
        print("   Time: \(String(format: "%.2f", loadTime))s")
        print("   Success: \(success)")
    }
    
    // MARK: - Fallback Handling
    
    /// Get fallback URL if optimization fails
    func getFallbackURL(from originalURL: String) -> URL? {
        // Return original URL as fallback
        return URL(string: originalURL)
    }
    
    /// Check if URL is optimizable
    func isOptimizable(_ url: String) -> Bool {
        return url.contains("storage.googleapis.com") || 
               url.contains("dropbox.com") ||
               url.contains("your-cdn.com")
    }
}

// MARK: - Extensions for SwiftUI

extension ImageOptimizationService {
    /// Get optimized URL for SwiftUI views
    func getOptimizedURL(
        for originalURL: String,
        context: ImageContext = .card
    ) -> URL? {
        let size: ImageSize
        let format = getBestFormat(for: originalURL)
        
        switch context {
        case .thumbnail:
            size = .thumbnail
        case .card:
            size = .small
        case .detail:
            size = .medium
        case .fullscreen:
            size = .large
        }
        
        return getOptimizedImageURL(originalURL: originalURL, size: size, format: format)
    }
} 