import XCTest

class VideoPlayerViewUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testVideoPlayerControls() {
        // Navigate to video player (assuming there's a way to get there)
        // This will need to be adjusted based on your app's navigation structure
        
        // Test play button
        let playButton = app.buttons["playButton"]
        waitForElement(playButton)
        playButton.tap()
        
        // Test pause button
        let pauseButton = app.buttons["pauseButton"]
        waitForElement(pauseButton)
        pauseButton.tap()
        
        // Test fullscreen button
        let fullscreenButton = app.buttons["fullscreenButton"]
        waitForElement(fullscreenButton)
        fullscreenButton.tap()
        
        // Test seeking
        let seekBar = app.sliders["seekBar"]
        waitForElement(seekBar)
        seekBar.adjust(toNormalizedSliderPosition: 0.5)
    }
    
    func testVideoPlayerOrientation() {
        // Test rotation
        XCUIDevice.shared.orientation = .landscapeLeft
        // Add assertions for landscape layout
        
        XCUIDevice.shared.orientation = .portrait
        // Add assertions for portrait layout
    }
    
    func testVideoPlayerGestures() {
        // Test double tap to seek
        let videoView = app.otherElements["videoView"]
        waitForElement(videoView)
        videoView.doubleTap()
        
        // Test swipe to seek
        videoView.swipeLeft()
        videoView.swipeRight()
    }
} 