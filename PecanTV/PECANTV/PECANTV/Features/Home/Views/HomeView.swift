import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var viewModel: ContentViewModel
    @EnvironmentObject private var healthChecker: APIHealthChecker
    @State private var selectedTab = 0
    @State private var searchText = ""
    @State private var selectedGenre = "All Genres"
    @State private var showGenrePicker = false
    @State private var selectedContent: MediaContent?
    @State private var showTrailer = false
    @State private var showDetail = false
    @State private var isGenreChanging = false
    
    let genres = ["All Genres", "Action", "Adventure", "Animals", "Anime", "Children", "Comedy", "Crime", "Documentary", "Drama", "Educational", "Faith", "Fantasy", "Fashion", "Food", "Gaming", "Health", "History", "Horror", "Martial Arts", "Mystery", "Nature", "News", "Reality", "Romance", "Science Fiction", "Science", "Sitcom", "Special", "Sports", "Technology", "Thriller", "Western"]
    
    var allContent: [MediaContent] {
        viewModel.films + viewModel.tvSeries
    }
    
    var filteredContent: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? allContent : allContent.filter { content in
            let contentGenres = content.genre
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            
            // Handle special cases for genre mapping
            let selectedGenreLower = selectedGenre.lowercased()
            let mappedGenres = getMappedGenres(for: selectedGenreLower)
            
            return contentGenres.contains { contentGenre in
                mappedGenres.contains(contentGenre)
            }
        }
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
        return searchFiltered
    }
    
    var filteredFilms: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? viewModel.films : viewModel.films.filter { content in
            let contentGenres = content.genre
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            
            // Handle special cases for genre mapping
            let selectedGenreLower = selectedGenre.lowercased()
            let mappedGenres = getMappedGenres(for: selectedGenreLower)
            
            return contentGenres.contains { contentGenre in
                mappedGenres.contains(contentGenre)
            }
        }
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
        return searchFiltered
    }
    
    var filteredTVSeries: [MediaContent] {
        let genreFiltered = selectedGenre == "All Genres" ? viewModel.tvSeries : viewModel.tvSeries.filter { content in
            let contentGenres = content.genre
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            
            // Handle special cases for genre mapping
            let selectedGenreLower = selectedGenre.lowercased()
            let mappedGenres = getMappedGenres(for: selectedGenreLower)
            
            return contentGenres.contains { contentGenre in
                mappedGenres.contains(contentGenre)
            }
        }
        let searchFiltered = searchText.isEmpty ? genreFiltered : genreFiltered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
        return searchFiltered
    }
    
    // Helper function to map display genre names to possible database names
    private func getMappedGenres(for displayGenre: String) -> [String] {
        let mapping: [String: [String]] = [
            "science fiction": ["science fiction", "sci-fi", "scifi"],
            "sci-fi": ["science fiction", "sci-fi", "scifi"],
            "martial arts": ["martial arts", "kung-fu", "kungfu"],
            "kung-fu": ["martial arts", "kung-fu", "kungfu"]
        ]
        
        return mapping[displayGenre] ?? [displayGenre]
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
                            .foregroundColor(.secondary)
                            .padding(.horizontal)
                        
                        Button("Retry Connection") {
                            healthChecker.checkAPIHealth()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                } else if viewModel.isLoading || isGenreChanging {
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
                            HStack {
                                Image(systemName: "magnifyingglass")
                                    .foregroundColor(.gray)
                                TextField("Search movies and shows...", text: $searchText)
                                    .textFieldStyle(PlainTextFieldStyle())
                                    .foregroundColor(.black)
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 12)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(25)
                            
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
                                    
                                    // Trending Now Carousel (exclude featured content)
                                    if filteredContent.count > 1 {
                                        LazyLandscapeCarouselView(
                                            title: "Trending Now",
                                            content: Array(filteredContent.dropFirst())
                                        )
                                    }
                                    
                                    // Films Carousel
                                    if !viewModel.films.isEmpty {
                                        LazyLandscapeCarouselView(
                                            title: "Films",
                                            content: viewModel.films
                                        )
                                    }
                                    
                                    // TV Series Carousel
                                    if !viewModel.tvSeries.isEmpty {
                                        LazyLandscapeCarouselView(
                                            title: "TV Series",
                                            content: viewModel.tvSeries
                                        )
                                    }
                                } else {
                                    // Show genre-specific carousels when a genre is selected
                                    
                                    // Genre Content Carousel (exclude featured content)
                                    if filteredContent.count > 1 {
                                        LazyLandscapeCarouselView(
                                            title: "\(selectedGenre) Content",
                                            content: Array(filteredContent.dropFirst())
                                        )
                                    }
                                    
                                    // Genre Films Carousel (only if there are films in this genre)
                                    if !filteredFilms.isEmpty {
                                        LazyLandscapeCarouselView(
                                            title: "\(selectedGenre) Films",
                                            content: filteredFilms
                                        )
                                    }
                                    
                                    // Genre TV Series Carousel (only if there are series in this genre)
                                    if !filteredTVSeries.isEmpty {
                                        LazyLandscapeCarouselView(
                                            title: "\(selectedGenre) TV Series",
                                            content: filteredTVSeries
                                        )
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
    @StateObject private var favoritesManager = FavoritesManager()
    @State private var showDetail = false
    
    // Use flexible dimensions to prevent layout conflicts
    private let featuredHeight: CGFloat = 300
    
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
                                Image(systemName: "photo")
                                    .font(.system(size: 48))
                                    .foregroundColor(.gray)
                            )
                    @unknown default:
                        EmptyView()
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

struct LazyLandscapeCarouselView: View {
    let title: String
    let content: [MediaContent]
    @State private var scrollOffset: CGFloat = 0
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(title)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                
                Spacer()
                
                // Scroll buttons
                HStack(spacing: 8) {
                    Button(action: {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            scrollOffset -= 200
                        }
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.title3)
                            .foregroundColor(.white)
                            .frame(width: 32, height: 32)
                            .background(Color.black.opacity(0.6))
                            .clipShape(Circle())
                    }
                    
                    Button(action: {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            scrollOffset += 200
                        }
                    }) {
                        Image(systemName: "chevron.right")
                            .font(.title3)
                            .foregroundColor(.white)
                            .frame(width: 32, height: 32)
                            .background(Color.black.opacity(0.6))
                            .clipShape(Circle())
                    }
                }
            }
            .padding(.horizontal)
            
            ScrollView(.horizontal, showsIndicators: false) {
                LazyHStack(spacing: 12) {
                    ForEach(content, id: \.id) { item in
                        LazyContentCard(content: item)
                    }
                }
                .padding(.horizontal)
                .offset(x: scrollOffset)
            }
        }
        .onAppear {
            print("🎬 Carousel '\(title)' created with \(content.count) items:")
            for (index, item) in content.enumerated() {
                print("  \(index): ID \(item.id) - \(item.title)")
            }
        }
    }
}

