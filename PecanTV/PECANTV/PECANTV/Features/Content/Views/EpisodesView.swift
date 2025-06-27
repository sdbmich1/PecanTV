import SwiftUI
import UIKit

struct EpisodesView: View {
    let series: MediaContent
    @State private var episodes: [Episode] = []
    @State private var selectedEpisode: Episode?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @EnvironmentObject var favoritesManager: FavoritesManager
    @Environment(\.dismiss) private var dismiss
    
    // API Configuration
    private let baseURL = "https://77b9-192-69-240-171.ngrok-free.app"
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.white.edgesIgnoringSafeArea(.all)
                
                VStack(alignment: .leading, spacing: 0) {
                    // Back button
                    Button(action: { dismiss() }) {
                        HStack {
                            Image(systemName: "chevron.left")
                            Text("Back")
                        }
                        .font(.headline)
                        .foregroundColor(.black)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(20)
                    }
                    .padding(.horizontal)
                    .padding(.top, 8)
                    
                    // Series Title
                    Text(series.title)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.black)
                        .padding(.horizontal)
                        .padding(.top, 20)
                        .padding(.bottom, 10)
                    
                    if isLoading {
                        VStack {
                            ProgressView()
                                .scaleEffect(1.5)
                            Text("Loading episodes...")
                                .font(.headline)
                                .foregroundColor(.black)
                                .padding(.top)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else if let errorMessage = errorMessage {
                        VStack(spacing: 16) {
                            Image(systemName: "exclamationmark.triangle")
                                .font(.system(size: 48))
                                .foregroundColor(.red)
                            Text("Error")
                                .font(.title2)
                                .foregroundColor(.black)
                            Text(errorMessage)
                                .font(.subheadline)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else if episodes.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "tv")
                                .font(.system(size: 48))
                                .foregroundColor(.gray)
                            Text("No Episodes Available")
                                .font(.title2)
                                .foregroundColor(.black)
                            Text("Episodes for this series will appear here")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        ScrollView {
                            LazyVStack(alignment: .leading, spacing: 20) {
                                // Episodes Carousel
                                EpisodesCarouselView(
                                    episodes: episodes,
                                    series: series,
                                    selectedEpisode: $selectedEpisode
                                )
                                
                                // Episode Details Section
                                if let selectedEpisode = selectedEpisode {
                                    EpisodeDetailsSection(
                                        episode: selectedEpisode,
                                        series: series
                                    )
                                }
                            }
                            .padding(.bottom, 100) // Space for footer
                        }
                    }
                    
                    Spacer()
                    
                    // Footer buttons
                    VStack(spacing: 12) {
                        Button(action: { 
                            // Add to favorites functionality
                            favoritesManager.toggleFavorite(series)
                        }) {
                            HStack {
                                Image(systemName: favoritesManager.isFavorite(series) ? "heart.fill" : "heart")
                                Text(favoritesManager.isFavorite(series) ? "Remove from Favorites" : "Add to Favorites")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(favoritesManager.isFavorite(series) ? Color.gray : Color.pecanRed)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 20)
                }
            }
            .navigationTitle("Episodes")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                loadEpisodes()
            }
        }
    }
    
    private func loadEpisodes() {
        isLoading = true
        errorMessage = nil
        
        guard let url = URL(string: "\(baseURL)/series/\(series.id)/episodes") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    errorMessage = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let data = data else {
                    errorMessage = "No data received"
                    return
                }
                
                do {
                    let decodedEpisodes = try JSONDecoder().decode([Episode].self, from: data)
                    
                    // Filter out episodes without content URLs
                    self.episodes = decodedEpisodes
                        .filter { !$0.contentURL.isEmpty }
                    
                    if let firstEpisode = self.episodes.first {
                        self.selectedEpisode = firstEpisode
                    }
                    
                    self.isLoading = false
                } catch {
                    print("❌ Error decoding episodes: \(error)")
                    self.errorMessage = "Failed to load episodes"
                    self.isLoading = false
                }
            }
        }.resume()
    }
}

struct EpisodesCarouselView: View {
    let episodes: [Episode]
    let series: MediaContent
    @State private var currentIndex = 0
    @State private var scrollViewProxy: ScrollViewProxy?
    @EnvironmentObject var favoritesManager: FavoritesManager
    @Binding var selectedEpisode: Episode?
    
