import SwiftUI

struct AsyncImageView: View {
    let url: URL?
    let aspectRatio: CGFloat
    
    var body: some View {
        if let url = url {
            AsyncImage(url: url) { phase in
                switch phase {
                case .empty:
                    // Show white placeholder while loading
                    Color.white
                        .aspectRatio(aspectRatio, contentMode: .fit)
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(aspectRatio, contentMode: .fit)
                case .failure(_):
                    // Show white placeholder on failure
                    Color.white
                        .aspectRatio(aspectRatio, contentMode: .fit)
                @unknown default:
                    Color.white
                        .aspectRatio(aspectRatio, contentMode: .fit)
                }
            }
        } else {
            // Show white placeholder if URL is nil
            Color.white
                .aspectRatio(aspectRatio, contentMode: .fit)
        }
    }
} 