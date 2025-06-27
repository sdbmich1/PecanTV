import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = ContentViewModel()
    @StateObject private var favoritesManager = FavoritesManager()
    @State private var searchText = ""
    
    private var searchResults: [MediaContent] {
        if searchText.isEmpty {
            return []
        }
        
        let allContent = viewModel.films + viewModel.tvSeries
        let filteredContent = allContent.filter { content in
            content.title.localizedCaseInsensitiveContains(searchText)
        }
        
        return filteredContent
    }
    
    var body: some View {
        NavigationView {
            VStack {
                // Search Bar
                SearchBar(text: $searchText, placeholder: "Search films and series...")
                    .padding()
                
                if searchText.isEmpty {
                    VStack {
                        Spacer()
                        Text("Start typing to search")
                            .foregroundColor(.gray)
                        Spacer()
                    }
                } else if searchResults.isEmpty {
                    VStack {
                        Spacer()
                        Text("No results found")
                            .foregroundColor(.gray)
                        Spacer()
                    }
                } else {
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(searchResults) { content in
                                NavigationLink(destination: ContentDetailView(content: content, favoritesManager: favoritesManager)) {
                                    HStack(spacing: 12) {
                                        // Poster Image
                                        AsyncImage(url: URL(string: content.posterURL)) { phase in
                                            switch phase {
                                            case .empty:
                                                Rectangle()
                                                    .fill(Color.gray.opacity(0.2))
                                                    .frame(width: 80, height: 120)
                                            case .success(let image):
                                                image
                                                    .resizable()
                                                    .aspectRatio(contentMode: .fill)
                                                    .frame(width: 80, height: 120)
                                                    .clipped()
                                            case .failure:
                                                Rectangle()
                                                    .fill(Color.gray.opacity(0.2))
                                                    .frame(width: 80, height: 120)
                                                    .overlay(
                                                        Image(systemName: "film")
                                                            .font(.title)
                                                            .foregroundColor(.gray)
                                                    )
                                            @unknown default:
                                                EmptyView()
                                            }
                                        }
                                        .cornerRadius(8)
                                        
                                        // Content Info
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(content.title.truncatedTitleWithWordBoundary())
                                                .font(.headline)
                                                .foregroundColor(.primary)
                                            
                                            Text(content.type)
                                                .font(.subheadline)
                                                .foregroundColor(.blue)
                                            
                                            Text("\(content.runtime) min • \(content.genre)")
                                                .font(.caption)
                                                .foregroundColor(.gray)
                                        }
                                        
                                        Spacer()
                                    }
                                    .padding(.horizontal)
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
                        }
                        .padding(.vertical)
                    }
                }
            }
            .navigationTitle("Search")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct SearchResultRow: View {
    let content: MediaContent
    var body: some View {
        HStack(spacing: 12) {
            // Poster Image
            AsyncImage(url: URL(string: content.posterURL)) { phase in
                switch phase {
                case .empty:
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(width: 80, height: 120)
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 80, height: 120)
                        .clipped()
                case .failure:
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(width: 80, height: 120)
                        .overlay(
                            Image(systemName: "film")
                                .font(.title)
                                .foregroundColor(.gray)
                        )
                @unknown default:
                    EmptyView()
                }
            }
            .cornerRadius(8)
            
            // Content Info
            VStack(alignment: .leading, spacing: 4) {
                Text(content.title.truncatedTitleWithWordBoundary())
                    .font(.headline)
                    .foregroundColor(.primary)
                
                Text(content.type)
                    .font(.subheadline)
                    .foregroundColor(.blue)
                
                Text("\(content.runtime) min • \(content.genre)")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            
            Spacer()
        }
        .padding(.horizontal)
    }
}

#Preview {
    SearchView()
} 