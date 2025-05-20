import SwiftUI

struct HomeView: View {
    @StateObject private var viewModel = HomeViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    if !viewModel.continueWatching.isEmpty {
                        ContentCarousel(
                            title: "Continue Watching",
                            content: viewModel.continueWatching
                        )
                    }
                    
                    ContentCarousel(
                        title: "Trending Now",
                        content: viewModel.trendingContent
                    )
                    
                    ContentCarousel(
                        title: "Recommended for You",
                        content: viewModel.recommendedContent
                    )
                }
                .padding(.vertical)
            }
            .navigationTitle("PecanTV")
            .refreshable {
                viewModel.refresh()
            }
            .alert("Error", isPresented: .constant(viewModel.error != nil)) {
                Button("OK") {
                    viewModel.error = nil
                }
            } message: {
                if let error = viewModel.error {
                    Text(error)
                }
            }
        }
    }
}

struct ContentCarousel: View {
    let title: String
    let content: [Content]
    
    var body: some View {
        VStack(alignment: .leading) {
            Text(title)
                .font(.title2)
                .fontWeight(.bold)
                .padding(.horizontal)
            
            ScrollView(.horizontal, showsIndicators: false) {
                LazyHStack(spacing: 15) {
                    ForEach(content) { item in
                        NavigationLink(destination: ContentDetailView(content: item)) {
                            ContentCard(content: item)
                        }
                    }
                }
                .padding(.horizontal)
            }
        }
    }
}

struct ContentCard: View {
    let content: Content
    
    var body: some View {
        VStack(alignment: .leading) {
            AsyncImage(url: content.posterURL) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
            }
            .frame(width: 120, height: 180)
            .cornerRadius(8)
            
            Text(content.title)
                .font(.caption)
                .lineLimit(2)
                .frame(width: 120)
        }
    }
}

#Preview {
    HomeView()
} 