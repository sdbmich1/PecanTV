import SwiftUI
import AVKit
import WebKit

struct ContentDetailView: View {
    let content: MediaContent
    @ObservedObject var favoritesManager: FavoritesManager
    @Environment(\.dismiss) private var dismiss
    @State private var showEpisodes = false
    @State private var showTrailer = false
    @State private var showContent = false
    
    var body: some View {
        ZStack {
            Color.white.edgesIgnoringSafeArea(.all)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
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
                    
                    // Poster and Info
                    VStack(alignment: .leading, spacing: 16) {
                        ZStack(alignment: .topTrailing) {
                            AsyncImage(url: URL(string: content.posterURL)) { phase in
                                switch phase {
                                case .empty:
                                    Rectangle()
                                        .fill(Color.gray.opacity(0.2))
                                        .frame(width: UIScreen.main.bounds.width - 8)
                                        .frame(height: 240)
                                        .overlay(
                                            Image(systemName: "photo")
                                                .font(.system(size: 48))
                                                .foregroundColor(.gray)
                                        )
                                case .success(let image):
                                    image
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                        .frame(width: UIScreen.main.bounds.width - 8)
                                        .frame(height: 240)
                                        .clipped()
                                case .failure:
                                    Rectangle()
                                        .fill(Color.gray.opacity(0.2))
                                        .frame(width: UIScreen.main.bounds.width - 8)
                                        .frame(height: 240)
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
                            
                            // Favorite button
                            Button(action: {
                                favoritesManager.toggleFavorite(content)
                            }) {
                                Image(systemName: favoritesManager.isFavorite(content) ? "heart.fill" : "heart")
                                    .font(.title2)
                                    .foregroundColor(favoritesManager.isFavorite(content) ? .pecanRed : .black)
                                    .padding(12)
                                    .background(Color.gray.opacity(0.2))
                                    .clipShape(Circle())
                            }
                            .padding(.top, 12)
                            .padding(.trailing, 12)
                        }
                        
                        // Content info
                        VStack(alignment: .leading, spacing: 12) {
                            Text(content.title)
                                .font(.title)
                                .fontWeight(.bold)
                                .foregroundColor(.black)
                            
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
                                .foregroundColor(.black)
                                .lineLimit(nil)
                                .multilineTextAlignment(.leading)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .padding(.horizontal, 16)
                        
                        // Action buttons
                        VStack(spacing: 12) {
                            if content.type.uppercased() == "SERIES" {
                                // Episodes button for series
                                Button(action: { showEpisodes = true }) {
                                    HStack {
                                        Image(systemName: "tv")
                                        Text("Episodes")
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.pecanRed)
                                    .foregroundColor(.white)
                                    .cornerRadius(10)
                                }
                            } else {
                                // Trailer and Film buttons for non-series content
                                Button(action: { 
                                    print("🎬 Trailer button tapped for: \(content.title) (ID: \(content.id))")
                                    print("🎬 Trailer URL: \(content.trailerURL)")
                                    showTrailer = true 
                                }) {
                                    HStack {
                                        Image(systemName: "play.fill")
                                        Text("Watch Trailer")
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(content.trailerURL.isEmpty ? Color.gray : Color.blue)
                                    .foregroundColor(.white)
                                    .cornerRadius(10)
                                }
                                .disabled(content.trailerURL.isEmpty)
                                .allowsHitTesting(!content.trailerURL.isEmpty)
                                
                                Button(action: { showContent = true }) {
                                    HStack {
                                        Image(systemName: "play.fill")
                                        Text("Watch Film")
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.pecanRed)
                                    .foregroundColor(.white)
                                    .cornerRadius(10)
                                }
                            }
                        }
                        .padding(.horizontal, 16)
                        .padding(.top, 20)
                    }
                    .padding(.vertical)
                }
            }
        }
        .navigationBarHidden(true)
        .fullScreenCover(isPresented: $showEpisodes) {
            EpisodesView(series: content)
                .environmentObject(favoritesManager)
        }
        .fullScreenCover(isPresented: $showTrailer) {
            Group {
                if content.trailerURL.isEmpty {
                    TrailerErrorView(content: content)
                } else if let url = URL(string: content.trailerURL) {
                    // Check if it's a direct video URL or a player URL
                    if content.trailerURL.contains(".mp4") || content.trailerURL.contains(".mov") || content.trailerURL.contains(".m4v") {
                        VideoPlayerView(url: url, content: content)
                    } else {
                        // For player URLs like Castr, show a web view or error message
                        TrailerWebView(url: url, content: content)
                    }
                } else {
                    // Show error if URL is invalid
                    TrailerErrorView(content: content)
                }
            }
        }
        .fullScreenCover(isPresented: $showContent) {
            Group {
                if let url = URL(string: content.contentURL) {
                    // Check if it's a direct video URL or a player URL
                    if content.contentURL.contains(".mp4") || content.contentURL.contains(".mov") || content.contentURL.contains(".m4v") {
                        VideoPlayerView(url: url, content: content)
                    } else {
                        // For player URLs like Castr, show a web view or error message
                        TrailerWebView(url: url, content: content)
                    }
                } else {
                    // Show error if URL is invalid
                    ContentErrorView(content: content)
                }
            }
        }
    }
}

struct ContentErrorView: View {
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Color.white.edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 20) {
                // Back button
                HStack {
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
                    
                    Spacer()
                }
                .padding(.horizontal)
                .padding(.top, 8)
                
                Spacer()
                
                VStack(spacing: 16) {
                    Image(systemName: content.contentURL.isEmpty ? "video.slash" : "exclamationmark.triangle")
                        .font(.system(size: 64))
                        .foregroundColor(content.contentURL.isEmpty ? .gray : .red)
                    
                    Text(content.contentURL.isEmpty ? "No Content Available" : "Unable to play content")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.black)
                    
                    Text(content.contentURL.isEmpty ? "This content doesn't have a video file available." : "The content URL is invalid or unavailable.")
                        .font(.body)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                    
                    if let url = URL(string: content.contentURL), !content.contentURL.isEmpty {
                        Button("Open in Browser") {
                            UIApplication.shared.open(url)
                        }
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                }
                
                Spacer()
            }
        }
    }
}

