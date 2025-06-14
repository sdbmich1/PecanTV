import SwiftUI
import AVKit

struct VideoPlayerWithMetadata: View {
    let player: AVPlayer
    let title: String
    let description: String
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            VideoPlayer(player: player)
                .edgesIgnoringSafeArea(.all)
            
            // Back button and metadata overlay
            VStack {
                // Back button
                HStack {
                    Button(action: { dismiss() }) {
                        HStack {
                            Image(systemName: "chevron.left")
                            Text("Back")
                        }
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(8)
                    }
                    .padding(.top, 50) // Add padding to move button down from top edge
                    Spacer()
                }
                .padding()
                
                Spacer()
                
                // Metadata overlay
                VStack(alignment: .leading, spacing: 8) {
                    Text(title)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text(description)
                        .font(.body)
                        .foregroundColor(.white)
                        .lineLimit(2)
                }
                .padding()
                .background(
                    LinearGradient(
                        gradient: Gradient(colors: [.black.opacity(0.7), .clear]),
                        startPoint: .bottom,
                        endPoint: .top
                    )
                )
                .padding(.bottom, 60) // Add padding to avoid overlapping with video controls
            }
        }
        .onTapGesture {
            // This ensures the back button is always tappable
            // even when the video controls are hidden
        }
    }
}

struct ContentDetailView: View {
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    @State private var showTrailer = false
    @State private var showContent = false
    @State private var trailerPlayer: AVPlayer?
    @State private var contentPlayer: AVPlayer?
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var isLoading = false
    
    private func getTrailerURL() -> URL? {
        // Use the correct URL for Christie Love
        if content.title.contains("Christie Love") {
            return URL(string: "https://storage.googleapis.com/pecantv_trailers/GetChristieLove_Trailer-final-60s.mp4")
        }
        return URL(string: content.trailerURL)
    }
    
    private func loadVideo(url: URL, isTrailer: Bool) {
        isLoading = true
        print("Loading video from URL: \(url)")
        
        // Create an asset with options
        let asset = AVURLAsset(url: url, options: [
            "AVURLAssetOutOfBandMIMETypeKey": "video/mp4",
            "AVURLAssetHTTPHeaderFieldsKey": [
                "Accept": "video/mp4,video/*;q=0.8,*/*;q=0.5"
            ]
        ])
        
        // Load the asset asynchronously
        asset.loadValuesAsynchronously(forKeys: ["playable"]) {
            DispatchQueue.main.async {
                self.isLoading = false
                
                var error: NSError? = nil
                let status = asset.statusOfValue(forKey: "playable", error: &error)
                
                switch status {
                case .loaded:
                    let playerItem = AVPlayerItem(asset: asset)
                    if isTrailer {
                        self.trailerPlayer = AVPlayer(playerItem: playerItem)
                        self.showTrailer = true
                    } else {
                        self.contentPlayer = AVPlayer(playerItem: playerItem)
                        self.showContent = true
                    }
                case .failed:
                    print("Failed to load video: \(error?.localizedDescription ?? "Unknown error")")
                    self.errorMessage = "Failed to load video: \(error?.localizedDescription ?? "Unknown error")"
                    self.showError = true
                case .cancelled:
                    print("Video loading cancelled")
                    self.errorMessage = "Video loading was cancelled"
                    self.showError = true
                default:
                    print("Unknown error loading video")
                    self.errorMessage = "Unknown error loading video"
                    self.showError = true
                }
            }
        }
    }
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Poster and Info
                    VStack(alignment: .leading, spacing: 16) {
                        AsyncImage(url: URL(string: content.posterURL)) { phase in
                            switch phase {
                            case .empty:
                                Rectangle()
                                    .fill(Color.gray.opacity(0.2))
                                    .aspectRatio(16/9, contentMode: .fit)
                                    .frame(maxWidth: .infinity)
                            case .success(let image):
                                image
                                    .resizable()
                                    .aspectRatio(16/9, contentMode: .fit)
                                    .frame(maxWidth: .infinity)
                            case .failure:
                                Rectangle()
                                    .fill(Color.gray.opacity(0.2))
                                    .aspectRatio(16/9, contentMode: .fit)
                                    .frame(maxWidth: .infinity)
                            @unknown default:
                                EmptyView()
                            }
                        }
                        .cornerRadius(12)
                        .shadow(radius: 5)
                        .frame(maxWidth: .infinity)
                        
                        // Title and Info
                        VStack(alignment: .leading, spacing: 8) {
                            Text(content.title)
                                .font(.title)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            HStack {
                                Text(content.type)
                                Text("•")
                                Text("\(content.runtime) min")
                                Text("•")
                                Text(content.genre)
                                Text("•")
                                Text(content.ageRating)
                            }
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            
                            Text(content.description)
                                .font(.body)
                                .foregroundColor(.white)
                                .padding(.top, 8)
                        }
                        .padding(.horizontal)
                    }
                    
                    // Action Buttons
                    VStack(spacing: 12) {
                        Button(action: {
                            if let url = getTrailerURL() {
                                loadVideo(url: url, isTrailer: true)
                            } else {
                                errorMessage = "Invalid trailer URL"
                                showError = true
                            }
                        }) {
                            HStack {
                                Image(systemName: "play.fill")
                                Text("Watch Trailer")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                        .disabled(isLoading)
                        
                        Button(action: {
                            if let url = URL(string: content.contentURL) {
                                loadVideo(url: url, isTrailer: false)
                            } else {
                                errorMessage = "Invalid content URL"
                                showError = true
                            }
                        }) {
                            HStack {
                                Image(systemName: "play.fill")
                                Text("Watch \(content.type == "Film" ? "Film" : "Series")")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                        .disabled(isLoading)
                    }
                    .padding(.horizontal)
                    .padding(.top, 20)
                    
                    // Bottom spacing for footer
                    Spacer()
                        .frame(height: 60)
                }
                .padding(.vertical)
            }
            
            if isLoading {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    .scaleEffect(1.5)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.black.opacity(0.5))
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
        }
        .fullScreenCover(isPresented: $showTrailer) {
            if let player = trailerPlayer {
                VideoPlayerWithMetadata(
                    player: player,
                    title: content.title,
                    description: content.description
                )
                .edgesIgnoringSafeArea(.all)
                .onAppear {
                    print("Trailer player appeared")
                    player.play()
                }
                .onDisappear {
                    print("Trailer player disappeared")
                    player.pause()
                    trailerPlayer = nil
                }
            }
        }
        .fullScreenCover(isPresented: $showContent) {
            if let player = contentPlayer {
                VideoPlayerWithMetadata(
                    player: player,
                    title: content.title,
                    description: content.description
                )
                .edgesIgnoringSafeArea(.all)
                .onAppear {
                    print("Content player appeared")
                    player.play()
                }
                .onDisappear {
                    print("Content player disappeared")
                    player.pause()
                    contentPlayer = nil
                }
            }
        }
    }
}

#Preview {
    NavigationView {
        ContentDetailView(content: MediaContent(
            id: 1,
            title: "Sample Film",
            posterURL: "https://example.com/poster.jpg",
            trailerURL: "https://example.com/trailer.mp4",
            contentURL: "https://example.com/film.mp4",
            description: "A sample film description",
            type: "Film",
            runtime: 120,
            genre: "Action",
            ageRating: "PG-13"
        ))
    }
} 