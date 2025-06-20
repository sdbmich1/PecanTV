import SwiftUI

struct LandscapeCarouselView: View {
    let title: String
    let content: [MediaContent]
    @State private var currentIndex = 0
    @State private var scrollViewProxy: ScrollViewProxy?
    @StateObject private var favoritesManager = FavoritesManager()
    
    private let itemWidth: CGFloat = 280
    private let spacing: CGFloat = 16
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .padding(.horizontal)
            
            GeometryReader { geometry in
                ZStack {
                    ScrollViewReader { proxy in
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: spacing) {
                                ForEach(Array(content.enumerated()), id: \.element.id) { index, item in
                                    NavigationLink(destination: ContentDetailView(content: item, favoritesManager: favoritesManager)) {
                                        VStack(alignment: .leading) {
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
                                            
                                            Text(item.title)
                                                .font(.subheadline)
                                                .fontWeight(.medium)
                                                .foregroundColor(.white)
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
                                        scrollViewProxy?.scrollTo(currentIndex, anchor: .leading)
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
                    }
                }
            }
            .frame(height: 200)
        }
    }
}

#Preview {
    LandscapeCarouselView(
        title: "Recently Added",
        content: [
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
        ]
    )
} 