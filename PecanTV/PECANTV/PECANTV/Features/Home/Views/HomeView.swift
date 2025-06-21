import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var viewModel: ContentViewModel
    @State private var selectedTab = 0
    @State private var searchText = ""
    @State private var selectedGenre = "All Genres"
    @State private var showGenrePicker = false
    @State private var selectedContent: MediaContent?
    @State private var showTrailer = false
    @State private var showDetail = false
    @State private var isGenreChanging = false
    
    let genres = ["All Genres", "Action", "Adventure", "Biography", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "Horror", "Martial Arts", "Mystery", "Noir", "Romance", "Sci-Fi", "Sports", "Thriller", "Western"]
    
    var allContent: [MediaContent] {
        viewModel.films + viewModel.tvSeries
    }
    
    var filteredContent: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? allContent : allContent.filter { content in
            let contentGenres = content.genre
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            return contentGenres.contains(selectedGenre.lowercased())
        }
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
        return searchFiltered
    }
    
    var filteredFilms: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? viewModel.films : viewModel.films.filter { content in
            let contentGenres = content.genre
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            return contentGenres.contains(selectedGenre.lowercased())
        }
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
        return searchFiltered
    }
    
    var filteredTVSeries: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? viewModel.tvSeries : viewModel.tvSeries.filter { content in
            let contentGenres = content.genre
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            return contentGenres.contains(selectedGenre.lowercased())
        }
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
        return searchFiltered
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.white.edgesIgnoringSafeArea(.all)
                
                if viewModel.isLoading || isGenreChanging {
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
                                        if selectedGenre != genre {
                                            isGenreChanging = true
                                            selectedGenre = genre
                                            // Debug: Log the filtered content
                                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                                                print("🎬 Genre changed to: \(genre)")
                                                print("🎬 Filtered content count: \(filteredContent.count)")
                                                print("🎬 Filtered films count: \(filteredFilms.count)")
                                                print("🎬 First 3 filtered films:")
                                                for (index, film) in filteredFilms.prefix(3).enumerated() {
                                                    print("  \(index): ID \(film.id) - \(film.title)")
                                                }
                                                isGenreChanging = false
                                            }
                                        }
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
                        
                        // Content ScrollView
                        ScrollView {
                            LazyVStack(alignment: .leading, spacing: 20) {
                                // Featured Content (First item as hero)
                                if let featuredContent = filteredContent.first {
                                    FeaturedContentView(content: featuredContent)
                                }
                                
                                // Content Carousels
                                if selectedGenre == "All Genres" {
                                    // Show general carousels when no genre is selected
                                    
                                    if searchText.isEmpty {
                                        // No search query - show regular carousels
                                        
                                        // Trending Now Section (always show when All Genres selected and no search)
                                        TrendingNowView(content: allContent)
                                        
                                        // Films Carousel
                                        if !viewModel.films.isEmpty {
                                            LandscapeCarouselView(
                                                title: "Films",
                                                content: viewModel.films
                                            )
                                        }
                                        
                                        // Poster Carousel (only when no search)
                                        if !viewModel.films.isEmpty {
                                            PosterCarouselView(
                                                title: "Featured Posters",
                                                content: Array(viewModel.films.prefix(10))
                                            )
                                        }
                                        
                                        // TV Series Carousel
                                        if !viewModel.tvSeries.isEmpty {
                                            LandscapeCarouselView(
                                                title: "TV Series",
                                                content: viewModel.tvSeries
                                            )
                                        }
                                    } else {
                                        // Search query - show search results
                                        if !filteredContent.isEmpty {
                                            LandscapeCarouselView(
                                                title: "Search Results for '\(searchText)'",
                                                content: filteredContent
                                            )
                                        } else {
                                            // No search results
                                            VStack(spacing: 16) {
                                                Image(systemName: "magnifyingglass")
                                                    .font(.system(size: 48))
                                                    .foregroundColor(.gray)
                                                Text("No results found for '\(searchText)'")
                                                    .font(.headline)
                                                    .foregroundColor(.black)
                                                Text("Try different keywords or browse our content")
                                                    .font(.subheadline)
                                                    .foregroundColor(.gray)
                                                    .multilineTextAlignment(.center)
                                                    .padding(.horizontal)
                                            }
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 40)
                                        }
                                    }
                                } else {
                                    // Show genre-specific carousels when a genre is selected
                                    
                                    if searchText.isEmpty {
                                        // No search query - show genre carousels
                                        
                                        // Genre Content Carousel (show all filtered content)
                                        if !filteredContent.isEmpty {
                                            LandscapeCarouselView(
                                                title: "\(selectedGenre) Content",
                                                content: filteredContent
                                            )
                                        }
                                        
                                        // Genre Films Carousel (only if there are films in this genre)
                                        if !filteredFilms.isEmpty {
                                            LandscapeCarouselView(
                                                title: "\(selectedGenre) Films",
                                                content: filteredFilms
                                            )
                                        }
                                        
                                        // Genre TV Series Carousel (only if there are series in this genre)
                                        if !filteredTVSeries.isEmpty {
                                            LandscapeCarouselView(
                                                title: "\(selectedGenre) TV Series",
                                                content: filteredTVSeries
                                            )
                                        }
                                    } else {
                                        // Search query with genre filter
                                        if !filteredContent.isEmpty {
                                            LandscapeCarouselView(
                                                title: "\(selectedGenre) Results for '\(searchText)'",
                                                content: filteredContent
                                            )
                                        } else {
                                            // No search results for this genre
                                            VStack(spacing: 16) {
                                                Image(systemName: "magnifyingglass")
                                                    .font(.system(size: 48))
                                                    .foregroundColor(.gray)
                                                Text("No \(selectedGenre) results for '\(searchText)'")
                                                    .font(.headline)
                                                    .foregroundColor(.black)
                                                Text("Try different keywords or browse other genres")
                                                    .font(.subheadline)
                                                    .foregroundColor(.gray)
                                                    .multilineTextAlignment(.center)
                                                    .padding(.horizontal)
                                            }
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 40)
                                        }
                                    }
                                }
                                
                                // Show message if no content found for selected genre
                                if selectedGenre != "All Genres" && filteredContent.isEmpty {
                                    VStack(spacing: 16) {
                                        Image(systemName: "film")
                                            .font(.system(size: 48))
                                            .foregroundColor(.gray)
                                        Text("No \(selectedGenre) content found")
                                            .font(.headline)
                                            .foregroundColor(.black)
                                        Text("Try selecting a different genre or search for something else")
                                            .font(.subheadline)
                                            .foregroundColor(.gray)
                                            .multilineTextAlignment(.center)
                                            .padding(.horizontal)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 40)
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
        }
    }
}

struct FeaturedContentView: View {
    let content: MediaContent
    @StateObject private var favoritesManager = FavoritesManager.shared
    @State private var showDetail = false
    
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
                            .frame(height: 300)
                            .overlay(
                                ProgressView("Loading...")
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    .foregroundColor(.white)
                            )
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(height: 300)
                            .clipped()
                    case .failure:
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(height: 300)
                            .overlay(
                                VStack(spacing: 12) {
                                    Image(systemName: "photo")
                                        .font(.system(size: 48))
                                        .foregroundColor(.gray)
                                    Text(content.title)
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
                .frame(height: 300)
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Content info
                VStack(alignment: .leading, spacing: 8) {
                    Text(content.title)
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