struct TrailerErrorView: View {
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Color.white.edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 20) {
                // Back button
                HStack {
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
                    
                    Spacer()
                }
                .padding(.horizontal)
                .padding(.top, 8)
                
                Spacer()
                
                VStack(spacing: 16) {
                    Image(systemName: content.trailerURL.isEmpty ? "video.slash" : "exclamationmark.triangle")
                        .font(.system(size: 64))
                        .foregroundColor(content.trailerURL.isEmpty ? .gray : .red)
                    
                    Text(content.trailerURL.isEmpty ? "No Trailer Available" : "Unable to play trailer")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.black)
                    
                    Text(content.trailerURL.isEmpty ? "This content doesn't have a trailer available." : "The trailer URL is invalid or unavailable.")
                        .font(.body)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                    
                    if let url = URL(string: content.trailerURL), !content.trailerURL.isEmpty {
                        Button("Open in Browser") {
                            UIApplication.shared.open(url)
                        }
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                }
                
                Spacer()
            }
        }
    }
}

struct TrailerWebView: View {
    let url: URL
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    @State private var isLoading = true
    @State private var error: Error?
    
    var body: some View {
        ZStack {
            Color.white.edgesIgnoringSafeArea(.all)
            
            VStack {
                // Back button
                HStack {
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
                    
                    Spacer()
                    
                    Button(action: {
                        UIApplication.shared.open(url)
                    }) {
                        HStack {
                            Image(systemName: "safari")
                            Text("Open in Browser")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.blue)
                        .cornerRadius(20)
                    }
                }
                .padding(.horizontal)
                .padding(.top, 8)
                
                if isLoading {
                    VStack {
                        ProgressView("Loading trailer...")
                            .progressViewStyle(CircularProgressViewStyle(tint: .black))
                            .foregroundColor(.black)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error = error {
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 48))
                            .foregroundColor(.red)
                        
                        Text("Unable to play trailer")
                            .font(.headline)
                            .foregroundColor(.black)
                        
                        Text(error.localizedDescription)
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                        
                        Button("Open in Browser") {
                            UIApplication.shared.open(url)
                        }
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    WebView(url: url, isLoading: $isLoading, error: $error)
                }
            }
        }
    }
}

struct WebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var error: Error?
    
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true
        return webView
    }
    
    func updateUIView(_ webView: WKWebView, context: Context) {
        let request = URLRequest(url: url)
        webView.load(request)
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, WKNavigationDelegate {
        let parent: WebView
        
        init(_ parent: WebView) {
            self.parent = parent
        }
        
        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            parent.isLoading = false
        }
        
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
            parent.error = error
        }
        
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
            parent.error = error
        }
    }
}

#Preview {
    let sampleContent = MediaContent(
        id: 1,
        title: "Sample Film",
        description: "A sample film description",
        posterURL: "https://example.com/poster.jpg",
        trailerURL: "https://example.com/trailer.mp4",
        contentURL: "https://example.com/content.mp4",
        type: "FILM",
        runtime: 120,
        genre: "Action",
        ageRating: "PG-13"
    )
    ContentDetailView(content: sampleContent, favoritesManager: FavoritesManager.shared)
} 