//
//  ProfileUITests.swift
//  PECANTVUITests
//
//  Created by Sean Brown on 7/2/25.
//

import XCTest

final class ProfileUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
    }
    
    func testProfileViewNavigation() throws {
        // Test navigation to profile view
        // This assumes there's a tab bar or navigation to profile
        let profileTab = app.tabBars.buttons["Profile"]
        if profileTab.exists {
            profileTab.tap()
            
            // Verify profile view is displayed
            XCTAssertTrue(app.navigationBars["Profile"].exists)
        }
    }
    
    func testProfileViewElements() throws {
        // Navigate to profile if possible
        let profileTab = app.tabBars.buttons["Profile"]
        if profileTab.exists {
            profileTab.tap()
            
            // Test profile elements exist
            XCTAssertTrue(app.staticTexts["Test User"].exists)
            XCTAssertTrue(app.staticTexts["test@pecantv.com"].exists)
        }
    }
    
    func testSubscriptionSection() throws {
        // Navigate to profile if possible
        let profileTab = app.tabBars.buttons["Profile"]
        if profileTab.exists {
            profileTab.tap()
            
            // Test subscription section
            XCTAssertTrue(app.staticTexts["Subscription"].exists)
            XCTAssertTrue(app.staticTexts["Premium"].exists)
            XCTAssertTrue(app.staticTexts["$14.99/month"].exists)
        }
    }
    
    func testQuickActions() throws {
        // Navigate to profile if possible
        let profileTab = app.tabBars.buttons["Profile"]
        if profileTab.exists {
            profileTab.tap()
            
            // Test quick actions buttons
            XCTAssertTrue(app.buttons["My List"].exists)
            XCTAssertTrue(app.buttons["Watch History"].exists)
            XCTAssertTrue(app.buttons["Downloads"].exists)
            XCTAssertTrue(app.buttons["Help & Support"].exists)
        }
    }
    
    func testAccountInfo() throws {
        // Navigate to profile if possible
        let profileTab = app.tabBars.buttons["Profile"]
        if profileTab.exists {
            profileTab.tap()
            
            // Test account information
            XCTAssertTrue(app.staticTexts["Member Since:"].exists)
            XCTAssertTrue(app.staticTexts["Device Limit:"].exists)
        }
    }
    
    func testProfileViewPerformance() throws {
        // Test performance of profile view loading
        let profileTab = app.tabBars.buttons["Profile"]
        if profileTab.exists {
            measure {
                profileTab.tap()
                // Wait for view to load
                XCTAssertTrue(app.navigationBars["Profile"].waitForExistence(timeout: 2))
            }
        }
    }
} 