import Foundation
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
