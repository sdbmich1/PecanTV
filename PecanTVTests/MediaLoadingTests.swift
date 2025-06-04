import XCTest
@testable import PecanTV

class MediaLoadingTests: XCTestCase {
    let mediaHelper = MediaTestHelper.shared
    
    func testLogoLoading() async throws {
        let expectation = XCTestExpectation(description: "Logo should load successfully")
        
        do {
            let success = try await mediaHelper.verifyMediaLoading(url: mediaHelper.testLogoURL)
            XCTAssertTrue(success, "Logo should load successfully")
            expectation.fulfill()
        } catch {
            XCTFail("Logo loading failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    func testPosterLoading() async throws {
        let expectation = XCTestExpectation(description: "Posters should load successfully")
        
        do {
            for posterURL in mediaHelper.testPosterURLs {
                let success = try await mediaHelper.verifyMediaLoading(url: posterURL)
                XCTAssertTrue(success, "Poster should load successfully")
            }
            expectation.fulfill()
        } catch {
            XCTFail("Poster loading failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    func testContentWithMedia() async throws {
        let content = mediaHelper.createTestContent()
        
        // Test poster loading
        let posterExpectation = XCTestExpectation(description: "Content poster should load")
        do {
            let success = try await mediaHelper.verifyMediaLoading(url: content.posterURL)
            XCTAssertTrue(success, "Content poster should load successfully")
            posterExpectation.fulfill()
        } catch {
            XCTFail("Content poster loading failed with error: \(error)")
        }
        
        // Test backdrop loading
        let backdropExpectation = XCTestExpectation(description: "Content backdrop should load")
        do {
            let success = try await mediaHelper.verifyMediaLoading(url: content.backdropURL)
            XCTAssertTrue(success, "Content backdrop should load successfully")
            backdropExpectation.fulfill()
        } catch {
            XCTFail("Content backdrop loading failed with error: \(error)")
        }
        
        await fulfillment(of: [posterExpectation, backdropExpectation], timeout: 10.0)
    }
} 