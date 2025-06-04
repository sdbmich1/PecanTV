import XCTest
@testable import PecanTV

class MediaTestHelper {
    static let shared = MediaTestHelper()
    
    // Dropbox shared folder URLs
    private let dropboxBaseURL = "https://dl.dropboxusercontent.com/s/"
    private let logoFolderID = "YOUR_LOGO_FOLDER_ID" // Replace with your Dropbox folder ID
    private let posterFolderID = "YOUR_POSTER_FOLDER_ID" // Replace with your Dropbox folder ID
    
    // Test media URLs
    var testLogoURL: URL {
        URL(string: "\(dropboxBaseURL)\(logoFolderID)/pecantv_logo.png")!
    }
    
    var testPosterURLs: [URL] {
        [
            URL(string: "\(dropboxBaseURL)\(posterFolderID)/movie1_poster.jpg")!,
            URL(string: "\(dropboxBaseURL)\(posterFolderID)/movie2_poster.jpg")!,
            URL(string: "\(dropboxBaseURL)\(posterFolderID)/movie3_poster.jpg")!
        ]
    }
    
    // Helper method to create test content with Dropbox media
    func createTestContent() -> Content {
        Content(
            id: "test-1",
            title: "Test Movie",
            type: .movie,
            description: "A test movie description",
            releaseDate: Date(),
            duration: 120,
            genres: ["Action", "Drama"],
            rating: 8.5,
            posterURL: testPosterURLs[0],
            backdropURL: testPosterURLs[1],
            videoURL: URL(string: "https://example.com/test-video.mp4")!,
            trailerURL: URL(string: "https://example.com/test-trailer.mp4"),
            cast: [
                CastMember(id: "1", name: "Test Actor", character: "Lead Role", profileImageURL: nil)
            ],
            director: "Test Director",
            seasons: nil
        )
    }
    
    // Helper method to verify media loading
    func verifyMediaLoading(url: URL) async throws -> Bool {
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NSError(domain: "MediaTestHelper", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])
        }
        return httpResponse.statusCode == 200 && !data.isEmpty
    }
} 