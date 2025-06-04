import Foundation
import SwiftUI

class DemoHomeViewModel: ObservableObject {
    @Published var trendingContent: [Content] = [
        Content(
            id: "1",
            title: "Carnival of Souls",
            type: .movie,
            description: "A classic horror film.",
            releaseDate: Date(),
            duration: 78,
            genres: ["Horror"],
            rating: 7.2,
            posterURL: URL(string: "https://dl.dropboxusercontent.com/scl/fi/7pn74cc7fon4vekofonvp/carnival_of_souls-092024.png?rlkey=1t4ngppw306jgma0g0b8ez1iy&dl=0")!,
            backdropURL: URL(string: "https://dl.dropboxusercontent.com/scl/fi/7pn74cc7fon4vekofonvp/carnival_of_souls-092024.png?rlkey=1t4ngppw306jgma0g0b8ez1iy&dl=0")!,
            videoURL: URL(string: "https://example.com/video1.mp4")!,
            trailerURL: URL(string: "https://example.com/trailer1.mp4"),
            cast: [],
            director: "Herk Harvey",
            seasons: nil
        ),
        Content(
            id: "2",
            title: "Charade",
            type: .movie,
            description: "A romantic comedy mystery.",
            releaseDate: Date(),
            duration: 113,
            genres: ["Comedy", "Mystery"],
            rating: 8.0,
            posterURL: URL(string: "https://dl.dropboxusercontent.com/scl/fi/qt9kiyvj9zs2xfl9k0746/Charade-092124.png?rlkey=9ri4kk17l1i0ydkss558vknp7&dl=0")!,
            backdropURL: URL(string: "https://dl.dropboxusercontent.com/scl/fi/qt9kiyvj9zs2xfl9k0746/Charade-092124.png?rlkey=9ri4kk17l1i0ydkss558vknp7&dl=0")!,
            videoURL: URL(string: "https://example.com/video2.mp4")!,
            trailerURL: URL(string: "https://example.com/trailer2.mp4"),
            cast: [],
            director: "Stanley Donen",
            seasons: nil
        ),
        Content(
            id: "3",
            title: "Christy Love",
            type: .movie,
            description: "Detective drama.",
            releaseDate: Date(),
            duration: 90,
            genres: ["Drama"],
            rating: 6.5,
            posterURL: URL(string: "https://dl.dropboxusercontent.com/scl/fi/q2asw4xxor4ugqhsxli87/ChristyLove-082424-1.png?rlkey=xrvqzee99q3ny3qz52cy8guqe&dl=0")!,
            backdropURL: URL(string: "https://dl.dropboxusercontent.com/scl/fi/q2asw4xxor4ugqhsxli87/ChristyLove-082424-1.png?rlkey=xrvqzee99q3ny3qz52cy8guqe&dl=0")!,
            videoURL: URL(string: "https://example.com/video3.mp4")!,
            trailerURL: URL(string: "https://example.com/trailer3.mp4"),
            cast: [],
            director: "Unknown",
            seasons: nil
        )
    ]
} 