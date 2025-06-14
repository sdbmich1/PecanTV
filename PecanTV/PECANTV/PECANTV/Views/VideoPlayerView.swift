import SwiftUI
import AVKit

struct VideoPlayerView: View {
    let url: URL
    @Environment(\.dismiss) private var dismiss
    @State private var player: AVPlayer?
    @State private var isLoading = true
    @State private var error: Error?
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            if let player = player {
                VideoPlayer(player: player)
                    .edgesIgnoringSafeArea(.all)
            } else if isLoading {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle())
                    .scaleEffect(1.5)
            } else if let error = error {
                VStack {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundColor(.red)
                    Text("Error loading video")
                        .foregroundColor(.white)
                    Text(error.localizedDescription)
                        .foregroundColor(.gray)
                        .font(.caption)
                    Button("Try Again") {
                        loadVideo()
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
            }
            
            // Close button
            VStack {
                HStack {
                    Spacer()
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark")
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding(8)
                            .background(Color.black.opacity(0.6))
                            .clipShape(Circle())
                    }
                    .padding()
                }
                Spacer()
            }
        }
        .onAppear {
            loadVideo()
        }
        .onDisappear {
            player?.pause()
            player = nil
        }
    }
    
    private func loadVideo() {
        isLoading = true
        error = nil
        
        // Create AVPlayerItem with the URL
        let playerItem = AVPlayerItem(url: url)
        
        // Add observer for loading status
        playerItem.addObserver(playerItem, forKeyPath: "status", options: [.new], context: nil)
        
        // Create player
        player = AVPlayer(playerItem: playerItem)
        
        // Start playback
        player?.play()
        
        // Set loading to false after a short delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            isLoading = false
        }
    }
}

#Preview {
    VideoPlayerView(url: URL(string: "https://storage.googleapis.com/pecantv_trailers/GetChristieLove_Trailer_35sFinal.mp4")!)
} 