//
//  AuthenticationUITests.swift
//  PECANTVUITests
//
//  Created by Sean Brown on 7/2/25.
//

import XCTest

final class AuthenticationUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
    }
    
    func testLoginFlow() throws {
        // Test login flow
        let emailTextField = app.textFields["Email"]
        let passwordSecureTextField = app.secureTextFields["Password"]
        let loginButton = app.buttons["Sign In"]
        
        if emailTextField.exists && passwordSecureTextField.exists && loginButton.exists {
            // Enter test credentials
            emailTextField.tap()
            emailTextField.typeText("test@pecantv.com")
            
            passwordSecureTextField.tap()
            passwordSecureTextField.typeText("testpassword123")
            
            // Tap login button
            loginButton.tap()
            
            // Wait for login to complete
            XCTAssertTrue(app.navigationBars["PecanTV"].waitForExistence(timeout: 5))
        }
    }
    
    func testRegistrationFlow() throws {
        // Test registration flow
        let signUpButton = app.buttons["Sign Up"]
        if signUpButton.exists {
            signUpButton.tap()
            
            // Fill registration form
            let firstNameTextField = app.textFields["First Name"]
            let lastNameTextField = app.textFields["Last Name"]
            let emailTextField = app.textFields["Email"]
            let passwordSecureTextField = app.secureTextFields["Password"]
            let confirmPasswordSecureTextField = app.secureTextFields["Confirm Password"]
            let createAccountButton = app.buttons["Create Account"]
            
            if firstNameTextField.exists {
                firstNameTextField.tap()
                firstNameTextField.typeText("Test")
                
                lastNameTextField.tap()
                lastNameTextField.typeText("User")
                
                emailTextField.tap()
                emailTextField.typeText("test\(Int.random(in: 1000...9999))@pecantv.com")
                
                passwordSecureTextField.tap()
                passwordSecureTextField.typeText("testpassword123")
                
                confirmPasswordSecureTextField.tap()
                confirmPasswordSecureTextField.typeText("testpassword123")
                
                // Tap create account button
                createAccountButton.tap()
                
                // Wait for registration to complete
                XCTAssertTrue(app.staticTexts["Choose Your Plan"].waitForExistence(timeout: 5))
            }
        }
    }
    
    func testSubscriptionSelection() throws {
        // Test subscription plan selection
        let basicPlanButton = app.buttons["Basic Plan"]
        let standardPlanButton = app.buttons["Standard Plan"]
        let premiumPlanButton = app.buttons["Premium Plan"]
        
        if basicPlanButton.exists {
            // Test basic plan selection
            basicPlanButton.tap()
            
            // Verify plan details are shown
            XCTAssertTrue(app.staticTexts["$8.99/month"].exists)
            XCTAssertTrue(app.staticTexts["480p"].exists)
            
            // Test continue button
            let continueButton = app.buttons["Continue"]
            if continueButton.exists {
                continueButton.tap()
                
                // Wait for payment setup
                XCTAssertTrue(app.staticTexts["Payment Method"].waitForExistence(timeout: 3))
            }
        }
        
        if standardPlanButton.exists {
            // Test standard plan selection
            standardPlanButton.tap()
            
            // Verify plan details are shown
            XCTAssertTrue(app.staticTexts["$12.99/month"].exists)
            XCTAssertTrue(app.staticTexts["1080p"].exists)
        }
        
        if premiumPlanButton.exists {
            // Test premium plan selection
            premiumPlanButton.tap()
            
            // Verify plan details are shown
            XCTAssertTrue(app.staticTexts["$14.99/month"].exists)
            XCTAssertTrue(app.staticTexts["4K"].exists)
        }
    }
    
    func testPaymentSetup() throws {
        // Test payment method setup
        let cardNumberTextField = app.textFields["Card Number"]
        let expiryTextField = app.textFields["MM/YY"]
        let cvvTextField = app.secureTextFields["CVV"]
        let nameTextField = app.textFields["Name on Card"]
        let startSubscriptionButton = app.buttons["Start Subscription"]
        
        if cardNumberTextField.exists {
            // Enter test payment information
            cardNumberTextField.tap()
            cardNumberTextField.typeText("4242424242424242")
            
            expiryTextField.tap()
            expiryTextField.typeText("12/25")
            
            cvvTextField.tap()
            cvvTextField.typeText("123")
            
            nameTextField.tap()
            nameTextField.typeText("Test User")
            
            // Start subscription
            startSubscriptionButton.tap()
            
            // Wait for subscription to complete
            XCTAssertTrue(app.navigationBars["PecanTV"].waitForExistence(timeout: 10))
        }
    }
    
    func testForgotPassword() throws {
        // Test forgot password flow
        let forgotPasswordButton = app.buttons["Forgot Password?"]
        if forgotPasswordButton.exists {
            forgotPasswordButton.tap()
            
            // Verify forgot password screen
            XCTAssertTrue(app.staticTexts["Reset Password"].exists)
            
            let emailTextField = app.textFields["Email"]
            let resetButton = app.buttons["Reset Password"]
            
            if emailTextField.exists {
                emailTextField.tap()
                emailTextField.typeText("test@pecantv.com")
                
                resetButton.tap()
                
                // Verify success message
                XCTAssertTrue(app.staticTexts["Check your email"].waitForExistence(timeout: 3))
            }
        }
    }
    
    func testAuthenticationErrors() throws {
        // Test authentication error handling
        let emailTextField = app.textFields["Email"]
        let passwordSecureTextField = app.secureTextFields["Password"]
        let loginButton = app.buttons["Sign In"]
        
        if emailTextField.exists {
            // Test invalid email
            emailTextField.tap()
            emailTextField.typeText("invalid-email")
            
            passwordSecureTextField.tap()
            passwordSecureTextField.typeText("password")
            
            loginButton.tap()
            
            // Verify error message
            XCTAssertTrue(app.staticTexts["Invalid email format"].waitForExistence(timeout: 3))
        }
    }
    
    func testAuthenticationPerformance() throws {
        // Test performance of authentication flow
        measure {
            let emailTextField = app.textFields["Email"]
            let passwordSecureTextField = app.secureTextFields["Password"]
            let loginButton = app.buttons["Sign In"]
            
            if emailTextField.exists {
                emailTextField.tap()
                emailTextField.typeText("test@pecantv.com")
                
                passwordSecureTextField.tap()
                passwordSecureTextField.typeText("testpassword123")
                
                loginButton.tap()
                
                // Wait for login to complete
                XCTAssertTrue(app.navigationBars["PecanTV"].waitForExistence(timeout: 5))
            }
        }
    }
} 