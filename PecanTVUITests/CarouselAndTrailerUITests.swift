import XCTest

class CarouselAndTrailerUITests: XCTestCase {
    func testCarouselAndTrailerFlow() {
        let app = XCUIApplication()
        app.launch()

        // Wait for splash to disappear
        sleep(3)

        // Find the first poster and tap it
        let firstPoster = app.images.element(boundBy: 0)
        XCTAssertTrue(firstPoster.exists)
        firstPoster.tap()

        // Tap the "Watch Trailer" button
        let trailerButton = app.buttons["Watch Trailer"]
        XCTAssertTrue(trailerButton.exists)
        trailerButton.tap()

        // Assert that the video player appears
        XCTAssert(app.otherElements["VideoPlayer"].exists)
    }
} 