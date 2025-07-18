import Foundation
import Combine
import UIKit // Added for UIDevice

// API Response structure to match the database schema
struct APIContent: Codable {
    let id: Int
    let title: String
    let posterURL: String
    let trailerURL: String
    let contentURL: String
    let description: String?
    let type: String
    let runtime: Int
    let genreId: Int?
    let ratingId: Int?
    let releaseDate: String?
    let createdAt: String
    let updatedAt: String
    let genres: [APIGenre]?  // Multiple genres
    let genre: APIGenre?     // Keep for backward compatibility
    let rating: APIRating?
    
    func toMediaContent() -> MediaContent {
        let genreNames = genres?.map { convertGenreToTitleCase($0.name) } ?? []
        let genreName = genre?.name ?? ""
        let ageRating = rating?.code ?? "NR"
        
        return MediaContent(
            id: id,
            title: title,
            description: description ?? "",
            posterURL: posterURL,
            trailerURL: trailerURL,
            contentURL: contentURL,
            type: type,
            runtime: runtime,
            genre: genreName,
            ageRating: ageRating
        )
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
}

struct APIGenre: Codable {
    let id: Int
    let name: String
    let description: String?
    let createdAt: String
    let updatedAt: String
}

struct APIRating: Codable {
    let id: Int
    let code: String
    let description: String?
    let minAge: Int?
    let createdAt: String
    let updatedAt: String
}

// Wrapper struct for JSON decoding
struct ContentResponse: Codable {
    let contents: [MediaContent]
}

class ContentViewModel: ObservableObject {
    @Published var films: [MediaContent] = []
    @Published var tvSeries: [MediaContent] = []
    @Published var allContent: [MediaContent] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        // Don't automatically load content - let the app decide when to load
        print("📱 ContentViewModel initialized")
    }
    
    func loadContent() {
        print("🔄 ContentViewModel: Starting content load...")
        isLoading = true
        error = nil
        
        guard let url = APIConfig.url(for: APIConfig.Endpoints.content) else {
            print("❌ ContentViewModel: Invalid URL for content endpoint")
            self.error = NSError(domain: "Invalid URL", code: -1, userInfo: nil)
            self.isLoading = false
            return
        }
        
        print("🔍 ContentViewModel: Loading content from: \(url)")
        
        URLSession.shared.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [APIContent].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    self.isLoading = false
                    switch completion {
                    case .finished:
                        print("✅ ContentViewModel: Content loaded successfully")
                    case .failure(let error):
                        print("❌ ContentViewModel: Failed to load content: \(error.localizedDescription)")
                        self.error = error
                    }
                },
                receiveValue: { apiContent in
                    print("📊 ContentViewModel: Received \(apiContent.count) content items")
                    self.films = apiContent.filter { $0.type.uppercased() == "FILM" }.map { $0.toMediaContent() }
                    self.tvSeries = apiContent.filter { $0.type.uppercased() == "SERIES" }.map { $0.toMediaContent() }
                    self.allContent = self.films + self.tvSeries
                    print("📊 ContentViewModel: Processed \(self.films.count) films and \(self.tvSeries.count) TV series")
                    
                    // Notify FavoritesManager to update favorite content
                    DispatchQueue.main.async {
                        FavoritesManager.shared.updateFavoriteContentFromAvailableContent(self.allContent)
                        
                        // Post notification that content has been loaded
                        NotificationCenter.default.post(name: .contentLoaded, object: nil)
                        print("📢 Content loaded notification posted")
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    func getContentsByGenre(_ genre: String) -> [MediaContent] {
        return films.filter { $0.genre.contains(genre) }
    }
} 