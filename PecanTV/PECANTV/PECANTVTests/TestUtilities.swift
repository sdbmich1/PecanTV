//
//  TestUtilities.swift
//  PECANTVTests
//
//  Created by Sean Brown on 7/2/25.
//

import XCTest
import SwiftUI
@testable import PECANTV

// MARK: - Mock Data Factory
class MockDataFactory {
    
    static func createMockUser(
        id: String = "1",
        firstName: String = "Test",
        lastName: String = "User",
        email: String = "test@pecantv.com"
    ) -> User {
        return User(
            id: id,
            firstName: firstName,
            lastName: lastName,
            email: email
        )
    }
    
    static func createMockMediaContent(
        id: Int = 1,
        title: String = "Test Movie",
        type: String = "Movie",
        runtime: Int = 120
    ) -> MediaContent {
        return MediaContent(
            id: id,
            title: title,
            description: "A test movie description",
            posterURL: "https://example.com/poster.jpg",
            trailerURL: "https://example.com/trailer.mp4",
            contentURL: "https://example.com/movie.mp4",
            type: type,
            runtime: runtime,
            genre: "Action",
            ageRating: "PG-13"
        )
    }
    
    static func createMockEpisode(
        id: Int = 1,
        title: String = "Test Episode",
        seasonNumber: Int = 1,
        episodeNumber: Int = 1
    ) -> Episode {
        return Episode(
            id: id,
            uuid: UUID().uuidString,
            title: title,
            description: "A test episode description",
            seasonNumber: seasonNumber,
            episodeNumber: episodeNumber,
            runtime: 45,
            contentURL: "https://example.com/episode.mp4",
            posterURL: "https://example.com/episode-poster.jpg",
            airDate: "2024-01-01",
            seriesId: 1,
            contentUUID: UUID().uuidString,
            createdAt: "2024-01-01T00:00:00Z",
            updatedAt: "2024-01-01T00:00:00Z"
        )
    }
}

// MARK: - Test Helpers
class TestHelpers {
    
    static func waitForElement(_ element: XCUIElement, timeout: TimeInterval = 5.0) -> Bool {
        return element.waitForExistence(timeout: timeout)
    }
    
    static func tapElement(_ element: XCUIElement, timeout: TimeInterval = 5.0) {
        XCTAssertTrue(waitForElement(element, timeout: timeout))
        element.tap()
    }
    
    static func typeText(_ text: String, into element: XCUIElement, timeout: TimeInterval = 5.0) {
        XCTAssertTrue(waitForElement(element, timeout: timeout))
        element.tap()
        element.typeText(text)
    }
    
    static func clearAndTypeText(_ text: String, into element: XCUIElement, timeout: TimeInterval = 5.0) {
        XCTAssertTrue(waitForElement(element, timeout: timeout))
        element.tap()
        element.doubleTap() // Select all text
        element.typeText(text)
    }
}

// MARK: - API Test Helpers
class APITestHelpers {
    
    static let baseURL = "https://pecantv-api-production.up.railway.app"
    
    static func makeRequest(
        endpoint: String,
        method: String = "GET",
        body: [String: Any]? = nil
    ) async throws -> (Data, HTTPURLResponse) {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        
        if let body = body {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        }
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        return (data, httpResponse)
    }
    
    static func parseJSON<T: Codable>(_ data: Data) throws -> T {
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    static func createTestUser() -> [String: Any] {
        return [
            "first_name": "Test",
            "last_name": "User",
            "email": "test\(Int.random(in: 1000...9999))@pecantv.com",
            "password": "testpassword123"
        ]
    }
}

// MARK: - UI Test Helpers
class UITestHelpers {
    
    static func launchApp() -> XCUIApplication {
        let app = XCUIApplication()
        app.launch()
        return app
    }
    
    static func navigateToProfile(_ app: XCUIApplication) {
        let profileTab = app.tabBars.buttons["Profile"]
        if profileTab.exists {
            profileTab.tap()
        }
    }
    
    static func navigateToSettings(_ app: XCUIApplication) {
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            settingsButton.tap()
        }
    }
    
    static func loginUser(_ app: XCUIApplication, email: String, password: String) {
        let emailTextField = app.textFields["Email"]
        let passwordSecureTextField = app.secureTextFields["Password"]
        let loginButton = app.buttons["Sign In"]
        
        if emailTextField.exists && passwordSecureTextField.exists && loginButton.exists {
            TestHelpers.typeText(email, into: emailTextField)
            TestHelpers.typeText(password, into: passwordSecureTextField)
            loginButton.tap()
        }
    }
    
    static func registerUser(_ app: XCUIApplication, firstName: String, lastName: String, email: String, password: String) {
        let signUpButton = app.buttons["Sign Up"]
        if signUpButton.exists {
            signUpButton.tap()
            
            let firstNameTextField = app.textFields["First Name"]
            let lastNameTextField = app.textFields["Last Name"]
            let emailTextField = app.textFields["Email"]
            let passwordSecureTextField = app.secureTextFields["Password"]
            let confirmPasswordSecureTextField = app.secureTextFields["Confirm Password"]
            let createAccountButton = app.buttons["Create Account"]
            
            if firstNameTextField.exists {
                TestHelpers.typeText(firstName, into: firstNameTextField)
                TestHelpers.typeText(lastName, into: lastNameTextField)
                TestHelpers.typeText(email, into: emailTextField)
                TestHelpers.typeText(password, into: passwordSecureTextField)
                TestHelpers.typeText(password, into: confirmPasswordSecureTextField)
                createAccountButton.tap()
            }
        }
    }
}

// MARK: - Test Assertions
extension XCTestCase {
    
    func XCTAssertValidUser(_ user: User, file: StaticString = #file, line: UInt = #line) {
        XCTAssertNotNil(user.id, "User ID should not be nil", file: file, line: line)
        XCTAssertNotNil(user.email, "User email should not be nil", file: file, line: line)
        XCTAssertNotNil(user.firstName, "User first name should not be nil", file: file, line: line)
        XCTAssertNotNil(user.lastName, "User last name should not be nil", file: file, line: line)
        XCTAssertNotNil(user.fullName, "User full name should not be nil", file: file, line: line)
    }
    
    func XCTAssertValidMediaContent(_ content: MediaContent, file: StaticString = #file, line: UInt = #line) {
        XCTAssertNotNil(content.id, "Content ID should not be nil", file: file, line: line)
        XCTAssertNotNil(content.title, "Content title should not be nil", file: file, line: line)
        XCTAssertNotNil(content.description, "Content description should not be nil", file: file, line: line)
        XCTAssertGreaterThan(content.runtime, 0, "Content runtime should be greater than 0", file: file, line: line)
        XCTAssertNotNil(content.genre, "Content genre should not be nil", file: file, line: line)
        XCTAssertNotNil(content.ageRating, "Content age rating should not be nil", file: file, line: line)
    }
    
    func XCTAssertValidEpisode(_ episode: Episode, file: StaticString = #file, line: UInt = #line) {
        XCTAssertNotNil(episode.id, "Episode ID should not be nil", file: file, line: line)
        XCTAssertNotNil(episode.title, "Episode title should not be nil", file: file, line: line)
        XCTAssertGreaterThan(episode.seasonNumber, 0, "Episode season number should be greater than 0", file: file, line: line)
        XCTAssertGreaterThan(episode.episodeNumber, 0, "Episode episode number should be greater than 0", file: file, line: line)
        XCTAssertGreaterThan(episode.runtime, 0, "Episode runtime should be greater than 0", file: file, line: line)
    }
} 