import Foundation
import UIKit
import SwiftUI

class ImageCacheService: ObservableObject {
    static let shared = ImageCacheService()
    
    // Cache configuration
    private let cache = NSCache<NSString, UIImage>()
    private let fileManager = FileManager.default
    private let cacheDirectory: URL
    private let maxCacheSize: Int = 100 * 1024 * 1024 // 100MB
    private let maxCacheAge: TimeInterval = 7 * 24 * 60 * 60 // 7 days
    
    // Performance tracking
    private var loadTimes: [String: TimeInterval] = [:]
    private var cacheHits: Int = 0
    private var cacheMisses: Int = 0
    
    private init() {
        // Set up cache directory
        let paths = fileManager.urls(for: .cachesDirectory, in: .userDomainMask)
        cacheDirectory = paths[0].appendingPathComponent("ImageCache")
        
        // Create cache directory if it doesn't exist
        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
        
        // Configure memory cache
        cache.countLimit = 100 // Max 100 images in memory
        cache.totalCostLimit = 50 * 1024 * 1024 // 50MB memory limit
        
        // Load cache statistics
        loadCacheStatistics()
        
        // Clean old cache files
        cleanOldCacheFiles()
    }
    
    // MARK: - Public Methods
    
    /// Load image with caching and optimization
    func loadImage(
        from urlString: String,
        context: ImageContext = .card,
        completion: @escaping (UIImage?) -> Void
    ) {
        let startTime = Date()
        
        // Check memory cache first
        if let cachedImage = getCachedImage(for: urlString) {
            cacheHits += 1
            trackPerformance(url: urlString, loadTime: Date().timeIntervalSince(startTime), success: true)
            completion(cachedImage)
            return
        }
        
        // Check disk cache
        if let diskImage = getDiskCachedImage(for: urlString) {
            cacheHits += 1
            // Store in memory cache
            setCachedImage(diskImage, for: urlString)
            trackPerformance(url: urlString, loadTime: Date().timeIntervalSince(startTime), success: true)
            completion(diskImage)
            return
        }
        
        cacheMisses += 1
        
        // Download and cache image
        downloadAndCacheImage(from: urlString, context: context) { [weak self] image in
            DispatchQueue.main.async {
                self?.trackPerformance(url: urlString, loadTime: Date().timeIntervalSince(startTime), success: image != nil)
                completion(image)
            }
        }
    }
    
    /// Preload images for better UX
    func preloadImages(from urls: [String], context: ImageContext = .card) {
        for url in urls {
            loadImage(from: url, context: context) { _ in
                // Silent preload
            }
        }
    }
    
    /// Clear all cached images
    func clearCache() {
        cache.removeAllObjects()
        
        do {
            let files = try fileManager.contentsOfDirectory(at: cacheDirectory, includingPropertiesForKeys: nil)
            for file in files {
                try fileManager.removeItem(at: file)
            }
            print("✅ Image cache cleared")
        } catch {
            print("❌ Error clearing cache: \(error)")
        }
    }
    
    /// Get cache statistics
    func getCacheStatistics() -> CacheStatistics {
        let diskSize = getDiskCacheSize()
        let memoryCount = cache.totalCostLimit
        let hitRate = cacheHits + cacheMisses > 0 ? Double(cacheHits) / Double(cacheHits + cacheMisses) : 0
        
        return CacheStatistics(
            memoryCount: Int(memoryCount),
            diskSize: diskSize,
            hitRate: hitRate,
            totalRequests: cacheHits + cacheMisses
        )
    }
    
    // MARK: - Private Methods
    
    private func getCachedImage(for urlString: String) -> UIImage? {
        let key = NSString(string: urlString)
        return cache.object(forKey: key)
    }
    
    private func setCachedImage(_ image: UIImage, for urlString: String) {
        let key = NSString(string: urlString)
        cache.setObject(image, forKey: key)
    }
    
    private func getDiskCachedImage(for urlString: String) -> UIImage? {
        let filename = getCacheFilename(for: urlString)
        let fileURL = cacheDirectory.appendingPathComponent(filename)
        
        guard fileManager.fileExists(atPath: fileURL.path) else { return nil }
        
        // Check if file is too old
        if let attributes = try? fileManager.attributesOfItem(atPath: fileURL.path),
           let creationDate = attributes[.creationDate] as? Date,
           Date().timeIntervalSince(creationDate) > maxCacheAge {
            try? fileManager.removeItem(at: fileURL)
            return nil
        }
        
        return UIImage(contentsOfFile: fileURL.path)
    }
    
