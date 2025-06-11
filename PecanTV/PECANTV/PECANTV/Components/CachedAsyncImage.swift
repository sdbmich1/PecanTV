import SwiftUI

struct CachedAsyncImage<Content: View, Placeholder: View>: View {
    private let url: URL
    private let scale: CGFloat
    private let transaction: Transaction
    private let content: (Image) -> Content
    private let placeholder: () -> Placeholder
    
    init(
        url: URL,
        scale: CGFloat = 1.0,
        transaction: Transaction = Transaction(),
        @ViewBuilder content: @escaping (Image) -> Content,
        @ViewBuilder placeholder: @escaping () -> Placeholder
    ) {
        self.url = url
        self.scale = scale
        self.transaction = transaction
        self.content = content
        self.placeholder = placeholder
    }
    
    var body: some View {
        AsyncImage(
            url: url,
            scale: scale,
            transaction: transaction
        ) { phase in
            switch phase {
            case .empty:
                placeholder()
            case .success(let image):
                content(image)
            case .failure:
                placeholder()
            @unknown default:
                placeholder()
            }
        }
        .task {
            do {
                _ = try await ImageCacheService.shared.getImage(for: url)
            } catch {
                print("Failed to cache image: \(error)")
            }
        }
    }
} 