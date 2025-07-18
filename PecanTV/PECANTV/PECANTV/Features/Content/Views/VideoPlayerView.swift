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
    @State private var isFullScreen = false
    
    var body: some View {
        Group {
            if isFullScreen {
                // Full screen video player
                FullScreenVideoPlayer(
                    url: url,
                    content: content,
                    player: $player,
                    isLoading: $isLoading,
                    error: $error,
                    isFullScreen: $isFullScreen,
                    dismiss: { dismiss() }
                )
            } else {
                // Regular video player
                RegularVideoPlayer(
                    url: url,
                    content: content,
                    player: $player,
                    showControls: $showControls,
                    isLoading: $isLoading,
                    error: $error,
                    isFullScreen: $isFullScreen,
                    dismiss: { dismiss() },
                    setupPlayer: setupPlayer
                )
            }
        }
        .onAppear {
            print("🎬 VideoPlayerView appeared for: \(content.title)")
            setupPlayer()
        }
        .onDisappear {
            print("🎬 VideoPlayerView disappeared for: \(content.title)")
            player?.pause()
            player = nil
        }
        .gesture(
            DragGesture()
                .onEnded { value in
                    // Swipe right to go back (iPad gesture support)
                    if value.translation.width > 100 && abs(value.translation.height) < 50 {
                        print("🔙 Swipe right gesture detected - dismissing video player")
                        player?.pause()
                        player = nil
                        dismiss()
                    }
                }
        )
    }
    
    // MARK: - Error Handling
    
    private func getErrorIcon() -> String {
        if isPermissionError() {
            return "lock.shield"
        } else if isNetworkError() {
            return "wifi.slash"
        } else if isTimeoutError() {
            return "clock"
        } else {
            return "exclamationmark.triangle"
        }
    }
    
    private func getErrorTitle() -> String {
        if isPermissionError() {
            return "Video Not Available"
        } else if isNetworkError() {
            return "Network Error"
        } else if isTimeoutError() {
            return "Loading Timeout"
        } else {
            return "Playback Error"
        }
    }
    
    private func getErrorMessage() -> String {
        if isPermissionError() {
            return "This video requires special access permissions. You can try opening it in your browser, or contact support if you believe this is an error."
        } else if isNetworkError() {
            return "Unable to connect to the video server. Please check your internet connection and try again."
        } else if isTimeoutError() {
            return "The video took too long to load. This might be due to a slow connection or server issues."
        } else {
            return error?.localizedDescription ?? "An unexpected error occurred while trying to play this video."
        }
    }
    
    private func isPermissionError() -> Bool {
        guard let error = error as NSError? else { return false }
        return error.domain == "VideoPlayer" && error.code == -1 ||
               error.localizedDescription.contains("permission") ||
               error.localizedDescription.contains("forbidden") ||
               error.localizedDescription.contains("403")
    }
    
    private func isNetworkError() -> Bool {
        guard let error = error as NSError? else { return false }
        return error.domain == NSURLErrorDomain ||
               error.localizedDescription.contains("network") ||
               error.localizedDescription.contains("connection")
    }
    
    private func isTimeoutError() -> Bool {
        guard let error = error as NSError? else { return false }
        return error.domain == "VideoPlayer" && error.code == -2 ||
               error.localizedDescription.contains("timeout") ||
               error.localizedDescription.contains("timed out")
    }
    
    // MARK: - Player Setup
    
    private func setupPlayer() {
        // Clean up existing player first
        player?.pause()
        player = nil
        
        isLoading = true
        error = nil
        
        print("🎬 Setting up player for: \(content.title)")
        print("🎬 URL: \(url)")
        
        // Create player with timeout
        createPlayerWithTimeout()
    }
    
    private func createPlayerWithTimeout() {
        // Create AVPlayerItem with asset
        let asset = AVURLAsset(url: url)
        let playerItem = AVPlayerItem(asset: asset)
        
        // Configure player item
        playerItem.canUseNetworkResourcesForLiveStreamingWhilePaused = true
        playerItem.preferredForwardBufferDuration = 10.0
        
        // Create player
        let newPlayer = AVPlayer(playerItem: playerItem)
        newPlayer.automaticallyWaitsToMinimizeStalling = true
        
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
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                            newPlayer.play()
                        }
                    }
                case .failed:
                    print("❌ Video failed to load for: \(self.content.title)")
                    self.isLoading = false
                    
                    // Create a more specific error message
                    let errorMessage: String
                    if let itemError = item.error {
                        errorMessage = itemError.localizedDescription
                    } else {
                        errorMessage = "Failed to load video"
                    }
                    
                    self.error = NSError(domain: "VideoPlayer", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])
                case .unknown:
                    print("⏳ Video status unknown for: \(self.content.title)")
                @unknown default:
                    break
                }
            }
        }
        
        // Store observer
        objc_setAssociatedObject(playerItem, "statusObserver", statusObserver, .OBJC_ASSOCIATION_RETAIN)
        
        player = newPlayer
        
        // Timeout: if not ready after 10 seconds, show error
        DispatchQueue.main.asyncAfter(deadline: .now() + 10.0) {
            if self.isLoading {
                print("⏰ Video loading timeout for: \(self.content.title)")
                DispatchQueue.main.async {
                    self.isLoading = false
                    self.error = NSError(domain: "VideoPlayer", code: -2, userInfo: [NSLocalizedDescriptionKey: "Video loading timed out"])
                }
            }
        }
    }
}

