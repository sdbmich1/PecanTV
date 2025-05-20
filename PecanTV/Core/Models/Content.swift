import Foundation

struct Content: Identifiable, Codable {
    let id: String
    let title: String
    let type: ContentType
    let description: String
    let releaseDate: Date
    let duration: Int // in minutes
    let genres: [String]
    let rating: Double
    let posterURL: URL
    let backdropURL: URL
    let videoURL: URL
    let trailerURL: URL?
    let cast: [CastMember]
    let director: String
    let seasons: [Season]?
    
    enum ContentType: String, Codable {
        case movie
        case tvShow
    }
}

struct CastMember: Codable, Identifiable {
    let id: String
    let name: String
    let character: String
    let profileImageURL: URL?
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case character
        case profileImageURL = "profile_image_url"
    }
}

struct Season: Codable, Identifiable {
    let id: String
    let number: Int
    let episodes: [Episode]
}

struct Episode: Codable, Identifiable {
    let id: String
    let title: String
    let number: Int
    let description: String
    let duration: Int
    let videoURL: URL
    let thumbnailURL: URL
    
    enum CodingKeys: String, CodingKey {
        case id
        case title
        case number
        case description
        case duration
        case videoURL = "video_url"
        case thumbnailURL = "thumbnail_url"
    }
} 