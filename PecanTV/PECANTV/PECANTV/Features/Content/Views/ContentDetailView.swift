import SwiftUI
import AVKit

struct ContentDetailView: View {
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    @State private var showTrailer = false
    @State private var showContent = false
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Back button
                Button(action: { dismiss() }) {
                    HStack {
                        Image(systemName: "chevron.left")
                        Text("PecanTV")
                    }
                    .foregroundColor(.primary)
                }
                .padding(.horizontal)
                
                // Poster and Info
                VStack(alignment: .leading, spacing: 16) {
                    AsyncImage(url: URL(string: content.posterURL)) { phase in
                        switch phase {
                        case .empty:
                            Rectangle()
                                .fill(Color.gray.opacity(0.2))
                                .aspectRatio(2/3, contentMode: .fit)
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                        case .failure:
                            Rectangle()
                                .fill(Color.gray.opacity(0.2))
                                .aspectRatio(2/3, contentMode: .fit)
                        @unknown default:
                            EmptyView()
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .cornerRadius(12)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text(content.title)
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.primary)
                        
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
                        .foregroundColor(.secondary)
                        
                        Text(content.description)
                            .font(.body)
                            .foregroundColor(.primary)
                            .padding(.top, 8)
                    }
                    .padding(.horizontal)
                }
                
                // Action Buttons
                VStack(spacing: 12) {
                    Button(action: { showTrailer = true }) {
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
                    
                    Button(action: { showContent = true }) {
                        HStack {
                            Image(systemName: "play.fill")
                            Text("Watch Film")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                }
                .padding(.horizontal)
            }
            .padding(.vertical)
        }
        .background(Color(.systemBackground))
        .fullScreenCover(isPresented: $showTrailer) {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)
                
                VStack {
                    // Back button
                    HStack {
                        Button(action: { showTrailer = false }) {
                            HStack {
                                Image(systemName: "chevron.left")
                                Text("Back")
                            }
                            .foregroundColor(.white)
                            .padding()
                        }
                        Spacer()
                    }
                    
                    if let trailerURL = URL(string: content.trailerURL) {
                        VideoPlayer(player: AVPlayer(url: trailerURL))
                            .edgesIgnoringSafeArea(.all)
                    }
                }
            }
        }
        .fullScreenCover(isPresented: $showContent) {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)
                
                VStack {
                    // Back button
                    HStack {
                        Button(action: { showContent = false }) {
                            HStack {
                                Image(systemName: "chevron.left")
                                Text("Back")
                            }
                            .foregroundColor(.white)
                            .padding()
                        }
                        Spacer()
                    }
                    
                    if let contentURL = URL(string: content.contentURL) {
                        VideoPlayer(player: AVPlayer(url: contentURL))
                            .edgesIgnoringSafeArea(.all)
                    }
                }
            }
        }
    }
}

#Preview {
    ContentDetailView(content: MediaContent(
        id: 1,
        title: "Sample Film",
        posterURL: "https://example.com/poster.jpg",
        trailerURL: "https://example.com/trailer.mp4",
        contentURL: "https://example.com/film.mp4",
        description: "A sample film description",
        type: "FILM",
        runtime: 120,
        genre: "Action",
        ageRating: "PG-13"
    ))
} 