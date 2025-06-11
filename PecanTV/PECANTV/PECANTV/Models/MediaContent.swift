import Foundation

enum MediaType: String, Codable {
    case film = "FILM"
    case series = "SERIES"
}

enum Genre: String, CaseIterable, Codable {
    case action = "Action"
    case adventure = "Adventure"
    case biography = "Biography"
    case comedy = "Comedy"
    case crime = "Crime"
    case documentary = "Documentary"
    case drama = "Drama"
    case family = "Family"
    case fantasy = "Fantasy"
    case horror = "Horror"
    case martialArts = "Martial Arts"
    case mystery = "Mystery"
    case noir = "Noir"
    case romance = "Romance"
    case sciFi = "Sci-Fi"
    case sports = "Sports"
    case thriller = "Thriller"
    case western = "Western"
    
    var displayName: String {
        switch self {
        case .sciFi:
            return "Sci-Fi"
        case .martialArts:
            return "Martial Arts"
        default:
            return rawValue
        }
    }
}

struct MediaContent: Identifiable, Hashable {
    let id: Int
    let title: String
    let posterURL: String
    let trailerURL: String
    let contentURL: String
    let description: String
    let type: String
    let runtime: Int
    let genre: String
    let ageRating: String
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: MediaContent, rhs: MediaContent) -> Bool {
        lhs.id == rhs.id
    }
    
    var mediaType: MediaType {
        return MediaType(rawValue: type) ?? .film
    }
    
    var genreEnum: Genre {
        return Genre(rawValue: genre) ?? .drama
    }
} 