    private let itemWidth: CGFloat = 320
    private let spacing: CGFloat = 16
    private let baseURL = "https://77b9-192-69-240-171.ngrok-free.app"
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            GeometryReader { geometry in
                ZStack {
                    ScrollViewReader { proxy in
                        ScrollView(.horizontal, showsIndicators: false) {
                            LazyHStack(spacing: spacing) {
                                ForEach(Array(episodes.enumerated()), id: \.element.id) { index, episode in
                                    Button(action: {
                                        selectedEpisode = episode
                                        print("🎬 Selected episode: \(episode.title) (S\(episode.seasonNumber)E\(episode.episodeNumber))")
                                    }) {
                                        VStack(alignment: .leading, spacing: 8) {
                                            let imageURL = episode.posterURL.hasPrefix("http") ? episode.posterURL : "\(baseURL)/\(episode.posterURL.hasPrefix("/") ? String(episode.posterURL.dropFirst()) : episode.posterURL)"
                                            AsyncImage(url: URL(string: imageURL)) { phase in
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
                                            .overlay(
                                                RoundedRectangle(cornerRadius: 8)
                                                    .stroke(selectedEpisode?.id == episode.id ? Color.blue : Color.clear, lineWidth: 3)
                                            )
                                            VStack(alignment: .leading, spacing: 4) {
                                                Text(episode.episodeNumberDisplay)
                                                    .font(.caption)
                                                    .fontWeight(.bold)
                                                    .foregroundColor(.blue)
                                                    .frame(width: itemWidth, alignment: .leading)
                                                Text(episode.title.truncatedTitleWithWordBoundary(maxLength: 60))
                                                    .font(.subheadline)
                                                    .fontWeight(.medium)
                                                    .foregroundColor(.black)
                                                    .lineLimit(2)
                                                    .frame(width: itemWidth, alignment: .leading)
                                                Text("\(episode.runtime) min")
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
                            if selectedEpisode == nil && !episodes.isEmpty {
                                selectedEpisode = episodes.first
                            }
                        }
                    }
                    
                    // Navigation Buttons (only show if there are multiple items)
                    if episodes.count > 1 {
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
                            if currentIndex < episodes.count - 1 {
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
            .frame(height: 240) // Slightly taller for episode info
        }
    }
}

struct EpisodeDetailsSection: View {
    let episode: Episode
    let series: MediaContent
    @State private var showVideoPlayer = false
    
    private var videoPlayerContent: some View {
        let baseURL = "https://77b9-192-69-240-171.ngrok-free.app"
        let videoURL: String
        if episode.contentURL.hasPrefix("http") {
            videoURL = episode.contentURL
        } else {
            // Remove leading slash to prevent double slashes
            let cleanContentURL = episode.contentURL.hasPrefix("/") ? String(episode.contentURL.dropFirst()) : episode.contentURL
            videoURL = "\(baseURL)/\(cleanContentURL)"
        }
        
        if let url = URL(string: videoURL) {
            // Create a MediaContent object from the episode for the video player
            let episodeContent = MediaContent(
                id: episode.id,
                title: episode.title,
                description: episode.description,
                posterURL: episode.posterURL,
                trailerURL: "",
                contentURL: episode.contentURL,
                type: "EPISODE",
                runtime: episode.runtime,
                genre: series.genre,
                ageRating: series.ageRating
            )
            return AnyView(VideoPlayerView(url: url, content: episodeContent))
        } else {
            // Show an alert or fallback
            return AnyView(
                VStack {
                    Text("Error")
                        .font(.title)
                        .foregroundColor(.red)
                    Text("Invalid video URL for this episode")
                        .foregroundColor(.gray)
                    Button("Close") {
                        showVideoPlayer = false
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.white)
            )
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Section Title
            Text("Episode Details")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.black)
                .padding(.horizontal)
            
            // Episode Description Card
            VStack(alignment: .leading, spacing: 12) {
                // Description
                if !episode.description.isEmpty {
                    ScrollView {
                        Text(episode.description.truncatedTitleWithWordBoundary(maxLength: 50))
                            .font(.body)
                            .foregroundColor(.black)
                            .lineLimit(nil)
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 8)
                    }
                    .frame(maxHeight: 200)
                } else {
                    Text("No description available for this episode.")
                        .font(.body)
                        .foregroundColor(.gray)
                        .italic()
                        .padding(.vertical, 8)
                }
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(12)
            .padding(.horizontal)
            
            // Watch Episode Button
            Button(action: {
                showVideoPlayer = true
            }) {
                HStack {
                    Image(systemName: "play.fill")
                    Text("Watch Episode")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .padding(.horizontal)
        }
        .fullScreenCover(isPresented: $showVideoPlayer) {
            videoPlayerContent
        }
    }
}

#Preview {
    let sampleSeries = MediaContent(
        id: 1,
        title: "Sample Series",
        description: "A sample series description",
        posterURL: "https://example.com/poster.jpg",
        trailerURL: "https://example.com/trailer.mp4",
        contentURL: "https://example.com/content.mp4",
        type: "SERIES",
        runtime: 60,
        genre: "Drama",
        ageRating: "TV-14"
    )
    
    EpisodesView(series: sampleSeries)
        .environmentObject(FavoritesManager())
} 