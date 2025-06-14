import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @State private var selectedTab = 0
    @State private var searchText = ""
    @State private var selectedGenre = "All Genres"
    @State private var showGenrePicker = false
    @State private var selectedContent: MediaContent?
    @State private var showTrailer = false
    @State private var showDetail = false
    
    let genres = ["All Genres", "Action", "Adventure", "Biography", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "Horror", "Martial Arts", "Mystery", "Noir", "Romance", "Sci-Fi", "Sports", "Thriller", "Western", "War"]
    
    // Sample content data
    let content: [MediaContent] = [
        MediaContent(
            id: 1,
            title: "Get Christie Love",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/GetChristieLove-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/GetChristieLove_Trailer-final-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/GetChristieLove.mp4",
            description: "A groundbreaking police drama following the adventures of Christie Love, an undercover detective.",
            type: "TV Series",
            runtime: 60,
            genre: "Crime",
            ageRating: "TV-PG"
        ),
        MediaContent(
            id: 2,
            title: "Black Brigade",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/Black-Brigade-Feature-Img.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/BlackBrigade_Trailer_35sFinal.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/BlackBrigade.mp4",
            description: "A war film about a group of African American soldiers during World War II.",
            type: "Film",
            runtime: 98,
            genre: "War",
            ageRating: "PG"
        ),
        MediaContent(
            id: 3,
            title: "The Learning Tree",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/The-Learning-Tree-Feature-Img.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/TheLearningTree_Trailer_35sFinal.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/TheLearningTree.mp4",
            description: "A coming-of-age story set in 1920s Kansas, following the life of a young African American boy.",
            type: "Film",
            runtime: 107,
            genre: "Drama",
            ageRating: "PG"
        ),
        MediaContent(
            id: 4,
            title: "Sounder",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/Sounder-Feature-Img.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/Sounder_Trailer_35sFinal.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/Sounder.mp4",
            description: "A family drama set in the Depression-era South, following a family's struggle to survive.",
            type: "Film",
            runtime: 105,
            genre: "Drama",
            ageRating: "G"
        ),
        MediaContent(
            id: 5,
            title: "The Autobiography of Miss Jane Pittman",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/JanePittman-Feature-Img.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/JanePittman_Trailer_35sFinal.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/JanePittman.mp4",
            description: "A powerful drama following the life of a woman who lived from slavery through the Civil Rights Movement.",
            type: "TV Series",
            runtime: 110,
            genre: "Drama",
            ageRating: "TV-PG"
        ),
        MediaContent(
            id: 6,
            title: "Roots",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/Roots-Feature-Img.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/Roots_Trailer_35sFinal.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/Roots.mp4",
            description: "A landmark miniseries tracing the history of an African American family from slavery to freedom.",
            type: "TV Series",
            runtime: 90,
            genre: "Drama",
            ageRating: "TV-14"
        ),
        MediaContent(
            id: 7,
            title: "The Color Purple",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/ColorPurple-Feature-Img.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/ColorPurple_Trailer_35sFinal.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/ColorPurple.mp4",
            description: "A powerful drama about the life of a young African American woman in the early 1900s.",
            type: "Film",
            runtime: 154,
            genre: "Drama",
            ageRating: "PG-13"
        ),
        MediaContent(
            id: 8,
            title: "Do the Right Thing",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/DoTheRightThing-Feature-Img.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/DoTheRightThing_Trailer_35sFinal.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/DoTheRightThing.mp4",
            description: "A powerful drama about racial tensions in a Brooklyn neighborhood on the hottest day of the year.",
            type: "Film",
            runtime: 120,
            genre: "Drama",
            ageRating: "R"
        )
    ]
    
    var filteredContent: [MediaContent] {
        content.filter { content in
            let matchesTab = selectedTab == 0 ? content.type == "Film" : content.type == "TV Series"
            let matchesGenre = selectedGenre == "All Genres" || content.genre == selectedGenre
            let matchesSearch = searchText.isEmpty || content.title.localizedCaseInsensitiveContains(searchText)
            return matchesTab && matchesGenre && matchesSearch
        }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Search and Genre Bar
                    HStack {
                        TextField("Search", text: $searchText)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .frame(maxWidth: .infinity)
                        
                        Button(action: { showGenrePicker = true }) {
                            HStack {
                                Text(selectedGenre)
                                    .foregroundColor(.white)
                                Image(systemName: "chevron.down")
                                    .foregroundColor(.white)
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(Color.blue)
                            .cornerRadius(8)
                        }
                        .buttonStyle(PlainButtonStyle())
                    }
                    .padding(.horizontal)
                    
                    // Content Type Tabs
                    HStack(spacing: 20) {
                        TabButton(title: "Films", isSelected: selectedTab == 0) {
                            selectedTab = 0
                        }
                        TabButton(title: "TV Series", isSelected: selectedTab == 1) {
                            selectedTab = 1
                        }
                    }
                    .padding(.horizontal)
                    
                    // Trending Now Section
                    LandscapeCarouselView(title: "Trending Now", content: filteredContent)
                        .frame(height: 250)
                }
            }
            .sheet(isPresented: $showGenrePicker) {
                NavigationView {
                    GenrePickerView(selectedGenre: $selectedGenre, genres: genres)
                }
                .presentationDetents([.medium])
            }
        }
        .sheet(isPresented: $showDetail) {
            if let content = selectedContent {
                ContentDetailView(content: content)
            }
        }
    }
}

struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .fontWeight(isSelected ? .bold : .regular)
                .foregroundColor(isSelected ? .white : .gray)
                .padding(.vertical, 8)
                .padding(.horizontal, 16)
                .background(isSelected ? Color.red : Color.clear)
                .cornerRadius(8)
        }
    }
}

struct GenrePickerView: View {
    @Binding var selectedGenre: String
    let genres: [String]
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        List(genres, id: \.self) { genre in
            Button(action: {
                selectedGenre = genre
                dismiss()
            }) {
                HStack {
                    Text(genre)
                    Spacer()
                    if genre == selectedGenre {
                        Image(systemName: "checkmark")
                            .foregroundColor(.blue)
                    }
                }
            }
        }
        .navigationTitle("Select Genre")
        .navigationBarItems(trailing: Button("Done") {
            dismiss()
        })
    }
}

#Preview {
    HomeView()
        .environmentObject(AuthViewModel())
} 