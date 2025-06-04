import SwiftUI

struct HomeView: View {
    @StateObject private var viewModel = DemoHomeViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    if !viewModel.trendingContent.isEmpty {
                        ContentCarousel(
                            title: "Trending Now",
                            content: viewModel.trendingContent
                        )
                    }
                }
                .padding(.vertical)
            }
            .navigationTitle("PecanTV")
            .refreshable {
                // No-op for demo
            }
            .alert("Error", isPresented: .constant(false)) {
                Button("OK") {}
            } message: {
                EmptyView()
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