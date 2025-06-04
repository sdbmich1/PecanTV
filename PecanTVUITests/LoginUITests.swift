import XCTest

class LoginUITests: XCTestCase {
    func testLoginFlow() {
        let app = XCUIApplication()
        app.launch()
        let emailField = app.textFields["Email"]
        let passwordField = app.secureTextFields["Password"]
        let loginButton = app.buttons["Login"]

        emailField.tap()
        emailField.typeText("testuser@example.com")
        passwordField.tap()
        passwordField.typeText("password123")
        loginButton.tap()

        // Assert that the main app view appears
        XCTAssert(app.staticTexts["Logged in!"].exists)
    }
} 