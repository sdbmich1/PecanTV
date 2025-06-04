import XCTest
@testable import PecanTV

class AuthenticationServiceTests: XCTestCase {
    var authService: AuthenticationService!
    
    override func setUp() {
        super.setUp()
        authService = AuthenticationService()
    }
    
    override func tearDown() {
        authService = nil
        super.tearDown()
    }
    
    func testSignIn() async throws {
        // Test successful sign in
        let expectation = XCTestExpectation(description: "Sign in successful")
        
        do {
            let user = try await authService.signIn(email: "test@example.com", password: "password123")
            XCTAssertNotNil(user)
            XCTAssertEqual(user.email, "test@example.com")
            expectation.fulfill()
        } catch {
            XCTFail("Sign in failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
    }
    
    func testSignUp() async throws {
        // Test successful sign up
        let expectation = XCTestExpectation(description: "Sign up successful")
        
        do {
            let user = try await authService.signUp(email: "newuser@example.com", password: "password123", username: "newuser")
            XCTAssertNotNil(user)
            XCTAssertEqual(user.email, "newuser@example.com")
            XCTAssertEqual(user.username, "newuser")
            expectation.fulfill()
        } catch {
            XCTFail("Sign up failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
    }
    
    func testSignOut() async throws {
        // Test successful sign out
        let expectation = XCTestExpectation(description: "Sign out successful")
        
        do {
            try await authService.signOut()
            expectation.fulfill()
        } catch {
            XCTFail("Sign out failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
    }
    
    func testInvalidCredentials() async {
        // Test sign in with invalid credentials
        let expectation = XCTestExpectation(description: "Sign in should fail with invalid credentials")
        
        do {
            _ = try await authService.signIn(email: "invalid@example.com", password: "wrongpassword")
            XCTFail("Sign in should have failed with invalid credentials")
        } catch {
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 5.0)
    }
} 