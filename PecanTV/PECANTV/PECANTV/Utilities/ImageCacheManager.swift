import SwiftUI
import Foundation

class ImageCacheManager: ObservableObject {
    static let shared = ImageCacheManager()
    
    private let cache = NSCache<NSString, UIImage>()
    private let fileManager = FileManager.default
    private let cacheDirectory: URL
    
    private init() {
        // Set cache limits
        cache.countLimit = 100 // Maximum number of images
        cache.totalCostLimit = 50 * 1024 * 1024 // 50 MB limit
        
        // Create cache directory
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        cacheDirectory = documentsPath.appendingPathComponent("ImageCache")
        
        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
    }
    
    // MARK: - Public Methods
    
    func getImage(from urlString: String) async -> UIImage? {
        let key = NSString(string: urlString)
        
        // Check memory cache first
        if let cachedImage = cache.object(forKey: key) {
            return cachedImage
        }
        
        // Check disk cache
        if let diskCachedImage = loadFromDisk(urlString: urlString) {
            cache.setObject(diskCachedImage, forKey: key)
            return diskCachedImage
        }
        
        // Download and cache
        guard let url = URL(string: urlString) else { return nil }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            guard let image = UIImage(data: data) else { return nil }
            
            // Save to memory and disk cache
            cache.setObject(image, forKey: key)
            saveToDisk(image: image, urlString: urlString)
            
            return image
        } catch {
            print("Error downloading image: \(error)")
            return nil
        }
    }
    
    func preloadImages(from urls: [String]) {
        Task {
            await withTaskGroup(of: Void.self) { group in
                for url in urls {
                    group.addTask {
                        _ = await self.getImage(from: url)
                    }
                }
            }
        }
    }
    
    func clearCache() {
        cache.removeAllObjects()
        clearDiskCache()
    }
    
    // MARK: - Private Methods
    
    private func saveToDisk(image: UIImage, urlString: String) {
        guard let data = image.jpegData(compressionQuality: 0.8) else { return }
        
        let filename = urlString.addingPercentEncoding(withAllowedCharacters: .urlHostAllowed) ?? urlString
        let fileURL = cacheDirectory.appendingPathComponent(filename)
        
        try? data.write(to: fileURL)
    }
    
    private func loadFromDisk(urlString: String) -> UIImage? {
        let filename = urlString.addingPercentEncoding(withAllowedCharacters: .urlHostAllowed) ?? urlString
        let fileURL = cacheDirectory.appendingPathComponent(filename)
        
        guard let data = try? Data(contentsOf: fileURL) else { return nil }
        return UIImage(data: data)
    }
    
    private func clearDiskCache() {
        do {
            let contents = try fileManager.contentsOfDirectory(at: cacheDirectory, includingPropertiesForKeys: nil)
            for fileURL in contents {
                try fileManager.removeItem(at: fileURL)
            }
        } catch {
            print("Error clearing disk cache: \(error)")
        }
    }
} 