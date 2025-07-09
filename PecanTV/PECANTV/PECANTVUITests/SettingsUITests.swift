//
//  SettingsUITests.swift
//  PECANTVUITests
//
//  Created by Sean Brown on 7/2/25.
//

import XCTest

final class SettingsUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
    }
    
    func testSettingsNavigation() throws {
        // Navigate to settings if possible
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Verify settings view is displayed
            XCTAssertTrue(app.navigationBars["Settings"].exists)
        }
    }
    
    func testAccountSection() throws {
        // Navigate to settings if possible
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Test account section elements
            XCTAssertTrue(app.staticTexts["Account"].exists)
            XCTAssertTrue(app.buttons["Edit Profile"].exists)
            XCTAssertTrue(app.buttons["Change Password"].exists)
            XCTAssertTrue(app.buttons["Billing Information"].exists)
        }
    }
    
    func testPreferencesSection() throws {
        // Navigate to settings if possible
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Test preferences section elements
            XCTAssertTrue(app.staticTexts["Preferences"].exists)
            XCTAssertTrue(app.buttons["Video Quality"].exists)
            XCTAssertTrue(app.buttons["Audio Language"].exists)
            XCTAssertTrue(app.buttons["Subtitles"].exists)
            XCTAssertTrue(app.buttons["Autoplay"].exists)
        }
    }
    
    func testPrivacySection() throws {
        // Navigate to settings if possible
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Test privacy section elements
            XCTAssertTrue(app.staticTexts["Privacy"].exists)
            XCTAssertTrue(app.buttons["Data Usage"].exists)
            XCTAssertTrue(app.buttons["Location Services"].exists)
        }
    }
    
    func testSignOutButton() throws {
        // Navigate to settings if possible
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Test sign out button
            let signOutButton = app.buttons["Sign Out"]
            XCTAssertTrue(signOutButton.exists)
            
            // Test sign out confirmation
            signOutButton.tap()
            
            // Check for confirmation alert
            let alert = app.alerts.firstMatch
            if alert.exists {
                XCTAssertTrue(alert.staticTexts["Sign Out"].exists)
                XCTAssertTrue(alert.buttons["Cancel"].exists)
                XCTAssertTrue(alert.buttons["Sign Out"].exists)
                
                // Cancel the sign out
                alert.buttons["Cancel"].tap()
            }
        }
    }
    
    func testDeleteAccountButton() throws {
        // Navigate to settings if possible
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Test delete account button
            let deleteAccountButton = app.buttons["Delete Account"]
            XCTAssertTrue(deleteAccountButton.exists)
            
            // Test delete account confirmation
            deleteAccountButton.tap()
            
            // Check for confirmation alert
            let alert = app.alerts.firstMatch
            if alert.exists {
                XCTAssertTrue(alert.staticTexts["Delete Account"].exists)
                XCTAssertTrue(alert.buttons["Cancel"].exists)
                XCTAssertTrue(alert.buttons["Delete"].exists)
                
                // Cancel the deletion
                alert.buttons["Cancel"].tap()
            }
        }
    }
    
    func testSettingsViewPerformance() throws {
        // Test performance of settings view loading
        let settingsButton = app.buttons["Settings"]
        if settingsButton.exists {
            measure {
                settingsButton.tap()
                // Wait for view to load
                XCTAssertTrue(app.navigationBars["Settings"].waitForExistence(timeout: 2))
            }
        }
    }
} 