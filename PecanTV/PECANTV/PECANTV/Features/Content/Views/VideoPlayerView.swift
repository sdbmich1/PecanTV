import SwiftUI
import AVKit

class VideoPlayerViewModel: ObservableObject {
    @Published var isLoading = true
    @Published var error: Error?
    @Published var isPaused = false
    private var player: AVPlayer?
    private var playerItem: AVPlayerItem?
    private var playerItemStatusObserver: NSKeyValueObservation?
    private var timeObserver: Any?
    
    func setupPlayer(with url: URL) {
        isLoading = true
        error = nil
        
        // Set up audio session
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .moviePlayback)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Failed to set up audio session: \(error)")
        }
        
        // Create player item
        let newPlayerItem = AVPlayerItem(url: url)
        
        // Create player
        let newPlayer = AVPlayer(playerItem: newPlayerItem)
        
        // Add observer for player item status
        playerItemStatusObserver = newPlayerItem.observe(\.status, options: [.new, .initial]) { [weak self] item, _ in
            DispatchQueue.main.async {
                switch item.status {
                case .readyToPlay:
                    self?.isLoading = false
                    newPlayer.play()
                case .failed:
                    self?.error = item.error
                    self?.isLoading = false
                case .unknown:
                    break
                @unknown default:
                    break
                }
            }
        }
        
        // Add observer for playback finished
        NotificationCenter.default.addObserver(forName: .AVPlayerItemDidPlayToEndTime, object: newPlayerItem, queue: .main) { [weak self] _ in
            newPlayer.seek(to: .zero)
            newPlayer.play()
        }
        
        // Add time observer to check for pauses
        timeObserver = newPlayer.addPeriodicTimeObserver(forInterval: CMTime(seconds: 0.5, preferredTimescale: 600), queue: .main) { [weak self] _ in
            self?.isPaused = newPlayer.rate == 0
        }
        
        player = newPlayer
        playerItem = newPlayerItem
    }
    
    func cleanup() {
        if let player = player {
            player.pause()
            player.replaceCurrentItem(with: nil)
        }
        
        if let timeObserver = timeObserver {
            player?.removeTimeObserver(timeObserver)
        }
        
        playerItemStatusObserver?.invalidate()
        playerItemStatusObserver = nil
        
        player = nil
        playerItem = nil
        
        // Deactivate audio session
        do {
            try AVAudioSession.sharedInstance().setActive(false)
        } catch {
            print("Failed to deactivate audio session: \(error)")
        }
    }
    
    func getPlayer() -> AVPlayer? {
        return player
    }
}

struct VideoPlayerView: View {
    let url: URL
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = VideoPlayerViewModel()
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            VStack {
                HStack {
                    Button {
                        viewModel.cleanup()
                        dismiss()
                    } label: {
                        Image(systemName: "xmark")
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding()
                    }
                    Spacer()
                }
                
                if viewModel.isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .scaleEffect(1.5)
                }
                
                if let error = viewModel.error {
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.white)
                        Text("Failed to load video")
                            .foregroundColor(.white)
                        Text(error.localizedDescription)
                            .foregroundColor(.white.opacity(0.7))
                            .font(.caption)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                }
                
                if let player = viewModel.getPlayer() {
                    ZStack {
                        VideoPlayer(player: player)
                            .edgesIgnoringSafeArea(.all)
                        
                        if viewModel.isPaused {
                            VStack(alignment: .leading, spacing: 16) {
                                Text(content.title)
                                    .font(.title)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                
                                HStack {
                                    Text(content.type)
                                        .font(.subheadline)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(Color.blue.opacity(0.2))
                                        .cornerRadius(4)
                                    
                                    Text("\(content.runtime) min")
                                        .font(.subheadline)
                                        .foregroundColor(.gray)
                                    
                                    Text(content.ageRating)
                                        .font(.subheadline)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(Color.gray.opacity(0.2))
                                        .cornerRadius(4)
                                }
                                
                                Text(content.genre)
                                    .font(.subheadline)
                                    .foregroundColor(.gray)
                                
                                Text(content.description)
                                    .font(.body)
                                    .foregroundColor(.white)
                                    .lineLimit(4)
                                
                                Button {
                                    viewModel.getPlayer()?.play()
                                } label: {
                                    HStack {
                                        Image(systemName: "play.fill")
                                        Text("Resume Playback")
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.blue)
                                    .foregroundColor(.white)
                                    .cornerRadius(10)
                                }
                            }
                            .padding()
                            .background(Color.black.opacity(0.8))
                            .cornerRadius(12)
                            .padding()
                        }
                    }
                }
            }
        }
        .onAppear {
            viewModel.setupPlayer(with: url)
        }
        .onDisappear {
            viewModel.cleanup()
        }
    }
}

#Preview {
    VideoPlayerView(
        url: URL(string: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1")!,
        content: MediaContent(
            id: 1,
            title: "Get Christie Love",
            posterURL: "https://example.com/poster.jpg",
            trailerURL: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1",
            contentURL: "https://example.com/film.mp4",
            description: "A groundbreaking crime drama series following the adventures of Christie Love, a stylish and tough undercover police detective.",
            type: "SERIES",
            runtime: 60,
            genre: "Crime",
            ageRating: "TV-14"
        )
    )
} 