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
    
    let genres = ["All Genres", "Action", "Adventure", "Biography", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "Horror", "Martial Arts", "Mystery", "Noir", "Romance", "Sci-Fi", "Sports", "Thriller", "Western"]
    
    let films: [MediaContent] = [
        MediaContent(
            id: 1,
            title: "Get Christie Love",
            posterURL: "https://www.dropbox.com/scl/fi/nxj319g2vpc43eb075vwx/GetChristieLove-Feature-Img-16x9.png?rlkey=nitbvdf33fe5ddkusowmydjjf&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1",
            description: "A groundbreaking crime drama series following the adventures of Christie Love, a stylish and tough undercover police detective.",
            type: "FILM",
            runtime: 60,
            genre: "Crime",
            ageRating: "TV-14"
        ),
        MediaContent(
            id: 2,
            title: "The Jackie Robinson Story",
            posterURL: "https://www.dropbox.com/scl/fi/cpetw71zb146k9av5bhbo/Jesse-Owens-Feature-Img.png?rlkey=rvdr3t4jszbfiwd2xsoz1arxl&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1",
            description: "The inspiring true story of Jackie Robinson, the first African American to play in Major League Baseball.",
            type: "FILM",
            runtime: 76,
            genre: "Biography",
            ageRating: "PG"
        ),
        MediaContent(
            id: 3,
            title: "Enter the Dragon",
            posterURL: "https://www.dropbox.com/scl/fi/25rrubaboabipsj0w2391/Master-of-the-Flying-Guillotine_title-img.png?rlkey=9vhe3jul0s1k2cfn361s25ojo&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/nol6t074fks597ztmmtl0/GetChristieLove_Trailer-final-30s.mp4?rlkey=s9xahbmy27pqu6jsjg1hp5eg8&raw=1",
            description: "A martial artist agrees to spy on a reclusive crime lord using his invitation to a tournament there.",
            type: "FILM",
            runtime: 102,
            genre: "Martial Arts",
            ageRating: "R"
        ),
        MediaContent(
            id: 4,
            title: "Carnival of Souls",
            posterURL: "https://www.dropbox.com/scl/fi/d01kibhq2pznji65jyijz/Carnival-of-souls_Title-Img.png?rlkey=230crqhaslibjvysq5w7oozh6&raw=1",
            trailerURL: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            contentURL: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            description: "A classic horror film about a woman who is haunted by strange visions after a car accident.",
            type: "FILM",
            runtime: 78,
            genre: "Horror",
            ageRating: "PG-13"
        ),
        MediaContent(
            id: 7,
            title: "Joe Bullett",
            posterURL: "https://www.dropbox.com/scl/fi/qucm6dy6l8gey68bz6kbj/Joe-Bullett-Feature-Img.png?rlkey=n34tmw17qomy3yybqctqbv8oo&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/zuek3zqlwzcvd6h9nk3bm/Joe-Bullett_trailer-1min.mp4?rlkey=lk25fddvasdi2hibbircsz5rn&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/zuek3zqlwzcvd6h9nk3bm/Joe-Bullett_trailer-1min.mp4?rlkey=lk25fddvasdi2hibbircsz5rn&raw=1",
            description: "Joe Bullett is called in to stop a gangster from sabotaging a soccer match.",
            type: "FILM",
            runtime: 79,
            genre: "Sports",
            ageRating: "PG"
        ),
        MediaContent(
            id: 8,
            title: "Black Brigade",
            posterURL: "https://www.dropbox.com/scl/fi/cffobst7dla6tw9l0mw9e/Black-Brigade-Feature-Img.png?rlkey=l8f129grte08prkjds8qd60sg&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/0x895ef52x47u2143o01m/BlackBrigade_Trailer_35sFinal.mp4?rlkey=garkzilvdgn2w1l94te7fqe2r&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/0x895ef52x47u2143o01m/BlackBrigade_Trailer_35sFinal.mp4?rlkey=garkzilvdgn2w1l94te7fqe2r&raw=1",
            description: "A racist officer is put in charge of a squad of black troops charged with taking an important bridge from the Germans.",
            type: "FILM",
            runtime: 70,
            genre: "Drama",
            ageRating: "PG-13"
        ),
        MediaContent(
            id: 9,
            title: "Dementia-13",
            posterURL: "https://www.dropbox.com/scl/fi/zko5zgyogcf7aonpm512n/dementia-13_Title-Img.png?rlkey=5qalmbthf77pl50mbdq658n0n&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            description: "A scheming widow hatches a bold plan to acquire her late husband's inheritance, unaware that she is being targeted by an ax murderer who lurks in the family's estate.",
            type: "FILM",
            runtime: 74,
            genre: "Horror",
            ageRating: "R"
        ),
        MediaContent(
            id: 10,
            title: "Little Shop of Horrors",
            posterURL: "https://www.dropbox.com/scl/fi/e9b8q4lm8f3eh6fseozvk/Little-Shop-of-Horrors_Title-Img-colorbk.png?rlkey=xpyd37aj59aat278udpo7lko7&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            description: "A farce about a florist's assistant who cultivates a plant that feeds on human blood.",
            type: "FILM",
            runtime: 60,
            genre: "Comedy",
            ageRating: "PG-13"
        ),
        MediaContent(
            id: 11,
            title: "The Last Time I Saw Paris",
            posterURL: "https://www.dropbox.com/scl/fi/nvu10pyjp82t3sgc6tir6/Last-Time-I-Saw-Paris_Title_Img-1920x1080.jpg?rlkey=xnbmvrsytndslb3pcc1qyb8cz&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            description: "An American journalist returns to Paris - a city that gave him true love and deep grief.",
            type: "FILM",
            runtime: 112,
            genre: "Romance",
            ageRating: "PG-13"
        ),
        MediaContent(
            id: 12,
            title: "Jesse Owens",
            posterURL: "https://www.dropbox.com/scl/fi/cpetw71zb146k9av5bhbo/Jesse-Owens-Feature-Img.png?rlkey=rvdr3t4jszbfiwd2xsoz1arxl&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/b0m6t5l8pmgy40lfr48zw/JesseOwens-Trailer_35sec.mp4?rlkey=oy8n83cs7b8imxoxjbt3sekwb&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/b0m6t5l8pmgy40lfr48zw/JesseOwens-Trailer_35sec.mp4?rlkey=oy8n83cs7b8imxoxjbt3sekwb&raw=1",
            description: "The full story of Jesse Owens, four-time Olympic gold medallist and star of the 1936 Berlin Olympics, as told through the lens of an investigator into Owen's life at the behest of a judicial mandate. Here we see Owens forced to battle overt and covert racism throughout his life and his battling through difficulties.",
            type: "FILM",
            runtime: 174,
            genre: "Sports",
            ageRating: "PG"
        ),
        MediaContent(
            id: 13,
            title: "Love Affair",
            posterURL: "https://www.dropbox.com/scl/fi/nfhq65w4nlswvcm1gpkst/Love-Affair_title-image.png?rlkey=ib9t6cjafnqfa1933u8f0wytx&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            description: "A French playboy and an American former nightclub singer fall in love aboard a ship.",
            type: "FILM",
            runtime: 88,
            genre: "Romance",
            ageRating: "PG"
        ),
        MediaContent(
            id: 14,
            title: "Man with the Golden Arm",
            posterURL: "https://www.dropbox.com/scl/fi/p031opbnsa2e44yoc5nrv/Man-with-the-Golden-Arm-Title-Img.png?rlkey=jfq97q3yge7hsdothrlm1ctgw&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            description: "A junkie must face his true self to kick his drug addiction.",
            type: "FILM",
            runtime: 119,
            genre: "Drama",
            ageRating: "PG"
        ),
        MediaContent(
            id: 15,
            title: "Master of the Flying Guillotine",
            posterURL: "https://www.dropbox.com/scl/fi/25rrubaboabipsj0w2391/Master-of-the-Flying-Guillotine_title-img.png?rlkey=9vhe3jul0s1k2cfn361s25ojo&raw=1",
            trailerURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            contentURL: "https://www.dropbox.com/scl/fi/h8w4ogywwks5het2mhh2w/Night-of-the-Living-Dead_trailer.mp4?rlkey=ow6hjsxggbtkz378ih2cyyo01&raw=1",
            description: "A vengeful and blind Kung Fu expert travels to a village where a martial arts contest is being held and vows to behead every one armed man he comes across.",
            type: "FILM",
            runtime: 93,
            genre: "Action",
            ageRating: "R"
        ),
        MediaContent(
            id: 5,
            title: "The Good, the Bad and the Ugly",
            posterURL: "https://www.dropbox.com/scl/fi/example.png?rlkey=example&raw=1",
            trailerURL: "https://example.com/trailer.mp4",
            contentURL: "https://example.com/film.mp4",
            description: "A classic western film about three gunslingers competing to find a fortune in buried Confederate gold.",
            type: "FILM",
            runtime: 161,
            genre: "Western",
            ageRating: "R"
        )
    ]
    
    var availableGenres: [String] {
        let typeFiltered = selectedTab == 0 ? films.filter { $0.type == "FILM" } : films.filter { $0.type == "SERIES" }
        let genres = Set(typeFiltered.map { $0.genre })
        return ["All Genres"] + Array(genres).sorted()
    }
    
    var filteredContent: [MediaContent] {
        let typeFiltered = selectedTab == 0 ? films.filter { $0.type == "FILM" } : films.filter { $0.type == "SERIES" }
        let genreFiltered = selectedGenre == "All Genres" ? typeFiltered : typeFiltered.filter { $0.genre == selectedGenre }
        if searchText.isEmpty {
            return genreFiltered
        }
        return genreFiltered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // Search and Genre Bar
                    HStack(spacing: 12) {
                        // Search Bar
                        HStack {
                            Image(systemName: "magnifyingglass")
                                .foregroundColor(.gray)
                            TextField("Search", text: $searchText)
                        }
                        .padding(8)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                        
                        // Genre Picker Button
                        Button(action: {
                            showGenrePicker = true
                        }) {
                            HStack {
                                Text(selectedGenre)
                                    .foregroundColor(.primary)
                                Image(systemName: "chevron.down")
                                    .foregroundColor(.gray)
                            }
                            .padding(8)
                            .background(Color(.systemGray6))
                            .cornerRadius(8)
                        }
                    }
                    .padding(.horizontal)
                    
                    // Content Type Tabs
                    HStack(spacing: 0) {
                        TabButton(title: "Films", isSelected: selectedTab == 0) {
                            withAnimation {
                                selectedTab = 0
                                selectedGenre = "All Genres"
                            }
                        }
                        
                        TabButton(title: "TV Series", isSelected: selectedTab == 1) {
                            withAnimation {
                                selectedTab = 1
                                selectedGenre = "All Genres"
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    // Recently Added Section
                    LandscapeCarouselView(
                        title: "Recently Added",
                        content: filteredContent
                    )
                    .padding(.vertical)
                }
                .padding(.bottom, 100) // Add padding for the tab bar
            }
            .navigationTitle("PECAN TV")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showGenrePicker) {
                GenrePickerView(selectedGenre: $selectedGenre, genres: genres)
            }
        }
        .sheet(isPresented: $showDetail) {
            if let content = selectedContent {
                ContentDetailView(content: content)
            }
        }
    }
}

struct GenrePickerView: View {
    @Binding var selectedGenre: String
    let genres: [String]
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVStack(spacing: 0) {
                    ForEach(genres, id: \.self) { genre in
                        Button {
                            selectedGenre = genre
                            dismiss()
                        } label: {
                            HStack {
                                Text(genre)
                                    .foregroundColor(.primary)
                                Spacer()
                                if genre == selectedGenre {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.blue)
                                }
                            }
                            .padding(.horizontal)
                            .padding(.vertical, 12)
                            .contentShape(Rectangle())
                        }
                        .buttonStyle(PlainButtonStyle())
                        
                        if genre != genres.last {
                            Divider()
                                .padding(.leading)
                        }
                    }
                }
            }
            .navigationTitle("Select Genre")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct SearchBar: View {
    @Binding var text: String
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)
            
            TextField("Search", text: $text)
                .foregroundColor(.primary)
            
            if !text.isEmpty {
                Button {
                    text = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(8)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .foregroundColor(isSelected ? .primary : .gray)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(
                    Rectangle()
                        .fill(isSelected ? Color.blue.opacity(0.1) : Color.clear)
                )
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(AuthViewModel())
} 