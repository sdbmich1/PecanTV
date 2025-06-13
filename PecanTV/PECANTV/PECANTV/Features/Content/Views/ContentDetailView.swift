import SwiftUI
import AVKit

struct ContentDetailView: View {
    let content: MediaContent
    @Environment(\.dismiss) private var dismiss
    @State private var showTrailer = false
    @State private var showContent = false
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Back button
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
                    .padding(.horizontal)
                    .padding(.top, 8)
                    
                    // Poster and Info
                    VStack(alignment: .leading, spacing: 16) {
                        AsyncImage(url: URL(string: content.posterURL)) { phase in
                            switch phase {
                            case .empty:
                                Rectangle()
                                    .fill(Color.gray.opacity(0.2))
                                    .aspectRatio(2/3, contentMode: .fit)
                                    .frame(maxWidth: 200)
                            case .success(let image):
                                image
                                    .resizable()
                                    .aspectRatio(2/3, contentMode: .fit)
                                    .frame(maxWidth: 200)
                            case .failure:
                                Rectangle()
                                    .fill(Color.gray.opacity(0.2))
                                    .aspectRatio(2/3, contentMode: .fit)
                                    .frame(maxWidth: 200)
                            @unknown default:
                                EmptyView()
                            }
                        }
                        .cornerRadius(12)
                        .shadow(radius: 5)
                        .frame(maxWidth: .infinity)
                        .padding(.horizontal)
                        
                        VStack(alignment: .leading, spacing: 8) {
                            Text(content.title)
                                .font(.title2)
                                .fontWeight(.bold)
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
                            .background(Color.pecanRed)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                    }
                    .padding(.horizontal)
                    .padding(.top, 20)
                    
                    // Bottom spacing for footer
                    Spacer()
                        .frame(height: 60)
                }
                .padding(.vertical)
            }
        }
        .navigationBarHidden(true)
        .fullScreenCover(isPresented: $showTrailer) {
            if let url = URL(string: content.trailerURL) {
                VideoPlayerView(url: url, content: content)
            }
        }
        .fullScreenCover(isPresented: $showContent) {
            if let url = URL(string: content.contentURL) {
                VideoPlayerView(url: url, content: content)
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