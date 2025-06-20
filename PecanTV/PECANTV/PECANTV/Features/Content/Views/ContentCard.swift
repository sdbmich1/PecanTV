import SwiftUI

class ImageCache {
    static let shared = ImageCache()
    private var cache = NSCache<NSString, UIImage>()
    
    private init() {
        cache.countLimit = 100 // Maximum number of images to cache
    }
    
    func set(_ image: UIImage, for key: String) {
        cache.setObject(image, forKey: key as NSString)
    }
    
    func get(for key: String) -> UIImage? {
        return cache.object(forKey: key as NSString)
    }
    
    func clear() {
        cache.removeAllObjects()
    }
}

struct ContentCard: View {
    let content: MediaContent
    let isFeatured: Bool
    @State private var imageLoadError = false
    @State private var isLoading = true
    @State private var retryCount = 0
    @State private var cachedImage: UIImage?
    
    private let maxRetries = 3
    
    var body: some View {
        VStack(alignment: .leading) {
            ZStack {
                if isLoading {
                    ProgressView()
                        .frame(width: isFeatured ? 300 : 150, height: isFeatured ? 180 : 225)
                        .background(Color.gray.opacity(0.3))
                }
                
                if let cachedImage = cachedImage {
                    Image(uiImage: cachedImage)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: isFeatured ? 300 : 150, height: isFeatured ? 180 : 225)
                        .clipped()
                        .cornerRadius(10)
                } else {
                    AsyncImage(url: URL(string: content.posterURL)) { phase in
                        switch phase {
                        case .empty:
                            ProgressView()
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .onAppear {
                                    isLoading = false
                                    if let uiImage = image.asUIImage() {
                                        ImageCache.shared.set(uiImage, for: content.posterURL)
                                        cachedImage = uiImage
                                    }
                                }
                        case .failure(_):
                            if retryCount < maxRetries {
                                ProgressView()
                                    .onAppear {
                                        retryLoad()
                                    }
                            } else {
                                Image(systemName: "photo")
                                    .font(.largeTitle)
                                    .foregroundColor(.gray)
                                    .frame(width: isFeatured ? 300 : 150, height: isFeatured ? 180 : 225)
                                    .background(Color.gray.opacity(0.3))
                                    .onAppear {
                                        isLoading = false
                                        imageLoadError = true
                                    }
                            }
                        @unknown default:
                            EmptyView()
                        }
                    }
                    .frame(width: isFeatured ? 300 : 150, height: isFeatured ? 180 : 225)
                    .clipped()
                    .cornerRadius(10)
                }
                
                if isFeatured {
                    Image(systemName: "play.fill")
                        .font(.largeTitle)
                        .foregroundColor(.white)
                }
            }
            
            Text(content.title)
                .font(isFeatured ? .headline : .subheadline)
                .lineLimit(1)
            
            if isFeatured {
                Text("\(content.genre) • \(content.runtime) min")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } else {
                Text(content.genre)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .frame(width: isFeatured ? 300 : 150)
        .onAppear {
            loadCachedImage()
        }
    }
    
    private func loadCachedImage() {
        if let cached = ImageCache.shared.get(for: content.posterURL) {
            cachedImage = cached
            isLoading = false
        }
    }
    
    private func retryLoad() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            retryCount += 1
            isLoading = true
            cachedImage = nil
        }
    }
}

extension Image {
    func asUIImage() -> UIImage? {
        let controller = UIHostingController(rootView: self)
        let view = controller.view
        
        let targetSize = controller.view.intrinsicContentSize
        view?.bounds = CGRect(origin: .zero, size: targetSize)
        view?.backgroundColor = .clear
        
        let renderer = UIGraphicsImageRenderer(size: targetSize)
        return renderer.image { _ in
            view?.drawHierarchy(in: controller.view.bounds, afterScreenUpdates: true)
        }
    }
}

#Preview {
    VStack {
        ContentCard(content: MediaContent(
            id: 1,
            title: "Sample Movie",
            description: "A sample movie description.",
            posterURL: "https://example.com/poster.jpg",
            trailerURL: "https://example.com/trailer.mp4",
            contentURL: "https://example.com/content.mp4",
            type: "FILM",
            runtime: 120,
            genre: "Action",
            ageRating: "PG-13"
        ), isFeatured: false)
        
        ContentCard(content: MediaContent(
            id: 2,
            title: "Featured Movie",
            description: "A featured movie description.",
            posterURL: "https://example.com/poster.jpg",
            trailerURL: "https://example.com/trailer.mp4",
            contentURL: "https://example.com/content.mp4",
            type: "FILM",
            runtime: 120,
            genre: "Action",
            ageRating: "PG-13"
        ), isFeatured: true)
    }
} 