    private func downloadAndCacheImage(
        from urlString: String,
        context: ImageContext,
        completion: @escaping (UIImage?) -> Void
    ) {
        guard let url = URL(string: urlString) else {
            completion(nil)
            return
        }
        
        // Use direct URL for now
        let optimizedURL = url
        
        URLSession.shared.dataTask(with: optimizedURL) { [weak self] data, response, error in
            guard let self = self,
                  let data = data,
                  let image = UIImage(data: data) else {
                DispatchQueue.main.async {
                    completion(nil)
                }
                return
            }
            
            // Cache the image
            self.setCachedImage(image, for: urlString)
            self.saveImageToDisk(image, for: urlString)
            
            DispatchQueue.main.async {
                completion(image)
            }
        }.resume()
    }
    
    private func saveImageToDisk(_ image: UIImage, for urlString: String) {
        let filename = getCacheFilename(for: urlString)
        let fileURL = cacheDirectory.appendingPathComponent(filename)
        
        // Convert to JPEG for smaller file size
        if let data = image.jpegData(compressionQuality: 0.8) {
            try? data.write(to: fileURL)
        }
    }
    
    private func getCacheFilename(for urlString: String) -> String {
        // Create a hash of the URL for the filename
        let hash = urlString.data(using: .utf8)?.base64EncodedString() ?? urlString
        return hash.replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "=", with: "")
    }
    
    private func getDiskCacheSize() -> Int {
        do {
            let files = try fileManager.contentsOfDirectory(at: cacheDirectory, includingPropertiesForKeys: [.fileSizeKey])
            return files.reduce(0) { total, file in
                let size = (try? file.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
                return total + size
            }
        } catch {
            return 0
        }
    }
    
    private func cleanOldCacheFiles() {
        do {
            let files = try fileManager.contentsOfDirectory(at: cacheDirectory, includingPropertiesForKeys: [.creationDateKey])
            let now = Date()
            
            for file in files {
                if let creationDate = try? file.resourceValues(forKeys: [.creationDateKey]).creationDate,
                   now.timeIntervalSince(creationDate) > maxCacheAge {
                    try? fileManager.removeItem(at: file)
                }
            }
        } catch {
            print("❌ Error cleaning cache: \(error)")
        }
    }
    
    private func loadCacheStatistics() {
        // Load from UserDefaults or other persistent storage
        cacheHits = UserDefaults.standard.integer(forKey: "ImageCacheHits")
        cacheMisses = UserDefaults.standard.integer(forKey: "ImageCacheMisses")
    }
    
    private func trackPerformance(url: String, loadTime: TimeInterval, success: Bool) {
        loadTimes[url] = loadTime
        
        // Save statistics periodically
        if (cacheHits + cacheMisses) % 10 == 0 {
            UserDefaults.standard.set(cacheHits, forKey: "ImageCacheHits")
            UserDefaults.standard.set(cacheMisses, forKey: "ImageCacheMisses")
        }
    }
}

// MARK: - Cache Statistics

struct CacheStatistics {
    let memoryCount: Int
    let diskSize: Int
    let hitRate: Double
    let totalRequests: Int
    
    var diskSizeMB: Double {
        return Double(diskSize) / (1024 * 1024)
    }
    
    var hitRatePercentage: Double {
        return hitRate * 100
    }
}

// MARK: - SwiftUI Extensions

extension ImageCacheService {
    /// Create a SwiftUI view that loads and caches images
    func cachedImage(
        from urlString: String,
        context: ImageContext = .card,
        placeholder: @escaping () -> AnyView = { AnyView(Color.gray.opacity(0.3)) }
    ) -> AnyView {
        return AnyView(
            CachedImageView(
                urlString: urlString,
                context: context,
                placeholder: placeholder
            )
        )
    }
}

// MARK: - Cached Image View

struct CachedImageView: View {
    let urlString: String
    let context: ImageContext
    let placeholder: () -> AnyView
    
    @StateObject private var cacheService = ImageCacheService.shared
    @State private var image: UIImage?
    @State private var isLoading = true
    @State private var loadError = false
    
    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } else if isLoading {
                placeholder()
                    .overlay(
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .gray))
                            .scaleEffect(0.8)
                    )
            } else if loadError {
                placeholder()
                    .overlay(
                        Image(systemName: "photo")
                            .font(.system(size: 24))
                            .foregroundColor(.gray)
                    )
            } else {
                placeholder()
            }
        }
        .onAppear {
            loadImage()
        }
    }
    
    private func loadImage() {
        guard image == nil else { return }
        
        isLoading = true
        loadError = false
        
        cacheService.loadImage(from: urlString, context: context) { loadedImage in
            isLoading = false
            if let loadedImage = loadedImage {
                image = loadedImage
            } else {
                loadError = true
            }
        }
    }
} 