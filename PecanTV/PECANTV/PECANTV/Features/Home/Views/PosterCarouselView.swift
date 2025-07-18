import SwiftUI

struct PosterCarouselView: View {
    let title: String
    let content: [MediaContent]
    @State private var scrollOffset: CGFloat = 0
    @State private var currentIndex: Int = 0
    @StateObject private var cacheManager = ImageCacheManager.shared
    
    // Constants for poster sizing
    private let posterWidth: CGFloat = 120
    private let posterHeight: CGFloat = 180
    private let spacing: CGFloat = 12
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(title)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                
                Spacer()
                
                // Navigation indicators
                HStack(spacing: 4) {
                    ForEach(0..<min(content.count, 5), id: \.self) { index in
                        Circle()
                            .fill(currentIndex == index ? Color.pecanRed : Color.gray.opacity(0.3))
                            .frame(width: 6, height: 6)
                    }
                }
                
                // Scroll buttons
                HStack(spacing: 8) {
                    Button(action: {
                        scrollToPrevious()
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 32, height: 32)
                            .background(Color.pecanRed)
                            .clipShape(Circle())
                    }
                    .disabled(currentIndex == 0)
                    .opacity(currentIndex == 0 ? 0.5 : 1.0)
                    
                    Button(action: {
                        scrollToNext()
                    }) {
                        Image(systemName: "chevron.right")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 32, height: 32)
                            .background(Color.pecanRed)
                            .clipShape(Circle())
                    }
                    .disabled(currentIndex >= content.count - 1)
                    .opacity(currentIndex >= content.count - 1 ? 0.5 : 1.0)
                }
            }
            .padding(.horizontal, 20)
            
            // Horizontal scrolling content
            ScrollViewReader { proxy in
                ScrollView(.horizontal, showsIndicators: false) {
                    LazyHStack(spacing: spacing) {
                        ForEach(Array(content.enumerated()), id: \.element.id) { index, item in
                            PosterCard(content: item, index: index)
                                .id(index)
                                .onAppear {
                                    updateCurrentIndex(index: index)
                                    preloadNearbyImages(currentIndex: index)
                                }
                        }
                    }
                    .padding(.horizontal, 20)
                }
                .onChange(of: currentIndex) { oldValue, newValue in
                    withAnimation(.easeInOut(duration: 0.3)) {
                        proxy.scrollTo(newValue, anchor: .center)
                    }
                }
            }
        }
        .onAppear {
            preloadInitialImages()
        }
    }
    
    private func scrollToNext() {
        guard currentIndex < content.count - 1 else { return }
        currentIndex += 1
    }
    
    private func scrollToPrevious() {
        guard currentIndex > 0 else { return }
        currentIndex -= 1
    }
    
    private func updateCurrentIndex(index: Int) {
        // Update current index based on scroll position
        DispatchQueue.main.async {
            if abs(currentIndex - index) <= 1 {
                currentIndex = index
            }
        }
    }
    
    private func preloadInitialImages() {
        // Preload first 5 images
        let initialUrls = Array(content.prefix(5)).map { $0.posterURL }
        cacheManager.preloadImages(from: initialUrls)
    }
    
    private func preloadNearbyImages(currentIndex: Int) {
        // Preload images for the next 3 items
        let startIndex = max(0, currentIndex)
        let endIndex = min(content.count, currentIndex + 3)
        let urlsToPreload = Array(content[startIndex..<endIndex]).map { $0.posterURL }
        cacheManager.preloadImages(from: urlsToPreload)
    }
}

struct PosterCard: View {
    let content: MediaContent
    let index: Int
    @State private var imageLoaded = false
    @State private var showDetail = false
    @StateObject private var favoritesManager = FavoritesManager.shared
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Poster Image with optimized caching and favorite button overlay
            ZStack(alignment: .topTrailing) {
                SimpleImageService.shared.directImage(
                    from: content.posterURL
                ) {
                    AnyView(
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 120, height: 180)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    )
                }
                .frame(width: 120, height: 180)
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .shadow(color: .black.opacity(0.2), radius: 4, x: 0, y: 2)
                .onAppear {
                    imageLoaded = true
                }
                
                // Favorite button
                Button(action: {
                    favoritesManager.toggleFavorite(content)
                }) {
                    Image(systemName: favoritesManager.isFavorite(content) ? "heart.fill" : "heart")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(favoritesManager.isFavorite(content) ? .pecanRed : .white)
                        .padding(6)
                        .background(Color.black.opacity(0.6))
                        .clipShape(Circle())
                }
                .padding(6)
            }
            
            // Title
            Text(content.title.truncatedTitleWithWordBoundary())
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.black)
                .lineLimit(2)
                .multilineTextAlignment(.leading)
                .frame(width: 120, alignment: .leading)
        }
        .contentShape(Rectangle())
        .onTapGesture {
            showDetail = true
        }
        .sheet(isPresented: $showDetail) {
            NavigationStack {
                ContentDetailView(content: content, favoritesManager: favoritesManager)
            }
        }
    }
}

#Preview {
    PosterCarouselView(
        title: "Featured Films",
        content: [
            MediaContent(
                id: 1,
                title: "Sample Movie 1",
                description: "A sample movie description",
                posterURL: "https://example.com/poster1.jpg",
                trailerURL: "https://example.com/trailer1.mp4",
                contentURL: "https://example.com/content1.mp4",
                type: "FILM",
                runtime: 120,
                genre: "Action",
                ageRating: "PG-13"
            ),
            MediaContent(
                id: 2,
                title: "Sample Movie 2",
                description: "Another sample movie description",
                posterURL: "https://example.com/poster2.jpg",
                trailerURL: "https://example.com/trailer2.mp4",
                contentURL: "https://example.com/content2.mp4",
                type: "FILM",
                runtime: 95,
                genre: "Drama",
                ageRating: "R"
            )
        ]
    )
    .padding()
    .background(Color.white)
} 