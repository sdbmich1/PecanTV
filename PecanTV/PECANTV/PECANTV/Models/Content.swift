import Foundation

struct Content: Identifiable, Codable {
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
    let seriesName: String?
    let seriesPosterURL: String?
    let seasonNumber: Int?
    let episodeNumber: Int?
    let episodeTitle: String?
    let episodeRuntime: Int?
} 