struct LazyContentCard: View {
    let content: MediaContent
    @EnvironmentObject var favoritesManager: FavoritesManager
    @State private var showDetail = false
    
    // Use landscape dimensions for 16:9 aspect ratio
    private let cardWidth: CGFloat = 280
    private let cardHeight: CGFloat = 157.5  // 16:9 aspect ratio
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            AsyncImage(url: URL(string: content.posterURL)) { phase in
                switch phase {
                case .empty:
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: cardWidth, height: cardHeight)
                        .overlay(
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .gray))
                        )
                        .cornerRadius(10)
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: cardWidth, height: cardHeight)
                        .clipped()
                        .cornerRadius(10)
                case .failure:
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: cardWidth, height: cardHeight)
                        .overlay(
                            Image(systemName: "photo")
                                .font(.system(size: 32))
                                .foregroundColor(.gray)
                        )
                        .cornerRadius(10)
                @unknown default:
                    EmptyView()
                }
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(content.title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
                    .lineLimit(2)
                
                HStack {
                    Text(content.genre)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                    
                    Spacer()
                    
                    if !content.ageRating.isEmpty && content.ageRating != "NR" {
                        Text(content.ageRating)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .frame(width: cardWidth, alignment: .leading)
        }
        .frame(width: cardWidth)
        .contentShape(Rectangle()) // Make entire card tappable
        .onTapGesture {
            print("🎬 Card tapped - ID: \(content.id), Title: \(content.title), Genre: \(content.genre)")
            showDetail = true
        }
        .sheet(isPresented: $showDetail) {
            ContentDetailView(content: content, favoritesManager: favoritesManager)
        }
        .onAppear {
            print("🎬 Card created - ID: \(content.id), Title: \(content.title)")
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