// MARK: - Regular Video Player

struct RegularVideoPlayer: View {
    let url: URL
    let content: MediaContent
    @Binding var player: AVPlayer?
    @Binding var showControls: Bool
    @Binding var isLoading: Bool
    @Binding var error: Error?
    @Binding var isFullScreen: Bool
    let dismiss: () -> Void
    let setupPlayer: () -> Void
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            VStack {
                // Simplified back button - single, clear implementation
                HStack {
                    Button(action: { 
                        print("🔙 Back button tapped - dismissing video player")
                        player?.pause()
                        player = nil
                        dismiss() 
                    }) {
                        HStack(spacing: 8) {
                            Image(systemName: "chevron.left")
                                .font(.title2)
                            Text("Back")
                                .font(.headline)
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(20)
                    }
                    .buttonStyle(PlainButtonStyle())
                    .accessibilityLabel("Back to previous screen")
                    
                    Spacer()
                    
                    // Close button for additional accessibility
                    Button(action: { 
                        print("🔙 Close button tapped - dismissing video player")
                        player?.pause()
                        player = nil
                        dismiss() 
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding(8)
                            .background(Color.black.opacity(0.6))
                            .clipShape(Circle())
                    }
                    .buttonStyle(PlainButtonStyle())
                    .accessibilityLabel("Close video player")
                }
                .padding()
                .zIndex(1000) // Ensure back button is always on top
                
                if isLoading {
                    VStack {
                        ProgressView("Loading video...")
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .foregroundColor(.white)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if error != nil {
                    // Error state with working back button
                    VStack(spacing: 20) {
                        Image(systemName: getErrorIcon())
                            .font(.system(size: 64))
                            .foregroundColor(.red)
                        
                        Text(getErrorTitle())
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .multilineTextAlignment(.center)
                        
                        Text(getErrorMessage())
                            .font(.body)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                        
                        // Action buttons
                        VStack(spacing: 12) {
                            Button("Try Again") {
                                setupPlayer()
                            }
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                            
                            Button("Open in Browser") {
                                UIApplication.shared.open(url)
                            }
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                            
                            Button("Go Back") {
                                print("🔙 Error state back button tapped")
                                dismiss()
                            }
                            .padding()
                            .background(Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .padding()
                } else if let player = player {
                    ZStack {
                        VideoPlayer(player: player)
                            .edgesIgnoringSafeArea(.all)
                            .onTapGesture {
                                withAnimation {
                                    showControls.toggle()
                                }
                            }
                        
                        // Floating back button when controls are hidden
                        if !showControls {
                            VStack {
                                HStack {
                                    Button(action: {
                                        print("🔙 Floating back button tapped")
                                        player.pause()
                                        dismiss()
                                    }) {
                                        Image(systemName: "xmark.circle.fill")
                                            .font(.title)
                                            .foregroundColor(.white)
                                            .background(Color.black.opacity(0.6))
                                            .clipShape(Circle())
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                    
                                    Spacer()
                                }
                                .padding()
                                Spacer()
                            }
                        }
                    }
                }
                
                if showControls && !isLoading && error == nil {
                    VStack(spacing: 16) {
                        HStack {
                            Text(content.title)
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            Spacer()
                            
                            // Full Screen Button
                            Button(action: {
                                withAnimation(.easeInOut(duration: 0.3)) {
                                    isFullScreen = true
                                }
                            }) {
                                Image(systemName: "arrow.up.left.and.arrow.down.right")
                                    .font(.title2)
                                    .foregroundColor(.white)
                                    .padding(8)
                                    .background(Color.black.opacity(0.6))
                                    .clipShape(Circle())
                            }
                        }
                        
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
                        
                        // Video controls
                        HStack(spacing: 20) {
                            Button(action: {
                                if player?.timeControlStatus == .playing {
                                    player?.pause()
                                } else {
                                    player?.play()
                                }
                            }) {
                                Image(systemName: player?.timeControlStatus == .playing ? "pause.fill" : "play.fill")
                                    .font(.title2)
                                    .foregroundColor(.white)
                                    .padding(12)
                                    .background(Color.black.opacity(0.6))
                                    .clipShape(Circle())
                            }
                            
                            Spacer()
                            
                            // Additional back button in controls
                            Button(action: {
                                print("🔙 Controls back button tapped")
                                player?.pause()
                                player = nil
                                dismiss()
                            }) {
                                HStack {
                                    Image(systemName: "chevron.left")
                                    Text("Exit")
                                }
                                .font(.subheadline)
                                .foregroundColor(.white)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(Color.black.opacity(0.6))
                                .cornerRadius(15)
                            }
                        }
                    }
                    .padding()
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.black.opacity(0.8), Color.clear]),
                            startPoint: .bottom,
                            endPoint: .top
                        )
                    )
                }
            }
        }
        .onTapGesture {
            if !isLoading && error == nil {
                withAnimation {
                    showControls.toggle()
                }
            }
        }
        .gesture(
            DragGesture()
                .onEnded { value in
                    // Swipe right to go back (iPad gesture support)
                    if value.translation.width > 100 && abs(value.translation.height) < 50 {
                        print("🔙 Swipe right gesture detected - dismissing video player")
                        player?.pause()
                        player = nil
                        dismiss()
                    }
                }
        )
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
            // Pause video when app goes to background
            player?.pause()
        }
    }
    
    // MARK: - Error Handling
    
    private func getErrorIcon() -> String {
        if isPermissionError() {
            return "lock.shield"
        } else if isNetworkError() {
            return "wifi.slash"
        } else if isTimeoutError() {
            return "clock"
        } else {
            return "exclamationmark.triangle"
        }
    }
    
    private func getErrorTitle() -> String {
        if isPermissionError() {
            return "Access Restricted"
        } else if isNetworkError() {
            return "Connection Error"
        } else if isTimeoutError() {
            return "Loading Timeout"
        } else {
            return "Playback Error"
        }
    }
    
    private func getErrorMessage() -> String {
        if isPermissionError() {
            return "This video requires special access permissions. You can try opening it in your browser, or contact support if you believe this is an error."
        } else if isNetworkError() {
            return "Unable to connect to the video server. Please check your internet connection and try again."
        } else if isTimeoutError() {
            return "The video took too long to load. This might be due to a slow connection or server issues."
        } else {
            return error?.localizedDescription ?? "An unexpected error occurred while trying to play this video."
        }
    }
    
    private func isPermissionError() -> Bool {
        guard let error = error as NSError? else { return false }
        return error.domain == "VideoPlayer" && error.code == -1 ||
               error.localizedDescription.contains("permission") ||
               error.localizedDescription.contains("forbidden") ||
               error.localizedDescription.contains("403")
    }
    
    private func isNetworkError() -> Bool {
        guard let error = error as NSError? else { return false }
        return error.domain == NSURLErrorDomain ||
               error.localizedDescription.contains("network") ||
               error.localizedDescription.contains("connection")
    }
    
    private func isTimeoutError() -> Bool {
        guard let error = error as NSError? else { return false }
        return error.domain == "VideoPlayer" && error.code == -2 ||
               error.localizedDescription.contains("timeout") ||
               error.localizedDescription.contains("timed out")
    }
}

// MARK: - Full Screen Video Player

struct FullScreenVideoPlayer: View {
    let url: URL
    let content: MediaContent
    @Binding var player: AVPlayer?
    @Binding var isLoading: Bool
    @Binding var error: Error?
    @Binding var isFullScreen: Bool
    let dismiss: () -> Void
    @State private var showControls = true
    @State private var controlsTimer: Timer?
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            if isLoading {
                VStack {
                    ProgressView("Loading video...")
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .foregroundColor(.white)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = error {
                // Error state in full screen
                VStack(spacing: 20) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 64))
                        .foregroundColor(.red)
                    
                    Text("Playback Error")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                    
                    Text(error.localizedDescription)
                        .font(.body)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                    
                    Button("Exit Full Screen") {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            isFullScreen = false
                        }
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .padding()
            } else if let player = player {
                VideoPlayer(player: player)
                    .edgesIgnoringSafeArea(.all)
                    .onTapGesture {
                        toggleControls()
                    }
                    .gesture(
                        DragGesture()
                            .onEnded { value in
                                // Swipe down to exit full screen
                                if value.translation.height > 100 && abs(value.translation.width) < 50 {
                                    print("🔙 Swipe down gesture detected - exiting full screen")
                                    withAnimation(.easeInOut(duration: 0.3)) {
                                        isFullScreen = false
                                    }
                                }
                            }
                    )
            }
            
