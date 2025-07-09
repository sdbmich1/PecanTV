import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var viewModel: ContentViewModel
    @EnvironmentObject private var healthChecker: APIHealthChecker
    @State private var selectedTab = 0
    @State private var searchText = ""
    @State private var selectedFilter = "All"
    @State private var selectedGenre = "All Genres"
    @State private var showGenrePicker = false
    @State private var selectedContent: MediaContent?
    @State private var showTrailer = false
    @State private var showDetail = false
    
    let genres = ["All Genres", "Action", "Adventure", "Animals", "Anime", "Children", "Comedy", "Crime", "Documentary", "Drama", "Educational", "Faith", "Fantasy", "Fashion", "Food", "Gaming", "Health", "History", "Horror", "Martial Arts", "Mystery", "Nature", "News", "Reality", "Romance", "Science Fiction", "Science", "Sitcom", "Special", "Sports", "Technology", "Thriller", "Western"]
    
    var allContent: [MediaContent] {
        viewModel.films + viewModel.tvSeries
    }
    
    var recentlyAddedContent: [MediaContent] {
        // Show the most recent content (first 10 items)
        let allContent = viewModel.films + viewModel.tvSeries
        return Array(allContent.prefix(10))
    }
    
    var filteredContent: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? allContent : allContent.filter { content in
            let contentGenre = content.genre.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
            let selectedGenreLower = selectedGenre.lowercased()
            
            // Debug logging
            print("🔍 Filtering: '\(content.title)' (genre: '\(content.genre)') against '\(selectedGenre)'")
            
            // Simple genre matching
            let matches = contentGenre.contains(selectedGenreLower) || selectedGenreLower.contains(contentGenre)
            print("🔍 Match result: \(matches)")
            
            return matches
        }
        
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { 
            $0.title.localizedCaseInsensitiveContains(searchText) 
        }
        
        print("🔍 Filtered content count: \(searchFiltered.count) for genre '\(selectedGenre)'")
        return searchFiltered
    }
    
    var filteredFilms: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? viewModel.films : viewModel.films.filter { content in
            let contentGenre = content.genre.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
            let selectedGenreLower = selectedGenre.lowercased()
            
            // Simple genre matching
            return contentGenre.contains(selectedGenreLower) || selectedGenreLower.contains(contentGenre)
        }
        
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { 
            $0.title.localizedCaseInsensitiveContains(searchText) 
        }
        
        print("🔍 Filtered films count: \(searchFiltered.count) for genre '\(selectedGenre)'")
        return searchFiltered
    }
    
    var filteredTVSeries: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? viewModel.tvSeries : viewModel.tvSeries.filter { content in
            let contentGenre = content.genre.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
            let selectedGenreLower = selectedGenre.lowercased()
            
            // Simple genre matching
            return contentGenre.contains(selectedGenreLower) || selectedGenreLower.contains(contentGenre)
        }
        
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { 
            $0.title.localizedCaseInsensitiveContains(searchText) 
        }
        
        print("🔍 Filtered TV series count: \(searchFiltered.count) for genre '\(selectedGenre)'")
        return searchFiltered
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.white.edgesIgnoringSafeArea(.all)
                
                if !healthChecker.isAPIAvailable {
                    VStack(spacing: 20) {
                        Image(systemName: "wifi.slash")
                            .font(.system(size: 60))
                            .foregroundColor(.red)
                        
                        Text("Server Unavailable")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Text("The PecanTV server is currently unavailable.\nPlease check your connection or try again later.")
                            .multilineTextAlignment(.center)
                            .foregroundColor(.gray)
                            .padding(.horizontal)
                    }
                } else if viewModel.isLoading {
                    VStack {
                        ProgressView("Loading content...")
                            .progressViewStyle(CircularProgressViewStyle(tint: .black))
                            .foregroundColor(.black)
                    }
                } else if let error = viewModel.error {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 48))
                            .foregroundColor(.red)
                        Text("Error loading content")
                            .font(.headline)
                            .foregroundColor(.black)
                        Text(error.localizedDescription)
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                } else if viewModel.films.isEmpty && viewModel.tvSeries.isEmpty {
                    // No content available
                    VStack(spacing: 20) {
                        Image(systemName: "film")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("No Content Available")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.black)
                        
                        Text("Check back later for new content")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                        
                        Button("Refresh") {
                            viewModel.loadContent()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                } else {
                    VStack(spacing: 0) {
                        // Search and Filter Bar at the top
                        HStack(spacing: 12) {
                            // Search Bar
                            SearchBar(text: $searchText, placeholder: "Search movies and shows...")
                            
                            // Genre Dropdown
                            Menu {
                                ForEach(genres, id: \.self) { genre in
                                    Button(genre) {
                                        selectedGenre = genre
                                    }
                                }
                            } label: {
                                HStack {
                                    Text(selectedGenre)
                                        .foregroundColor(.black)
                                        .lineLimit(1)
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.gray)
                                }
                                .padding(.horizontal, 12)
                                .padding(.vertical, 12)
                                .background(Color.gray.opacity(0.1))
                                .cornerRadius(25)
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 8)
                        .padding(.bottom, 16)
                        
                        // Main content area
                        ScrollView {
                            LazyVStack(spacing: 20) {
                                // Featured Section (Hero)
                                if let featuredContent = filteredContent.first {
                                    FeaturedContentView(content: featuredContent)
                                }
                                
                                // Trending Now Section
                                if !filteredFilms.isEmpty {
                                    TrendingNowView(content: filteredFilms)
                                }
                                
                                // Hot Series Section
                                if !filteredTVSeries.isEmpty {
                                    LandscapeCarouselView(title: "Hot Series", content: filteredTVSeries)
                                }
                                
                                // Recently Added Section
                                let recentlyAdded = Array((viewModel.films + viewModel.tvSeries).prefix(10)); if !recentlyAdded.isEmpty {
                                    LandscapeCarouselView(title: "Recently Added", content: recentlyAdded)
                                }
                            }
                            .padding(.bottom, 100) // Space for tab bar
                        }
                    }
                }
            }
            .navigationTitle("PECAN TV")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Image("pecantv_logo")
                        .resizable()
                        .scaledToFit()
                        .frame(height: 30)
                }
            }
            .onAppear {
                // Content will load automatically via ContentViewModel
            }
        }
    }
}

