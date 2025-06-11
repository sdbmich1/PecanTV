import Foundation
import SwiftUI

class ImageCacheService {
    static let shared = ImageCacheService()
    private let cache = NSCache<NSString, UIImage>()
    private let fileManager = FileManager.default
    private let cacheDirectory: URL
    
    private init() {
        // Get the cache directory
        let cacheDirectory = fileManager.urls(for: .cachesDirectory, in: .userDomainMask)[0]
        self.cacheDirectory = cacheDirectory.appendingPathComponent("ImageCache")
        
        // Create cache directory if it doesn't exist
        try? fileManager.createDirectory(at: self.cacheDirectory, withIntermediateDirectories: true)
    }
    
    func getImage(for url: URL) async throws -> UIImage {
        // Check memory cache first
        if let cachedImage = cache.object(forKey: url.absoluteString as NSString) {
            return cachedImage
        }
        
        // Check disk cache
        let fileURL = cacheDirectory.appendingPathComponent(url.lastPathComponent)
        if let data = try? Data(contentsOf: fileURL),
           let image = UIImage(data: data) {
            // Store in memory cache
            cache.setObject(image, forKey: url.absoluteString as NSString)
            return image
        }
        
        do {
            // Download and cache the image
            let (data, response) = try await URLSession.shared.data(from: url)
            
            // Verify we got a valid response
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                throw NSError(domain: "ImageCacheService", code: -2, userInfo: [NSLocalizedDescriptionKey: "Invalid server response"])
            }
            
            // Verify we got valid image data
            guard let image = UIImage(data: data) else {
                throw NSError(domain: "ImageCacheService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid image data"])
            }
            
            // Store in memory cache
            cache.setObject(image, forKey: url.absoluteString as NSString)
            
            // Store in disk cache
            try? data.write(to: fileURL)
            
            return image
        } catch {
            // If download fails, return a placeholder image
            let placeholderImage = UIImage(systemName: "photo") ?? UIImage()
            cache.setObject(placeholderImage, forKey: url.absoluteString as NSString)
            return placeholderImage
        }
    }
    
    func clearCache() {
        cache.removeAllObjects()
        try? fileManager.removeItem(at: cacheDirectory)
        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
    }
} 