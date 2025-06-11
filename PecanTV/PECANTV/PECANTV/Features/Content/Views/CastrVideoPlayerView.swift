import SwiftUI
import AVKit
import WebKit

class PlayerObserver: NSObject {
    var statusObservation: NSKeyValueObservation?
    var player: AVPlayer?
    
    func observe(_ player: AVPlayer, onStatusChange: @escaping (AVPlayerItem.Status) -> Void) {
        self.player = player
        
        statusObservation = player.currentItem?.observe(\.status, options: [.new]) { item, _ in
            DispatchQueue.main.async {
                onStatusChange(item.status)
            }
        }
    }
    
    deinit {
        statusObservation?.invalidate()
        player?.pause()
        player = nil
    }
}

struct CastrVideoPlayerView: View {
    let url: URL
    @Environment(\.dismiss) private var dismiss
    @State private var isLoading = true
    @State private var error: Error?
    @State private var player: AVPlayer?
    @State private var playerObserver: PlayerObserver?
    @State private var isCastrURL: Bool
    
    init(url: URL) {
        self.url = url
        self._isCastrURL = State(initialValue: url.absoluteString.contains("castr.com"))
    }
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            VStack {
                HStack {
                    Button {
                        dismiss()
                    } label: {
                        Image(systemName: "xmark")
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding()
                    }
                    Spacer()
                }
                
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .scaleEffect(1.5)
                }
                
                if let error = error {
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
                
                if isCastrURL {
                    CastrWebView(url: url, isLoading: $isLoading, error: $error)
                        .edgesIgnoringSafeArea(.all)
                } else if let player = player {
                    VideoPlayer(player: player)
                        .edgesIgnoringSafeArea(.all)
                }
            }
        }
        .onAppear {
            if !isCastrURL {
                setupPlayer()
            }
        }
        .onDisappear {
            cleanup()
        }
    }
    
    private func setupPlayer() {
        isLoading = true
        error = nil
        
        // Create AVPlayerItem
        let playerItem = AVPlayerItem(url: url)
        
        // Create player
        let newPlayer = AVPlayer(playerItem: playerItem)
        player = newPlayer
        
        // Setup observer
        let observer = PlayerObserver()
        observer.observe(newPlayer) { status in
            switch status {
            case .readyToPlay:
                isLoading = false
                newPlayer.play()
            case .failed:
                isLoading = false
                error = newPlayer.currentItem?.error ?? NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Failed to load video"])
            case .unknown:
                break
            @unknown default:
                break
            }
        }
        playerObserver = observer
    }
    
    private func cleanup() {
        playerObserver = nil
        player?.pause()
        player = nil
    }
}

struct CastrWebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var error: Error?
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    func makeUIView(context: Context) -> WKWebView {
        let preferences = WKWebpagePreferences()
        preferences.allowsContentJavaScript = true
        
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences = preferences
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []
        configuration.allowsAirPlayForMediaPlayback = true
        
        // Enable background audio and airplay
        configuration.mediaPlaybackAllowsAirPlay = true
        
        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.scrollView.isScrollEnabled = false
        webView.backgroundColor = .black
        webView.isOpaque = false
        
        // Enable fullscreen video
        webView.configuration.allowsInlineMediaPlayback = true
        webView.configuration.mediaTypesRequiringUserActionForPlayback = []
        
        // Add custom CSS to hide Castr's default controls if needed
        let cssString = """
            .castr-player-controls { display: none !important; }
            .castr-player-overlay { display: none !important; }
        """
        let script = WKUserScript(source: cssString, injectionTime: .atDocumentEnd, forMainFrameOnly: false)
        webView.configuration.userContentController.addUserScript(script)
        
        // Set up audio session
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .moviePlayback)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Failed to set up audio session: \(error)")
        }
        
        return webView
    }
    
    func updateUIView(_ webView: WKWebView, context: Context) {
        let request = URLRequest(url: url)
        webView.load(request)
    }
    
    class Coordinator: NSObject, WKNavigationDelegate {
        var parent: CastrWebView
        
        init(_ parent: CastrWebView) {
            self.parent = parent
        }
        
        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            DispatchQueue.main.async {
                self.parent.isLoading = true
                self.parent.error = nil
            }
        }
        
        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            DispatchQueue.main.async {
                self.parent.isLoading = false
            }
        }
        
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            handleError(error)
        }
        
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            handleError(error)
        }
        
        private func handleError(_ error: Error) {
            let nsError = error as NSError
            
            // Ignore cancellation errors (-999)
            if nsError.code == NSURLErrorCancelled {
                return
            }
            
            DispatchQueue.main.async {
                self.parent.isLoading = false
                self.parent.error = error
            }
        }
    }
}

#Preview {
    CastrVideoPlayerView(url: URL(string: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")!)
} 