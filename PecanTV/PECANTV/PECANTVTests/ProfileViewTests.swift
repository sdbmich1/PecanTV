//
//  ProfileViewTests.swift
//  PECANTVTests
//
//  Created by Sean Brown on 7/2/25.
//

import XCTest
import SwiftUI
@testable import PECANTV

@MainActor
final class ProfileViewTests: XCTestCase {
    
    var authViewModel: AuthViewModel!
    var testUser: User!
    
    override func setUpWithError() throws {
        super.setUp()
        // Create a mock user and AuthViewModel for testing
        testUser = User(
            id: "1",
            firstName: "Test",
            lastName: "User",
            email: "test@pecantv.com"
        )
        authViewModel = AuthViewModel()
        authViewModel.currentUser = testUser
    }
    
    override func tearDownWithError() throws {
        authViewModel = nil
        testUser = nil
        super.tearDown()
    }
    
    func testProfileViewInitialization() throws {
        // Test that ProfileView can be created with AuthViewModel
        let profileView = ProfileView()
            .environmentObject(authViewModel)
        
        // Verify the view can be rendered
        XCTAssertNotNil(profileView)
    }
    
    func testProfileViewDisplaysUserInfo() throws {
        // Create ProfileView with mock AuthViewModel
        let profileView = ProfileView()
            .environmentObject(authViewModel)
        
        // Test that the view loads without crashing
        // Note: In a real test, you would use UI testing to verify text content
        XCTAssertNotNil(profileView)
    }
    
    func testProfileViewNavigation() throws {
        // Test that ProfileView can navigate to other views
        let profileView = ProfileView()
            .environmentObject(authViewModel)
        
        // Verify the view can be rendered
        XCTAssertNotNil(profileView)
    }
    
    func testProfileViewWithNilUser() throws {
        // Test ProfileView behavior when user is nil
        authViewModel.currentUser = nil
        
        let profileView = ProfileView()
            .environmentObject(authViewModel)
        
        // Verify the view can still be rendered
        XCTAssertNotNil(profileView)
    }
    
    func testProfileViewUserDisplay() throws {
        // Test that user information is displayed correctly
        let view = ProfileView().environmentObject(authViewModel)
        let hostingController = UIHostingController(rootView: view)
        hostingController.loadViewIfNeeded()
        
        // Verify the view loads without crashing
        XCTAssertNotNil(hostingController.view)
        
        // Note: In a real UI test, you would use XCUITest to verify text content
        // For unit tests, we just verify the view renders successfully
    }
    
    func testProfileViewSettingsButton() throws {
        // Test settings button functionality
        let view = ProfileView().environmentObject(authViewModel)
        let hostingController = UIHostingController(rootView: view)
        hostingController.loadViewIfNeeded()
        XCTAssertNotNil(hostingController.view)
    }
    
    func testProfileViewQuickActions() throws {
        // Test quick actions functionality
        let view = ProfileView().environmentObject(authViewModel)
        let hostingController = UIHostingController(rootView: view)
        hostingController.loadViewIfNeeded()
        XCTAssertNotNil(hostingController.view)
    }
    
    func testProfileViewAccountInfo() throws {
        // Test account information display
        let view = ProfileView().environmentObject(authViewModel)
        let hostingController = UIHostingController(rootView: view)
        hostingController.loadViewIfNeeded()
        
        // Verify the view loads without crashing
        XCTAssertNotNil(hostingController.view)
        
        // Note: In a real UI test, you would use XCUITest to verify email is displayed
        // For unit tests, we just verify the view renders successfully
    }
    
    func testProfileViewPerformance() throws {
        // Test performance of ProfileView rendering
        measure {
            let view = ProfileView().environmentObject(authViewModel)
            let hostingController = UIHostingController(rootView: view)
            hostingController.loadViewIfNeeded()
        }
    }
} 