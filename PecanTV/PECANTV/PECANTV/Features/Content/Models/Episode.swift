import Foundation

struct Episode: Identifiable, Codable {
    let id: Int
    let uuid: String
    let title: String
    let description: String
    let seasonNumber: Int
    let episodeNumber: Int
    let runtime: Int
    let contentURL: String
    let posterURL: String
    let airDate: String?
    let seriesId: Int
    let contentUUID: String
    let createdAt: String
    let updatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case uuid
        case title
        case description
        case seasonNumber = "seasonNumber"
        case episodeNumber = "episodeNumber"
        case runtime
        case contentURL = "contentURL"
        case posterURL = "posterURL"
        case airDate = "airDate"
        case seriesId = "seriesId"
        case contentUUID = "contentUuid"
        case createdAt = "createdAt"
        case updatedAt = "updatedAt"
    }
    
    // Computed property for episode display title
    var displayTitle: String {
        return "S\(seasonNumber)E\(episodeNumber): \(title)"
    }
    
    // Computed property for episode number display
    var episodeNumberDisplay: String {
        return "S\(seasonNumber)E\(episodeNumber)"
    }
} 