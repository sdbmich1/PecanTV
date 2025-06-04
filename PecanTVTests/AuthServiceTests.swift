import XCTest
@testable import PecanTV

class AuthServiceTests: XCTestCase {
    func testRegisterAndLogin() {
        let expectation = self.expectation(description: "Register and login")
        let email = "testuser@example.com"
        let username = "testuser"
        let password = "password123"

        register(email: email, username: username, password: password) { success in
            XCTAssertTrue(success, "Registration should succeed")
            login(email: email, password: password) { token in
                XCTAssertNotNil(token, "Login should return a token")
                expectation.fulfill()
            }
        }
        waitForExpectations(timeout: 10)
    }
} 