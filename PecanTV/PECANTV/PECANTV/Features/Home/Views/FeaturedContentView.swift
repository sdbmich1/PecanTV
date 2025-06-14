import SwiftUI

struct FeaturedContentView: View {
    let content: MediaContent
    let onTap: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            AsyncImage(url: URL(string: content.posterURL)) { phase in
                switch phase {
                case .empty:
                    ProgressView()
                        .frame(height: 400)
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(height: 400)
                        .clipped()
                case .failure:
                    Image(systemName: "photo")
                        .font(.system(size: 100))
                        .foregroundColor(.gray)
                        .frame(height: 400)
                @unknown default:
                    EmptyView()
                }
            }
            .cornerRadius(12)
            .onTapGesture(perform: onTap)
            
            VStack(alignment: .leading, spacing: 8) {
                Text(content.title)
                    .font(.title)
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
                    .lineLimit(3)
            }
            .padding(.horizontal)
        }
    }
}

#Preview {
    ZStack {
        Color.black.edgesIgnoringSafeArea(.all)
        
        FeaturedContentView(
            content: MediaContent(
                id: 1,
                title: "Get Christie Love",
                posterURL: "https://storage.googleapis.com/pecantv_title_images/getchristielove-Feature-Img-16x9.png",
                trailerURL: "https://storage.googleapis.com/pecantv_trailers/getchristielove_trailer-60s.mp4",
                contentURL: "https://storage.googleapis.com/pecantv_content/getchristielove.mp4",
                description: "A groundbreaking crime drama series",
                type: "SERIES",
                runtime: 60,
                genre: "Crime",
                ageRating: "TV-14"
            ),
            onTap: {}
        )
    }
} 