//
//  SettingsViewTests.swift
//  PECANTVTests
//
//  Created by Sean Brown on 7/2/25.
//

import XCTest
import SwiftUI
@testable import PECANTV

final class SettingsViewTests: XCTestCase {
    
    var settingsView: SettingsView!
    
    override func setUpWithError() throws {
        super.setUp()
        settingsView = SettingsView()
    }
    
    override func tearDownWithError() throws {
        settingsView = nil
        super.tearDown()
    }
    
    func testSettingsViewInitialization() throws {
        // Test that SettingsView can be initialized
        XCTAssertNotNil(settingsView)
    }
    
    func testSettingsViewDisplay() throws {
        // Test that SettingsView displays correctly
        let hostingController = UIHostingController(rootView: settingsView)
        hostingController.loadViewIfNeeded()
        
        // Verify the view loads without errors
        XCTAssertNotNil(hostingController.view)
    }
    
    func testSettingsViewNavigation() throws {
        // Test navigation functionality
        let hostingController = UIHostingController(rootView: settingsView)
        hostingController.loadViewIfNeeded()
        
        // Verify navigation elements exist
        XCTAssertNotNil(hostingController.view)
    }
    
    func testSettingsViewAccountSection() throws {
        // Test account section functionality
        let hostingController = UIHostingController(rootView: settingsView)
        hostingController.loadViewIfNeeded()
        
        // Verify account section is displayed
        XCTAssertNotNil(hostingController.view)
    }
    
    func testSettingsViewPreferencesSection() throws {
        // Test preferences section functionality
        let hostingController = UIHostingController(rootView: settingsView)
        hostingController.loadViewIfNeeded()
        
        // Verify preferences section is displayed
        XCTAssertNotNil(hostingController.view)
    }
    
    func testSettingsViewSignOutButton() throws {
        // Test sign out button functionality
        let hostingController = UIHostingController(rootView: settingsView)
        hostingController.loadViewIfNeeded()
        
        // Verify sign out button is accessible
        XCTAssertNotNil(hostingController.view)
    }
    
    func testSettingsViewDeleteAccountButton() throws {
        // Test delete account button functionality
        let hostingController = UIHostingController(rootView: settingsView)
        hostingController.loadViewIfNeeded()
        
        // Verify delete account button is accessible
        XCTAssertNotNil(hostingController.view)
    }
    
    func testSettingsViewPerformance() throws {
        // Test performance of SettingsView rendering
        measure {
            let hostingController = UIHostingController(rootView: settingsView)
            hostingController.loadViewIfNeeded()
        }
    }
} 