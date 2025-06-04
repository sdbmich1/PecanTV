import XCTest
@testable import PecanTV

class TestHelpers {
    static func createMockVideo() -> Video {
        return Video(
            id: "test-video-1",
            title: "Test Video",
            description: "Test Description",
            thumbnailURL: URL(string: "https://example.com/thumbnail.jpg")!,
            videoURL: URL(string: "https://example.com/video.mp4")!,
            duration: 120,
            category: "Test",
            tags: ["test", "mock"],
            createdAt: Date(),
            updatedAt: Date()
        )
    }
    
    static func createMockUser() -> User {
        return User(
            id: "test-user-1",
            email: "test@example.com",
            username: "testuser",
            createdAt: Date(),
            updatedAt: Date()
        )
    }
    
    static func createMockPlaylist() -> Playlist {
        return Playlist(
            id: "test-playlist-1",
            title: "Test Playlist",
            description: "Test Playlist Description",
            videos: [createMockVideo()],
            createdAt: Date(),
            updatedAt: Date()
        )
    }
}

// MARK: - XCTestCase Extensions
extension XCTestCase {
    func waitForElement(_ element: XCUIElement, timeout: TimeInterval = 5) {
        let exists = element.waitForExistence(timeout: timeout)
        XCTAssertTrue(exists, "Element should exist")
    }
    
    func waitForElementToDisappear(_ element: XCUIElement, timeout: TimeInterval = 5) {
        let exists = element.waitForExistence(timeout: timeout)
        XCTAssertFalse(exists, "Element should not exist")
    }
} 