import SwiftUI
import AVKit
import ObjectiveC

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
                
                if isLoading {
                    VStack {
                        ProgressView("Loading video...")
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .foregroundColor(.white)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error = error {
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
                        
                        Button("Try Again") {
                            setupPlayer()
                        }
                        .padding()
                        .background(Color.pecanRed)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
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
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, alignment: .leading)
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
        // Clean up existing player first
        player?.pause()
        player = nil
        
        isLoading = true
        error = nil
        
        print("🎬 Setting up player for: \(content.title)")
        print("🎬 URL: \(url)")
        
        // Test network connectivity first
        testNetworkConnectivity { isConnected in
            if !isConnected {
                print("❌ No network connectivity")
                DispatchQueue.main.async {
                    self.isLoading = false
                    self.error = NSError(domain: "VideoPlayer", code: -1, userInfo: [NSLocalizedDescriptionKey: "No network connectivity"])
                }
                return
            }
            
            DispatchQueue.main.async {
                self.createPlayer()
            }
        }
    }
    
    private func createPlayer() {
        // Create AVPlayerItem with asset
        let asset = AVURLAsset(url: url)
        let playerItem = AVPlayerItem(asset: asset)
        
        // Configure player item for better buffering
        playerItem.canUseNetworkResourcesForLiveStreamingWhilePaused = true
        playerItem.preferredForwardBufferDuration = 15.0 // Increased to 15 seconds
        
        // Create player with minimal configuration
        let newPlayer = AVPlayer(playerItem: playerItem)
        newPlayer.automaticallyWaitsToMinimizeStalling = true // Changed to true for better buffering
        
        var didStartPlayback = false
        
        // Add observer for player item status
        let statusObserver = playerItem.observe(\.status, options: [.new, .initial]) { item, _ in
            DispatchQueue.main.async {
                print("🎬 Status changed for \(self.content.title): \(item.status.rawValue)")
                switch item.status {
                case .readyToPlay:
                    print("✅ Video ready to play for: \(self.content.title)")
                    self.isLoading = false
                    if !didStartPlayback {
                        didStartPlayback = true
                        // Add a small delay to ensure buffering
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                            newPlayer.play()
                        }
                    }
                case .failed:
                    print("❌ Video failed to load for: \(self.content.title)")
                    if let error = item.error {
                        print("❌ Error details: \(error.localizedDescription)")
                    }
                    self.isLoading = false
                    self.error = item.error
                case .unknown:
                    print("⏳ Video status unknown for: \(self.content.title)")
                @unknown default:
                    break
                }
            }
        }
        
        // Add observer for playback buffer
        let bufferObserver = playerItem.observe(\.loadedTimeRanges, options: [.new]) { item, _ in
            let ranges = item.loadedTimeRanges
            if let range = ranges.first {
                let duration = CMTimeGetSeconds(range.timeRangeValue.duration)
                print("📊 Buffered duration: \(duration)s for \(self.content.title)")
                // If we have at least 5 seconds buffered and not started, play
                if duration > 5.0 && !didStartPlayback {
                    print("🎬 Starting playback with buffer: \(duration)s")
                    DispatchQueue.main.async {
                        self.isLoading = false
                        didStartPlayback = true
                        newPlayer.play()
                    }
                }
            }
        }
        
        // Add observer for playback stall
        let stallObserver = playerItem.observe(\.isPlaybackLikelyToKeepUp, options: [.new]) { item, _ in
            DispatchQueue.main.async {
                if !item.isPlaybackLikelyToKeepUp {
                    print("⚠️ Playback likely to stall for: \(self.content.title)")
                } else {
                    print("✅ Playback likely to keep up for: \(self.content.title)")
                }
            }
        }
        
        // Store observers to prevent deallocation
        objc_setAssociatedObject(playerItem, "statusObserver", statusObserver, .OBJC_ASSOCIATION_RETAIN)
        objc_setAssociatedObject(playerItem, "bufferObserver", bufferObserver, .OBJC_ASSOCIATION_RETAIN)
        objc_setAssociatedObject(playerItem, "stallObserver", stallObserver, .OBJC_ASSOCIATION_RETAIN)
        
        player = newPlayer
        
        // Fallback: if not started after 8 seconds, try to play anyway
        DispatchQueue.main.asyncAfter(deadline: .now() + 8.0) {
            if !didStartPlayback {
                print("🎬 Fallback: attempting to play after 8 second timeout")
                self.isLoading = false
                didStartPlayback = true
                newPlayer.play()
            }
        }
    }
    
    private func testNetworkConnectivity(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "https://www.apple.com") else {
            completion(false)
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { _, response, error in
            let isConnected = error == nil && (response as? HTTPURLResponse)?.statusCode == 200
            completion(isConnected)
        }
        task.resume()
    }
}

#Preview {
    VideoPlayerView(
        url: URL(string: "https://example.com/video.mp4")!,
        content: MediaContent(
            id: 1,
            title: "Sample Video",
            description: "Sample description",
            posterURL: "https://example.com/poster.jpg",
            trailerURL: "https://example.com/trailer.mp4",
            contentURL: "https://example.com/content.mp4",
            type: "FILM",
            runtime: 120,
            genre: "Action",
            ageRating: "PG-13"
        )
    )
} 