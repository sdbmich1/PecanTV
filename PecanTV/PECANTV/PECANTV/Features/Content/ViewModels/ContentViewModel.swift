import Foundation
import Combine

// API Response structure to match the database schema
struct APIContent: Codable {
    let id: Int
    let title: String
    let poster_url: String
    let trailer_url: String
    let content_url: String
    let description: String?
    let type: String
    let runtime: Int
    let genre_id: Int?
    let rating_id: Int?
    let release_date: String?
    let created_at: String
    let updated_at: String
    let genres: [APIGenre]?  // Multiple genres
    let genre: APIGenre?     // Keep for backward compatibility
    let rating: APIRating?
}

struct APIGenre: Codable {
    let id: Int
    let name: String
    let description: String?
    let created_at: String
    let updated_at: String
}

struct APIRating: Codable {
    let id: Int
    let code: String
    let description: String?
    let min_age: Int?
    let created_at: String
    let updated_at: String
}

// Wrapper struct for JSON decoding
struct ContentResponse: Codable {
    let contents: [MediaContent]
}

class ContentViewModel: ObservableObject {
    @Published var films: [MediaContent] = []
    @Published var tvSeries: [MediaContent] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        loadContent()
    }
    
    func loadContent() {
        isLoading = true
        error = nil
        
        guard let url = URL(string: "http://localhost:8000/content") else {
            self.error = NSError(domain: "Invalid URL", code: -1, userInfo: nil)
            self.isLoading = false
            return
        }
        
        URLSession.shared.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [APIContent].self, decoder: JSONDecoder())
            .map { apiContents in
                apiContents.map { apiContent in
                    // Convert API content to MediaContent
                    let genreNames = apiContent.genres?.map { self.convertGenreToTitleCase($0.name) } ?? []
                    let genreString: String
                    if genreNames.isEmpty {
                        if let genreName = apiContent.genre?.name {
                            genreString = self.convertGenreToTitleCase(genreName)
                        } else {
                            genreString = "Unknown"
                        }
                    } else {
                        genreString = genreNames.joined(separator: ", ")
                    }
                    
                    return MediaContent(
                        id: apiContent.id,
                        title: apiContent.title,
                        description: apiContent.description ?? "",
                        posterURL: apiContent.poster_url,
                        trailerURL: apiContent.trailer_url,
                        contentURL: apiContent.content_url,
                        type: apiContent.type,
                        runtime: apiContent.runtime,
                        genre: genreString,
                        ageRating: apiContent.rating?.code ?? "NR"
                    )
                }
            }
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    self.isLoading = false
                    if case .failure(let error) = completion {
                        self.error = error
                    }
                },
                receiveValue: { contents in
                    self.films = contents.filter { $0.type == "FILM" }
                    self.tvSeries = contents.filter { $0.type == "SERIES" }
                }
            )
            .store(in: &cancellables)
    }
    
    // Helper function to convert genre names from all caps to title case
    private func convertGenreToTitleCase(_ genre: String) -> String {
        // Handle special cases mapping database names to display names
        let specialCases = [
            "SCI-FI": "Science Fiction",
            "SCIENCE FICTION": "Science Fiction",
            "KUNG-FU": "Martial Arts",
            "KUNGFU": "Martial Arts",
            "MARTIAL ARTS": "Martial Arts"
        ]
        
        if let specialCase = specialCases[genre.uppercased()] {
            return specialCase
        }
        
        // Convert to title case for regular genres
        return genre.lowercased().capitalized
    }
    
    func getContentsByGenre(_ genre: String) -> [MediaContent] {
        return films.filter { $0.genre.contains(genre) }
    }
} 