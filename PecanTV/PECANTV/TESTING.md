# PecanTV iOS App Testing Guide

This document outlines the comprehensive testing strategy for the PecanTV iOS app, including unit tests, UI tests, and API integration tests.

## Test Structure

### Unit Tests (`PECANTVTests/`)
- **ProfileViewTests.swift**: Tests for ProfileView SwiftUI component
- **SettingsViewTests.swift**: Tests for SettingsView SwiftUI component  
- **APIIntegrationTests.swift**: Tests for FastAPI backend integration

### UI Tests (`PECANTVUITests/`)
- **ProfileUITests.swift**: UI tests for ProfileView user interactions
- **SettingsUITests.swift**: UI tests for SettingsView user interactions
- **AuthenticationUITests.swift**: UI tests for authentication flow
- **PECANTVUITests.swift**: Existing comprehensive UI tests
- **PECANTVUITestsLaunchTests.swift**: App launch tests

## Running Tests

### In Xcode
1. Open `PecanTV.xcodeproj` in Xcode
2. Select the test target (`PECANTVTests` or `PECANTVUITests`)
3. Press `Cmd+U` to run all tests
4. Or select individual test methods and press `Cmd+U`

### From Command Line
```bash
# Run unit tests
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -destination 'platform=iOS Simulator,name=iPhone 15'

# Run UI tests
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -destination 'platform=iOS Simulator,name=iPhone 15' -only-testing:PECANTVUITests
```

## Test Categories

### 1. Unit Tests

#### ProfileViewTests
- Tests ProfileView initialization with mock user data
- Verifies user information display
- Tests subscription information display
- Tests navigation functionality
- Tests quick actions functionality
- Performance testing for view rendering

#### SettingsViewTests
- Tests SettingsView initialization
- Verifies settings sections (Account, Preferences, Privacy)
- Tests sign out functionality
- Tests delete account functionality
- Performance testing for view rendering

#### APIIntegrationTests
- Tests FastAPI health endpoint
- Tests subscription plans endpoint
- Tests content and series endpoints
- Tests authentication flow (register/login)
- Tests subscription creation
- Tests error handling

### 2. UI Tests

#### ProfileUITests
- Tests navigation to profile view
- Verifies profile UI elements exist
- Tests subscription section display
- Tests quick actions buttons
- Tests account information display
- Performance testing for UI interactions

#### SettingsUITests
- Tests navigation to settings view
- Tests account section interactions
- Tests preferences section interactions
- Tests privacy section interactions
- Tests sign out confirmation flow
- Tests delete account confirmation flow

#### AuthenticationUITests
- Tests login flow with valid credentials
- Tests registration flow with new user
- Tests subscription plan selection
- Tests payment method setup
- Tests forgot password flow
- Tests authentication error handling
- Performance testing for authentication

## Test Data

### Mock User Data
```swift
let mockUser = User(
    id: 1,
    email: "test@pecantv.com",
    firstName: "Test",
    lastName: "User",
    stripeCustomerId: "cus_test123",
    subscriptionStatus: "active",
    subscriptionPlan: "Premium",
    createdAt: Date(),
    updatedAt: Date()
)
```

### API Test Endpoints
- Base URL: `http://localhost:8000`
- Health: `/health`
- Subscription Plans: `/subscriptions/plans`
- Content: `/content?limit=5`
- Series: `/series?limit=3`
- Authentication: `/auth/register`, `/auth/login`
- Subscription Creation: `/subscriptions/create`

## Test Environment Setup

### Prerequisites
1. Xcode 15+ installed
2. iOS Simulator available
3. FastAPI backend running on localhost:8000
4. PostgreSQL database running

### Environment Variables
```bash
# API Configuration
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/pecantv

# Test Configuration
TEST_USER_EMAIL=test@pecantv.com
TEST_USER_PASSWORD=testpassword123
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: iOS Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Unit Tests
        run: |
          xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -destination 'platform=iOS Simulator,name=iPhone 15'
      - name: Run UI Tests
        run: |
          xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -destination 'platform=iOS Simulator,name=iPhone 15' -only-testing:PECANTVUITests
```

## Test Coverage Goals

### Unit Tests: 80%+
- All SwiftUI views
- All view models
- All service classes
- All utility functions

### UI Tests: Key User Flows
- Authentication flow (login/register)
- Profile management
- Settings configuration
- Subscription management
- Content browsing

### API Integration Tests: 100%
- All FastAPI endpoints
- Authentication flows
- Subscription flows
- Error handling

## Best Practices

### Unit Testing
1. Use descriptive test method names
2. Test one concept per test method
3. Use mock data for external dependencies
4. Test both success and failure scenarios
5. Use `XCTAssert` for clear assertions

### UI Testing
1. Use accessibility identifiers for reliable element selection
2. Wait for elements to exist before interacting
3. Test user flows end-to-end
4. Handle dynamic content appropriately
5. Use performance testing for critical paths

### API Testing
1. Test all HTTP status codes
2. Verify JSON response structure
3. Test authentication and authorization
4. Test error handling and edge cases
5. Use async/await for modern concurrency

## Debugging Tests

### Common Issues
1. **Element not found**: Check accessibility identifiers
2. **Timeout errors**: Increase wait timeouts
3. **API connection errors**: Verify backend is running
4. **Simulator issues**: Reset simulator content

### Debug Commands
```bash
# Reset simulator
xcrun simctl erase all

# List available simulators
xcrun simctl list devices

# Run specific test
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -only-testing:PECANTVTests/ProfileViewTests/testProfileViewInitialization
```

## Performance Testing

### Metrics to Monitor
- App launch time
- View rendering time
- API response time
- Memory usage
- CPU usage

### Performance Baselines
- App launch: < 3 seconds
- View rendering: < 1 second
- API response: < 2 seconds
- Memory usage: < 100MB

## Reporting

### Test Results
- Unit test results in Xcode test navigator
- UI test screenshots in test reports
- Performance metrics in Instruments
- API test results in console output

### Coverage Reports
- Use Xcode's built-in coverage reporting
- Generate HTML coverage reports
- Track coverage trends over time

## Maintenance

### Regular Tasks
1. Update test data when models change
2. Refresh mock responses for API changes
3. Update UI tests when UI changes
4. Review and update performance baselines
5. Clean up obsolete tests

### Test Data Management
- Use factory patterns for test data creation
- Centralize mock data in test utilities
- Version control test data files
- Document test data dependencies 