            // Full screen controls overlay
            if showControls && !isLoading && error == nil {
                VStack {
                    // Top controls
                    HStack {
                        Button(action: {
                            print("🔙 Full screen exit button tapped")
                            withAnimation(.easeInOut(duration: 0.3)) {
                                isFullScreen = false
                            }
                        }) {
                            HStack(spacing: 8) {
                                Image(systemName: "chevron.left")
                                Text("Exit")
                            }
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(Color.black.opacity(0.7))
                            .cornerRadius(20)
                        }
                        
                        Spacer()
                        
                        Text(content.title)
                            .font(.headline)
                            .foregroundColor(.white)
                            .lineLimit(1)
                        
                        Spacer()
                        
                        Button(action: {
                            UIApplication.shared.open(url)
                        }) {
                            Image(systemName: "safari")
                                .font(.title2)
                                .foregroundColor(.white)
                                .padding(12)
                                .background(Color.black.opacity(0.6))
                                .clipShape(Circle())
                        }
                    }
                    .padding()
                    
                    Spacer()
                    
                    // Bottom controls
                    VStack(spacing: 12) {
                        HStack {
                            Text(content.type)
                            Text("•")
                            Text("\(content.runtime) min")
                            if !content.genre.isEmpty && content.genre != "Unknown" {
                                Text("•")
                                Text(content.genre)
                            }
                        }
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        
                        Text(content.description)
                            .font(.body)
                            .foregroundColor(.white)
                            .multilineTextAlignment(.center)
                            .lineLimit(3)
                            .padding(.horizontal)
                    }
                    .padding()
                    .background(Color.black.opacity(0.8))
                }
            }
            
