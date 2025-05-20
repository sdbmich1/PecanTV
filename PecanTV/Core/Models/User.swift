import Foundation

struct User: Codable, Identifiable {
    let id: String
    let email: String
    var displayName: String?
    var profileImageURL: URL?
    var watchHistory: [String] // Array of content IDs
    var watchlist: [String] // Array of content IDs
    
    enum CodingKeys: String, CodingKey {
        case id
        case email
        case displayName = "display_name"
        case profileImageURL = "profile_image_url"
        case watchHistory = "watch_history"
        case watchlist
    }
} 