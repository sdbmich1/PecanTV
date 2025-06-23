import SwiftUI

struct FavoritesView: View {
    @EnvironmentObject var favoritesManager: FavoritesManager
    let allContent: [MediaContent]
    @State private var selectedContent: MediaContent?
    @State private var showDetail = false
    
    var favoriteContent: [MediaContent] {
        allContent.filter { favoritesManager.isFavorite($0) }
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.white.edgesIgnoringSafeArea(.all)
                
                VStack(alignment: .leading, spacing: 0) {
                    // Section Title
                    Text("My Favorites")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.black)
                        .padding(.horizontal)
                        .padding(.top, 20)
                        .padding(.bottom, 10)
                    
                    if favoriteContent.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "heart.slash")
                                .font(.system(size: 48))
                                .foregroundColor(.gray)
                            Text("No Favorites Yet")
                                .font(.title2)
                                .foregroundColor(.black)
                            Text("Add movies and shows to your favorites to see them here")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        ScrollView {
                            LazyVStack(alignment: .leading, spacing: 20) {
                                // Custom Favorites Carousel with titles and genres
                                FavoritesCarouselView(content: favoriteContent)
                            }
                            .padding(.bottom, 100) // Space for tab bar
                        }
                    }
                }
            }
            .navigationTitle("My Favorites")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct FavoritesCarouselView: View {
    let content: [MediaContent]
    @State private var currentIndex = 0
    @State private var scrollViewProxy: ScrollViewProxy?
    @StateObject private var favoritesManager = FavoritesManager()
    
    private let itemWidth: CGFloat = 280
    private let spacing: CGFloat = 16
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            GeometryReader { geometry in
                ZStack {
                    ScrollViewReader { proxy in
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: spacing) {
                                ForEach(Array(content.enumerated()), id: \.element.id) { index, item in
                                    NavigationLink(destination: ContentDetailView(content: item, favoritesManager: favoritesManager)) {
                                        VStack(alignment: .leading, spacing: 8) {
                                            AsyncImage(url: URL(string: item.posterURL)) { phase in
                                                switch phase {
                                                case .empty:
                                                    Rectangle()
                                                        .fill(Color.gray.opacity(0.3))
                                                        .frame(width: itemWidth, height: 157.5)
                                                case .success(let image):
                                                    image
                                                        .resizable()
                                                        .aspectRatio(contentMode: .fill)
                                                        .frame(width: itemWidth, height: 157.5)
                                                        .clipped()
                                                case .failure:
                                                    Rectangle()
                                                        .fill(Color.gray.opacity(0.3))
                                                        .frame(width: itemWidth, height: 157.5)
                                                @unknown default:
                                                    EmptyView()
                                                }
                                            }
                                            .frame(width: itemWidth, height: 157.5)
                                            .cornerRadius(8)
                                            
                                            VStack(alignment: .leading, spacing: 4) {
                                                Text(item.title)
                                                    .font(.subheadline)
                                                    .fontWeight(.medium)
                                                    .foregroundColor(.black)
                                                    .lineLimit(2)
                                                    .frame(width: itemWidth, alignment: .leading)
                                                
                                                Text(item.genre)
                                                    .font(.caption)
                                                    .foregroundColor(.gray)
                                                    .frame(width: itemWidth, alignment: .leading)
                                            }
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
                    
                    // Navigation Buttons (only show if there are multiple items)
                    if content.count > 1 {
                        HStack {
                            // Left scroll button
                            if currentIndex > 0 {
                                Button(action: {
                                    withAnimation {
                                        currentIndex -= 1
                                        scrollViewProxy?.scrollTo(currentIndex, anchor: .leading)
                                    }
                                }) {
                                    Image(systemName: "chevron.left")
                                        .font(.title2)
                                        .foregroundColor(.white)
                                        .frame(width: 40, height: 40)
                                        .background(Color.black.opacity(0.7))
                                        .clipShape(Circle())
                                }
                                .padding(.leading, 8)
                            }
                            
                            Spacer()
                            
                            // Right scroll button
                            if currentIndex < content.count - 1 {
                                Button(action: {
                                    withAnimation {
                                        currentIndex += 1
                                        scrollViewProxy?.scrollTo(currentIndex, anchor: .trailing)
                                    }
                                }) {
                                    Image(systemName: "chevron.right")
                                        .font(.title2)
                                        .foregroundColor(.white)
                                        .frame(width: 40, height: 40)
                                        .background(Color.black.opacity(0.7))
                                        .clipShape(Circle())
                                }
                                .padding(.trailing, 8)
                            }
                        }
                        .position(x: geometry.size.width / 2, y: geometry.size.height / 2)
                    }
                }
            }
            .frame(height: 220) // Fixed height for the carousel
        }
    }
}

#Preview {
    let sampleContent = MediaContent(
        id: 1,
        title: "Sample Film",
        description: "A sample film description",
        posterURL: "https://example.com/poster.jpg",
        trailerURL: "https://example.com/trailer.mp4",
        contentURL: "https://example.com/content.mp4",
        type: "FILM",
        runtime: 120,
        genre: "Action",
        ageRating: "PG-13"
    )
    FavoritesView(allContent: [sampleContent])
        .environmentObject(FavoritesManager())
} 