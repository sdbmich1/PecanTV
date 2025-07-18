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
        // For GCS URLs, use direct URLs for best performance
        // GCS already provides excellent global CDN performance
        return URL(string: originalURL)
    }
    
    /// Generate optimized URL using Cloudflare Image Resizing (for future use)
    private func generateCloudflareOptimizedURL(
        originalURL: String,
        size: ImageSize,
        format: ImageFormat
    ) -> URL? {
        // Cloudflare Image Resizing URL format:
        // https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85/https://original-url.com/image.jpg
        
        // CDN Configuration - Currently using GCS direct URLs
        // let cloudflareDomain = "images.pecantv.com"  // Future CDN option
        
        // For now, return direct GCS URL for best performance
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
    
    // MARK: - GCS-Specific Helpers
    
    /// Check if URL is from Google Cloud Storage
    func isGCSURL(_ url: String) -> Bool {
        return url.contains("storage.googleapis.com")
    }
    
    /// Get GCS bucket and path from URL
    func getGCSPath(from url: String) -> (bucket: String, path: String)? {
        guard isGCSURL(url) else { return nil }
        
        // Parse GCS URL: https://storage.googleapis.com/bucket-name/path/to/file
        let components = url.components(separatedBy: "storage.googleapis.com/")
        guard components.count > 1 else { return nil }
        
        let pathComponents = components[1].components(separatedBy: "/")
        guard pathComponents.count > 1 else { return nil }
        
        let bucket = pathComponents[0]
        let path = pathComponents.dropFirst().joined(separator: "/")
        
        return (bucket: bucket, path: path)
    }
    
    // MARK: - Performance Optimization
    
    /// Get optimal image size for device
    func getOptimalSize(for context: ImageContext, deviceScale: CGFloat = UIScreen.main.scale) -> ImageSize {
        switch context {
        case .thumbnail:
            return deviceScale > 2 ? .small : .thumbnail
        case .card:
            return deviceScale > 2 ? .medium : .small
        case .detail:
            return deviceScale > 2 ? .large : .medium
        case .fullscreen:
            return .large
        }
    }
    
    /// Get optimal format for device
    func getOptimalFormat() -> ImageFormat {
        // Use WebP for iOS 14+ (better compression)
        if #available(iOS 14.0, *) {
            return .webp
        } else {
            return .jpeg
        }
    }
} 