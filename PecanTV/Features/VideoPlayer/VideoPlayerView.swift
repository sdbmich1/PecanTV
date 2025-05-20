import SwiftUI
import AVKit

struct VideoPlayerView: View {
    let content: Content
    @Environment(\.dismiss) private var dismiss
    @State private var player: AVPlayer?
    @State private var isPlaying = false
    @State private var showControls = true
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            if let player = player {
                VideoPlayer(player: player)
                    .edgesIgnoringSafeArea(.all)
                    .onTapGesture {
                        withAnimation {
                            showControls.toggle()
                        }
                    }
            }
            
            if showControls {
                VStack {
                    HStack {
                        Button(action: {
                            dismiss()
                        }) {
                            Image(systemName: "xmark")
                                .font(.title2)
                                .foregroundColor(.white)
                                .padding()
                        }
                        
                        Spacer()
                        
                        Text(content.title)
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        Spacer()
                    }
                    .padding()
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.black.opacity(0.7), Color.clear]),
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    
                    Spacer()
                    
                    HStack(spacing: 40) {
                        Button(action: {
                            player?.seek(to: CMTime(seconds: -10, preferredTimescale: 1))
                        }) {
                            Image(systemName: "gobackward.10")
                                .font(.title)
                                .foregroundColor(.white)
                        }
                        
                        Button(action: {
                            if isPlaying {
                                player?.pause()
                            } else {
                                player?.play()
                            }
                            isPlaying.toggle()
                        }) {
                            Image(systemName: isPlaying ? "pause.fill" : "play.fill")
                                .font(.title)
                                .foregroundColor(.white)
                        }
                        
                        Button(action: {
                            player?.seek(to: CMTime(seconds: 10, preferredTimescale: 1))
                        }) {
                            Image(systemName: "goforward.10")
                                .font(.title)
                                .foregroundColor(.white)
                        }
                    }
                    .padding()
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.clear, Color.black.opacity(0.7)]),
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
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
        let playerItem = AVPlayerItem(url: content.videoURL)
        player = AVPlayer(playerItem: playerItem)
        player?.play()
        isPlaying = true
    }
}

#Preview {
    VideoPlayerView(content: Content(
        id: "1",
        title: "Sample Movie",
        type: .movie,
        description: "A sample movie description",
        releaseDate: Date(),
        duration: 120,
        genres: ["Action", "Drama"],
        rating: 8.5,
        posterURL: URL(string: "https://example.com/poster.jpg")!,
        backdropURL: URL(string: "https://example.com/backdrop.jpg")!,
        videoURL: URL(string: "https://example.com/video.mp4")!,
        trailerURL: URL(string: "https://example.com/trailer.mp4"),
        cast: [
            CastMember(id: "1", name: "John Doe", character: "Lead Actor", profileImageURL: nil)
        ],
        director: "Jane Smith",
        seasons: nil
    ))
} 