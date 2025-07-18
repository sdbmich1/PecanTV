import Foundation
import UIKit
import SwiftUI

/// Optimized image service with caching and lazy loading
class SimpleImageService: ObservableObject {
    static let shared = SimpleImageService()
    
    private let imageCache = NSCache<NSString, UIImage>()
    private var loadingTasks: [String: Task<UIImage?, Error>] = [:]
    private let queue = DispatchQueue(label: "com.pecantv.imageservice", qos: .userInitiated)
    
    private init() {
        // Configure cache limits
        imageCache.countLimit = 100 // Maximum 100 images in memory
        imageCache.totalCostLimit = 50 * 1024 * 1024 // 50 MB limit
    }
    
    /// Get direct URL for image
    func getImageURL(from originalURL: String) -> URL? {
        return URL(string: originalURL)
    }
    
    /// Create a SwiftUI view that loads images with optimized caching and lazy loading
    func directImage(
        from urlString: String,
        placeholder: @escaping () -> AnyView = { AnyView(Color.gray.opacity(0.3)) }
    ) -> AnyView {
        return AnyView(
            OptimizedLazyImageView(
                urlString: urlString,
                imageService: self,
                placeholder: placeholder
            )
        )
    }
    
    /// Load image with caching
    func loadImage(from urlString: String) async throws -> UIImage {
        // Safety check - ensure URL string is not empty
        guard !urlString.isEmpty else {
            throw ImageServiceError.invalidURL
        }
        
        // Check cache first
        if let cachedImage = imageCache.object(forKey: urlString as NSString) {
            print("📸 ImageService: Cache hit for \(urlString)")
            return cachedImage
        }
        
        // Check if URL is valid
        guard let url = URL(string: urlString) else {
            throw ImageServiceError.invalidURL
        }
        
        // Check if already loading
        if let existingTask = loadingTasks[urlString] {
            print("📸 ImageService: Already loading \(urlString)")
            do {
                return try await existingTask.value ?? UIImage()
            } catch {
                // If the existing task failed, remove it and try again
                loadingTasks.removeValue(forKey: urlString)
                throw error
            }
        }
        
        // Create new loading task
        let task = Task<UIImage?, Error> {
            defer {
                // Remove task from loading tasks
                loadingTasks.removeValue(forKey: urlString)
            }
            
            do {
                print("📸 ImageService: Loading \(urlString)")
                
                let (data, response) = try await URLSession.shared.data(from: url)
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw ImageServiceError.invalidResponse
                }
                
                guard httpResponse.statusCode == 200 else {
                    throw ImageServiceError.httpError(httpResponse.statusCode)
                }
                
                guard let image = UIImage(data: data) else {
                    throw ImageServiceError.invalidImageData
                }
                
                // Cache the image safely
                DispatchQueue.main.async {
                    self.imageCache.setObject(image, forKey: urlString as NSString)
                }
                
                print("📸 ImageService: Successfully loaded \(urlString)")
                return image
                
            } catch {
                print("📸 ImageService: Failed to load \(urlString): \(error)")
                throw error
            }
        }
        
        // Store the task
        loadingTasks[urlString] = task
        
        // Wait for result
        do {
            return try await task.value ?? UIImage()
        } catch {
            // Remove the failed task
            loadingTasks.removeValue(forKey: urlString)
            throw error
        }
    }
    
    /// Clear cache (useful for memory management)
    func clearCache() {
        imageCache.removeAllObjects()
        print("📸 ImageService: Cache cleared")
    }
    
    /// Preload images in background
    func preloadImages(_ urls: [String]) {
        // Safety check - ensure we have valid URLs
        let validURLs = urls.filter { !$0.isEmpty }
        
        guard !validURLs.isEmpty else {
            print("⚠️ ImageService: No valid URLs to preload")
            return
        }
        
        print("📸 ImageService: Preloading \(validURLs.count) images")
        
        Task {
            await withTaskGroup(of: Void.self) { group in
                for url in validURLs {
                    group.addTask {
                        do {
                            _ = try await self.loadImage(from: url)
                        } catch {
                            print("📸 ImageService: Failed to preload \(url): \(error)")
                        }
                    }
                }
            }
            print("📸 ImageService: Completed preloading \(validURLs.count) images")
        }
    }
}

// MARK: - Optimized Lazy Image View

struct OptimizedLazyImageView: View {
    let urlString: String
    let imageService: SimpleImageService
    let placeholder: () -> AnyView
    
    @State private var image: UIImage?
    @State private var isLoading = false
    @State private var error: Error?
    @State private var hasAppeared = false
    @State private var loadAttempted = false
    
    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .transition(.opacity.animation(.easeInOut(duration: 0.3)))
            } else if isLoading {
                placeholder()
                    .overlay(
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .gray))
                            .scaleEffect(0.8)
                    )
            } else if error != nil {
                placeholder()
                    .overlay(
                        VStack(spacing: 4) {
                            Image(systemName: "photo")
                                .font(.system(size: 20))
                                .foregroundColor(.gray)
                            Text("Failed to load")
                                .font(.caption2)
                                .foregroundColor(.gray)
                        }
                    )
            } else {
                placeholder()
            }
        }
        .onAppear {
            if !hasAppeared {
                hasAppeared = true
                loadImage()
            }
        }
        .onDisappear {
            // Reset state when view disappears to allow retry
            if !hasAppeared {
                loadAttempted = false
            }
        }
    }
    
    private func loadImage() {
        guard !isLoading && !loadAttempted else { return }
        
        isLoading = true
        error = nil
        loadAttempted = true
        
        print("🖼️ Loading image: \(urlString)")
        
        Task {
            do {
                let loadedImage = try await imageService.loadImage(from: urlString)
                await MainActor.run {
                    self.image = loadedImage
                    self.isLoading = false
                    print("✅ Image loaded successfully: \(urlString)")
                }
            } catch {
                await MainActor.run {
                    self.error = error
                    self.isLoading = false
                    print("❌ Failed to load image: \(urlString) - \(error.localizedDescription)")
                }
            }
        }
    }
}

// MARK: - Error Types

enum ImageServiceError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case invalidImageData
    case httpError(Int)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid image URL"
        case .invalidResponse:
            return "Invalid server response"
        case .invalidImageData:
            return "Invalid image data"
        case .httpError(let code):
            return "HTTP error: \(code)"
        }
    }
}
