import SwiftUI

struct TrendingNowView: View {
    let content: [MediaContent]
    @State private var currentIndex = 0
    @State private var scrollViewProxy: ScrollViewProxy?
    @StateObject private var favoritesManager = FavoritesManager.shared
    
    private let itemWidth: CGFloat = 280
    private let spacing: CGFloat = 16
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Header with title and scroll buttons
            HStack {
                Text("Trending Now")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                    .accessibilityIdentifier("TrendingNowLabel")
                
                Spacer()
                
                // Scroll buttons (only show if there are multiple items)
                if content.count > 1 {
                    HStack(spacing: 8) {
                        Button(action: {
                            withAnimation {
                                if currentIndex > 0 {
                                    currentIndex -= 1
                                    scrollViewProxy?.scrollTo(currentIndex, anchor: .leading)
                                }
                            }
                        }) {
                            Image(systemName: "chevron.left")
                                .font(.title3)
                                .foregroundColor(.white)
                                .frame(width: 32, height: 32)
                                .background(Color.black.opacity(0.6))
                                .clipShape(Circle())
                        }
                        .accessibilityIdentifier("TrendingNowLeftButton")
                        .disabled(currentIndex == 0)
                        .opacity(currentIndex == 0 ? 0.5 : 1.0)
                        
                        Button(action: {
                            withAnimation {
                                if currentIndex < content.count - 1 {
                                    currentIndex += 1
                                    scrollViewProxy?.scrollTo(currentIndex, anchor: .leading)
                                }
                            }
                        }) {
                            Image(systemName: "chevron.right")
                                .font(.title3)
                                .foregroundColor(.white)
                                .frame(width: 32, height: 32)
                                .background(Color.black.opacity(0.6))
                                .clipShape(Circle())
                        }
                        .accessibilityIdentifier("TrendingNowRightButton")
                        .disabled(currentIndex >= content.count - 1)
                        .opacity(currentIndex >= content.count - 1 ? 0.5 : 1.0)
                    }
                }
            }
            .padding(.horizontal)
            .accessibilityElement(children: .combine)
            .accessibilityIdentifier("TrendingNowHeader")
            
            // Content carousel
            if !content.isEmpty {
                GeometryReader { geometry in
                    ZStack {
                        ScrollViewReader { proxy in
                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: spacing) {
                                    ForEach(Array(content.enumerated()), id: \.element.id) { index, item in
                                        NavigationLink(destination: ContentDetailView(content: item, favoritesManager: favoritesManager)) {
                                            VStack(alignment: .leading) {
                                                ZStack(alignment: .topTrailing) {
                                                    AsyncImage(url: URL(string: item.posterURL)) { phase in
                                                        switch phase {
                                                        case .empty:
                                                            Rectangle()
                                                                .fill(Color.gray.opacity(0.3))
                                                                .frame(width: itemWidth, height: 157.5)
                                                                .overlay(
                                                                    ProgressView()
                                                                        .progressViewStyle(CircularProgressViewStyle(tint: .gray))
                                                                        .scaleEffect(0.8)
                                                                )
                                                        case .success(let image):
                                                            image
                                                                .resizable()
                                                                .aspectRatio(contentMode: .fill)
                                                                .frame(width: itemWidth, height: 157.5)
                                                                .clipped()
                                                                .cornerRadius(8)
                                                        case .failure:
                                                            Rectangle()
                                                                .fill(Color.gray.opacity(0.3))
                                                                .frame(width: itemWidth, height: 157.5)
                                                                .overlay(
                                                                    VStack(spacing: 8) {
                                                                        Image(systemName: "photo")
                                                                            .font(.system(size: 24))
                                                                            .foregroundColor(.gray)
                                                                        Text(item.title)
                                                                            .font(.caption)
                                                                            .foregroundColor(.gray)
                                                                            .multilineTextAlignment(.center)
                                                                            .lineLimit(2)
                                                                            .padding(.horizontal, 4)
                                                                    }
                                                                )
                                                                .cornerRadius(8)
                                                        @unknown default:
                                                            Rectangle()
                                                                .fill(Color.gray.opacity(0.3))
                                                                .frame(width: itemWidth, height: 157.5)
                                                                .cornerRadius(8)
                                                        }
                                                    }
                                                    
                                                    // Favorite button
                                                    Button(action: {
                                                        favoritesManager.toggleFavorite(item)
                                                    }) {
                                                        Image(systemName: favoritesManager.isFavorite(item) ? "heart.fill" : "heart")
                                                            .font(.system(size: 16, weight: .semibold))
                                                            .foregroundColor(favoritesManager.isFavorite(item) ? .pecanRed : .white)
                                                            .padding(8)
                                                            .background(Color.black.opacity(0.6))
                                                            .clipShape(Circle())
                                                    }
                                                    .padding(8)
                                                }
                                                
                                                Text(item.title.truncatedTitleWithWordBoundary())
                                                    .font(.subheadline)
                                                    .fontWeight(.medium)
                                                    .foregroundColor(.black)
                                                    .lineLimit(2)
                                                    .frame(width: itemWidth, alignment: .leading)
                                                    .padding(.top, 4)
                                            }
                                        }
                                        .buttonStyle(PlainButtonStyle())
                                        .id(index)
                                    }
                                }
                                .padding(.horizontal)
                            }
                            .onAppear {
                                scrollViewProxy = proxy
                            }
                        }
                    }
                }
                .frame(height: 200)
                .accessibilityIdentifier("TrendingNowCarousel")
            } else {
                // Loading state when no content
                Rectangle()
                    .fill(Color.gray.opacity(0.1))
                    .frame(height: 200)
                    .overlay(
                        VStack(spacing: 12) {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .gray))
                            Text("Loading trending content...")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    )
                    .accessibilityIdentifier("TrendingNowLoadingState")
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("TrendingNowSection")
    }
}

#Preview {
    TrendingNowView(content: [
        MediaContent(
            id: 1,
            title: "Sample Film 1",
            description: "A sample film description",
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
            title: "Sample Film 2",
            description: "Another sample film description",
            posterURL: "https://example.com/poster2.jpg",
            trailerURL: "https://example.com/trailer2.mp4",
            contentURL: "https://example.com/content2.mp4",
            type: "FILM",
            runtime: 95,
            genre: "Comedy",
            ageRating: "PG"
        )
    ])
    .background(Color.black)
} 