struct FeaturedContentView: View {
    let content: MediaContent
    @StateObject private var favoritesManager = FavoritesManager.shared
    @State private var showDetail = false
    
    // Use flexible dimensions to prevent layout conflicts
    private let featuredHeight: CGFloat = 200
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Featured")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.black)
                .padding(.horizontal)
            
            ZStack(alignment: .bottomLeading) {
                AsyncImage(url: URL(string: content.posterURL)) { phase in
                    switch phase {
                    case .empty:
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(maxHeight: featuredHeight)
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(maxHeight: featuredHeight)
                            .clipped()
                    case .failure:
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(maxHeight: featuredHeight)
                            .overlay(
                                VStack(spacing: 12) {
                                    Image(systemName: "photo")
                                        .font(.system(size: 48))
                                        .foregroundColor(.gray)
                                    Text(content.title.truncatedTitleWithWordBoundary())
                                        .font(.headline)
                                        .foregroundColor(.gray)
                                        .multilineTextAlignment(.center)
                                        .padding(.horizontal)
                                }
                            )
                    @unknown default:
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(height: 300)
                    }
                }
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Gradient overlay
                LinearGradient(
                    gradient: Gradient(colors: [Color.clear, Color.black.opacity(0.7)]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .frame(maxHeight: featuredHeight)
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Content info
                VStack(alignment: .leading, spacing: 8) {
                    Text(content.title.truncatedTitleWithWordBoundary())
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    HStack {
                        Text(content.type)
                        Text("•")
                        Text("\(content.runtime) min")
                        if !content.genre.isEmpty && content.genre != "Unknown" {
                            Text("•")
                            Text(content.genre)
                        }
                        if !content.ageRating.isEmpty && content.ageRating != "NR" {
                            Text("•")
                            Text(content.ageRating)
                        }
                    }
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    
                    Text(content.description)
                        .font(.body)
                        .foregroundColor(.white)
                        .lineLimit(3)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 20)
            }
            .onTapGesture {
                showDetail = true
            }
        }
        .sheet(isPresented: $showDetail) {
            ContentDetailView(content: content, favoritesManager: favoritesManager)
        }
    }
}

struct GenrePickerView: View {
    @Binding var selectedGenre: String
    let genres: [String]
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVStack(spacing: 0) {
                    ForEach(genres, id: \.self) { genre in
                        Button {
                            selectedGenre = genre
                            dismiss()
                        } label: {
                            HStack {
                                Text(genre)
                                    .foregroundColor(.primary)
                                Spacer()
                                if genre == selectedGenre {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.blue)
                                }
                            }
                            .padding(.horizontal)
                            .padding(.vertical, 12)
                            .contentShape(Rectangle())
                        }
                        .buttonStyle(PlainButtonStyle())
                        
                        if genre != genres.last {
                            Divider()
                                .padding(.leading)
                        }
                    }
                }
            }
            .navigationTitle("Select Genre")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    HomeView()
} 