            // Always show exit button in top-left corner, even when controls are hidden
            if !showControls && !isLoading && error == nil {
                VStack {
                    HStack {
                        Button(action: {
                            print("🔙 Hidden exit button tapped")
                            withAnimation(.easeInOut(duration: 0.3)) {
                                isFullScreen = false
                            }
                        }) {
                            Image(systemName: "chevron.left")
                                .font(.title2)
                                .foregroundColor(.white)
                                .padding(12)
                                .background(Color.black.opacity(0.7))
                                .clipShape(Circle())
                        }
                        Spacer()
                    }
                    .padding()
                    Spacer()
                }
            }
        }
        .onAppear {
            // Auto-hide controls after 3 seconds
            startControlsTimer()
        }
        .onDisappear {
            stopControlsTimer()
        }
    }
    
    private func toggleControls() {
        withAnimation(.easeInOut(duration: 0.3)) {
            showControls.toggle()
        }
        
        if showControls {
            startControlsTimer()
        } else {
            stopControlsTimer()
        }
    }
    
    private func startControlsTimer() {
        stopControlsTimer()
        controlsTimer = Timer.scheduledTimer(withTimeInterval: 3.0, repeats: false) { _ in
            withAnimation(.easeInOut(duration: 0.3)) {
                showControls = false
            }
        }
    }
    
    private func stopControlsTimer() {
        controlsTimer?.invalidate()
        controlsTimer = nil
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