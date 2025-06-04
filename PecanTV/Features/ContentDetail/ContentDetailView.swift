import SwiftUI
import AVKit

struct ContentDetailView: View {
    let content: Content
    @State private var isPlaying = false
    @State private var isInWatchlist = false
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Hero Image
                AsyncImage(url: content.backdropURL) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                }
                .frame(height: 250)
                .clipped()
                
                VStack(alignment: .leading, spacing: 15) {
                    // Title and Rating
                    HStack {
                        Text(content.title)
                            .font(.title)
                            .fontWeight(.bold)
                        
                        Spacer()
                        
                        HStack {
                            Image(systemName: "star.fill")
                                .foregroundColor(.yellow)
                            Text(String(format: "%.1f", content.rating))
                        }
                    }
                    
                    // Metadata
                    HStack {
                        Text(content.type.rawValue.capitalized)
                        Text("•")
                        Text(content.releaseDate, style: .date)
                        Text("•")
                        Text("\(content.duration) min")
                    }
                    .foregroundColor(.gray)
                    
                    // Genres
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack {
                            ForEach(content.genres, id: \.self) { genre in
                                Text(genre)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.gray.opacity(0.2))
                                    .cornerRadius(15)
                            }
                        }
                    }
                    
                    // Description
                    Text(content.description)
                        .lineSpacing(4)
                    
                    // Cast
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Cast")
                            .font(.headline)
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 15) {
                                ForEach(content.cast) { member in
                                    VStack {
                                        if let imageURL = member.profileImageURL {
                                            AsyncImage(url: imageURL) { image in
                                                image
                                                    .resizable()
                                                    .aspectRatio(contentMode: .fill)
                                            } placeholder: {
                                                Circle()
                                                    .fill(Color.gray.opacity(0.3))
                                            }
                                            .frame(width: 60, height: 60)
                                            .clipShape(Circle())
                                        } else {
                                            Circle()
                                                .fill(Color.gray.opacity(0.3))
                                                .frame(width: 60, height: 60)
                                        }
                                        
                                        Text(member.name)
                                            .font(.caption)
                                            .lineLimit(1)
                                        
                                        Text(member.character)
                                            .font(.caption2)
                                            .foregroundColor(.gray)
                                            .lineLimit(1)
                                    }
                                    .frame(width: 80)
                                }
                            }
                        }
                    }
                    
                    // Action Buttons
                    HStack(spacing: 20) {
                        Button(action: {
                            isPlaying = true
                        }) {
                            HStack {
                                Image(systemName: "play.fill")
                                Text("Play")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }
                        
                        Button(action: {
                            isInWatchlist.toggle()
                        }) {
                            Image(systemName: isInWatchlist ? "bookmark.fill" : "bookmark")
                                .font(.title2)
                                .foregroundColor(isInWatchlist ? .red : .gray)
                        }
                    }
                    // Watch Trailer Button
                    if let trailerURL = content.trailerURL {
                        Button(action: {
                            isPlaying = true
                        }) {
                            HStack {
                                Image(systemName: "play.rectangle.fill")
                                Text("Watch Trailer")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }
                        .accessibilityIdentifier("Watch Trailer")
                    }
                }
                .padding()
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .fullScreenCover(isPresented: $isPlaying) {
            if let trailerURL = content.trailerURL {
                VideoPlayer(player: AVPlayer(url: trailerURL))
                    .edgesIgnoringSafeArea(.all)
                    .accessibilityIdentifier("VideoPlayer")
            } else {
                VideoPlayerView(content: content)
            }
        }
    }
}

#Preview {
    NavigationView {
        ContentDetailView(content: Content(
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
} 