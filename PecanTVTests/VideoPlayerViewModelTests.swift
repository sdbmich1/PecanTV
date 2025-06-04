import XCTest
@testable import PecanTV

class VideoPlayerViewModelTests: XCTestCase {
    var viewModel: VideoPlayerViewModel!
    var testContent: Content!
    let mediaHelper = MediaTestHelper.shared
    
    override func setUp() {
        super.setUp()
        testContent = mediaHelper.createTestContent()
        viewModel = VideoPlayerViewModel(content: testContent)
    }
    
    override func tearDown() {
        viewModel = nil
        testContent = nil
        super.tearDown()
    }
    
    func testInitialState() {
        XCTAssertEqual(viewModel.content.id, testContent.id)
        XCTAssertEqual(viewModel.content.title, testContent.title)
        XCTAssertFalse(viewModel.isPlaying)
        XCTAssertEqual(viewModel.currentTime, 0)
        XCTAssertEqual(viewModel.duration, testContent.duration)
    }
    
    func testPlayPause() {
        // Test play
        viewModel.play()
        XCTAssertTrue(viewModel.isPlaying)
        
        // Test pause
        viewModel.pause()
        XCTAssertFalse(viewModel.isPlaying)
    }
    
    func testSeek() {
        let seekTime: TimeInterval = 30
        viewModel.seek(to: seekTime)
        XCTAssertEqual(viewModel.currentTime, seekTime)
    }
    
    func testToggleFullscreen() {
        XCTAssertFalse(viewModel.isFullscreen)
        
        viewModel.toggleFullscreen()
        XCTAssertTrue(viewModel.isFullscreen)
        
        viewModel.toggleFullscreen()
        XCTAssertFalse(viewModel.isFullscreen)
    }
    
    func testMediaLoading() async throws {
        let expectation = XCTestExpectation(description: "Media should load successfully")
        
        do {
            let success = try await mediaHelper.verifyMediaLoading(url: testContent.posterURL)
            XCTAssertTrue(success, "Poster should load successfully")
            expectation.fulfill()
        } catch {
            XCTFail("Media loading failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
} 