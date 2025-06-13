import SwiftUI
import AVKit

struct VideoPlayerView: View {
    let url: URL
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    @State private var player: AVPlayer?
    @State private var showControls = true
    @State private var isLoading = true
    @State private var error: Error?
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            VStack {
                // Back button
                HStack {
                    Button(action: { dismiss() }) {
                        HStack {
                            Image(systemName: "chevron.left")
                            Text("Back")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.black.opacity(0.6))
                        .cornerRadius(20)
                    }
                    Spacer()
                }
                .padding()
                
                if let error = error {
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 48))
                            .foregroundColor(.red)
                        Text("Failed to load video")
                            .font(.headline)
                            .foregroundColor(.white)
                        Text(error.localizedDescription)
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .padding()
                } else if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .scaleEffect(1.5)
                } else if let player = player {
                    VideoPlayer(player: player)
                        .edgesIgnoringSafeArea(.all)
                        .onTapGesture {
                            withAnimation {
                                showControls.toggle()
                            }
                        }
                }
                
                if showControls && !isLoading && error == nil {
                    VStack(spacing: 16) {
                        Text(content.title)
                            .font(.headline)
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
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .padding()
                    .background(Color.black.opacity(0.8))
                }
            }
        }
        .onAppear {
            setupPlayer()
        }
        .onDisappear {
            player?.pause()
            player = nil
        }
    }
    
    private func setupPlayer() {
        isLoading = true
        error = nil
        
        // Create AVPlayerItem with asset
        let asset = AVAsset(url: url)
        let playerItem = AVPlayerItem(asset: asset)
        
        // Create player
        let newPlayer = AVPlayer(playerItem: playerItem)
        
        // Add observer for player item status
        let statusObserver = playerItem.observe(\.status, options: [.new, .initial]) { item, _ in
            DispatchQueue.main.async {
                switch item.status {
                case .readyToPlay:
                    self.isLoading = false
                    newPlayer.play()
                case .failed:
                    self.isLoading = false
                    self.error = item.error
                case .unknown:
                    break
                @unknown default:
                    break
                }
            }
        }
        
        // Store observer to prevent deallocation
        objc_setAssociatedObject(playerItem, "statusObserver", statusObserver, .OBJC_ASSOCIATION_RETAIN)
        
        player = newPlayer
    }
}

#Preview {
    VideoPlayerView(
        url: URL(string: "https://example.com/video.mp4")!,
        content: MediaContent(
            id: 1,
            title: "Sample Video",
            posterURL: "https://example.com/poster.jpg",
            trailerURL: "https://example.com/trailer.mp4",
            contentURL: "https://example.com/video.mp4",
            description: "Sample description",
            type: "FILM",
            runtime: 120,
            genre: "Action",
            ageRating: "PG-13"
        )
    )
} 