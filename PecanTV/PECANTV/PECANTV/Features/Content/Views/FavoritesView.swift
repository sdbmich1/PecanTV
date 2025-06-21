import SwiftUI

struct FavoritesView: View {
    @StateObject private var favoritesManager = FavoritesManager.shared
    let allContent: [MediaContent]
    @State private var selectedContent: MediaContent?
    @State private var showDetail = false
    
    var favoriteContent: [MediaContent] {
        allContent.filter { favoritesManager.isFavorite($0) }
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.white.ignoresSafeArea()
                
                if favoriteContent.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "heart")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("No Favorites Yet")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.black)
                        
                        Text("Start adding your favorite content to see them here")
                            .font(.body)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    VStack(spacing: 0) {
                        // Content area
                        ScrollView {
                            LandscapeCarouselView(
                                title: "My Favorites",
                                content: favoriteContent
                            )
                            .padding(.horizontal)
                            .padding(.top, 20)
                        }
                    }
                }
            }
            .navigationTitle("My Favorites")
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showDetail) {
                if let selectedContent = selectedContent {
                    ContentDetailView(content: selectedContent, favoritesManager: favoritesManager)
                }
            }
        }
        .onAppear {
            // Load favorites from database when view appears
            Task {
                await favoritesManager.loadFavoritesFromDatabase()
            }
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