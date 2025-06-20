import SwiftUI

struct FavoritesView: View {
    @StateObject private var favoritesManager = FavoritesManager()
    let allContent: [MediaContent]
    @State private var selectedContent: MediaContent?
    @State private var showDetail = false
    
    var favoriteContent: [MediaContent] {
        allContent.filter { favoritesManager.isFavorite($0) }
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)
                
                if favoriteContent.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "heart.slash")
                            .font(.system(size: 48))
                            .foregroundColor(.gray)
                        Text("No Favorites Yet")
                            .font(.title2)
                            .foregroundColor(.white)
                        Text("Add movies and shows to your favorites to see them here")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                } else {
                    ScrollView {
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 16) {
                            ForEach(favoriteContent) { content in
                                ContentPosterCard(content: content)
                                    .onTapGesture {
                                        selectedContent = content
                                        showDetail = true
                                    }
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("My Favorites")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showDetail) {
                if let content = selectedContent {
                    ContentDetailView(content: content, favoritesManager: favoritesManager)
                }
            }
        }
    }
}

struct ContentPosterCard: View {
    let content: MediaContent
    
    var body: some View {
        VStack(alignment: .leading) {
            AsyncImage(url: URL(string: content.posterURL)) { phase in
                switch phase {
                case .empty:
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .aspectRatio(2/3, contentMode: .fit)
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(2/3, contentMode: .fit)
                case .failure:
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .aspectRatio(2/3, contentMode: .fit)
                @unknown default:
                    EmptyView()
                }
            }
            .cornerRadius(8)
            
            Text(content.title)
                .font(.subheadline)
                .foregroundColor(.white)
                .lineLimit(2)
                .padding(.top, 4)
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
} 