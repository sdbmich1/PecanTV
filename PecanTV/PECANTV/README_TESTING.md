# PecanTV iOS App Testing Guide

This guide covers the comprehensive testing setup for the PecanTV iOS app, including unit tests, UI tests, and API integration tests.

## 🚀 Quick Start

### Prerequisites
- Xcode 15+ installed
- iOS Simulator available
- FastAPI backend running on localhost:8000
- PostgreSQL database running

### Running All Tests
```bash
cd PecanTV/PECANTV
./run_tests.sh
```

### Running Individual Test Categories
```bash
# Unit tests only
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -destination 'platform=iOS Simulator,name=iPhone 15' -only-testing:PECANTVTests

# UI tests only
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -destination 'platform=iOS Simulator,name=iPhone 15' -only-testing:PECANTVUITests
```

## 📁 Test Structure

```
PECANTV/
├── PECANTVTests/                    # Unit Tests
│   ├── ProfileViewTests.swift       # Profile view unit tests
│   ├── SettingsViewTests.swift      # Settings view unit tests
│   ├── APIIntegrationTests.swift    # API integration tests
│   └── TestUtilities.swift          # Test utilities and helpers
├── PECANTVUITests/                  # UI Tests
│   ├── ProfileUITests.swift         # Profile UI interactions
│   ├── SettingsUITests.swift        # Settings UI interactions
│   ├── AuthenticationUITests.swift  # Auth flow UI tests
│   ├── PECANTVUITests.swift         # Comprehensive UI tests
│   └── PECANTVUITestsLaunchTests.swift # App launch tests
└── run_tests.sh                     # Test runner script
```

## 🧪 Test Categories

### 1. Unit Tests (`PECANTVTests/`)

#### ProfileViewTests.swift
Tests the ProfileView SwiftUI component:
- ✅ View initialization with mock data
- ✅ User information display
- ✅ Subscription information display
- ✅ Navigation functionality
- ✅ Quick actions functionality
- ✅ Performance testing

#### SettingsViewTests.swift
Tests the SettingsView SwiftUI component:
- ✅ View initialization
- ✅ Account section functionality
- ✅ Preferences section functionality
- ✅ Privacy section functionality
- ✅ Sign out functionality
- ✅ Delete account functionality

#### APIIntegrationTests.swift
Tests FastAPI backend integration:
- ✅ Health endpoint (`/health`)
- ✅ Subscription plans endpoint (`/subscriptions/plans`)
- ✅ Content endpoint (`/content`)
- ✅ Series endpoint (`/series`)
- ✅ Authentication flow (`/auth/register`, `/auth/login`)
- ✅ Subscription creation (`/subscriptions/create`)
- ✅ Error handling

#### TestUtilities.swift
Provides test utilities and helpers:
- ✅ Mock data factory
- ✅ Test helpers for common tasks
- ✅ API test helpers
- ✅ UI test helpers
- ✅ Performance test helpers
- ✅ Custom assertions

### 2. UI Tests (`PECANTVUITests/`)

#### ProfileUITests.swift
Tests ProfileView user interactions:
- ✅ Navigation to profile view
- ✅ Profile UI elements verification
- ✅ Subscription section display
- ✅ Quick actions buttons
- ✅ Account information display
- ✅ Performance testing

#### SettingsUITests.swift
Tests SettingsView user interactions:
- ✅ Navigation to settings view
- ✅ Account section interactions
- ✅ Preferences section interactions
- ✅ Privacy section interactions
- ✅ Sign out confirmation flow
- ✅ Delete account confirmation flow

#### AuthenticationUITests.swift
Tests authentication flow:
- ✅ Login flow with valid credentials
- ✅ Registration flow with new user
- ✅ Subscription plan selection
- ✅ Payment method setup
- ✅ Forgot password flow
- ✅ Authentication error handling
- ✅ Performance testing

## 🔧 Test Configuration

### Environment Setup
```bash
# API Configuration
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/pecantv

# Test Configuration
TEST_USER_EMAIL=test@pecantv.com
TEST_USER_PASSWORD=testpassword123
```

### Mock Data
The test utilities provide mock data for:
- Users with different subscription statuses
- Subscription plans (Free, Basic, Premium, Family)
- Content items (movies, series, episodes)
- API responses

### Test Helpers
- `TestHelpers`: Common UI interaction helpers
- `APITestHelpers`: API testing utilities
- `UITestHelpers`: UI test navigation helpers
- `PerformanceTestHelpers`: Performance testing utilities

## 📊 Test Results

### Success Indicators
- ✅ All unit tests pass
- ✅ All UI tests pass
- ✅ API integration tests pass
- ✅ Performance tests within acceptable limits

### Common Issues & Solutions

#### Element Not Found
```swift
// Use accessibility identifiers
let profileButton = app.buttons["Profile"]
XCTAssertTrue(profileButton.exists)
```

#### Timeout Errors
```swift
// Increase wait timeouts
XCTAssertTrue(element.waitForExistence(timeout: 10.0))
```

#### API Connection Errors
- Verify backend is running: `curl http://localhost:8000/health`
- Check database connection
- Verify environment variables

#### Simulator Issues
```bash
# Reset simulator
xcrun simctl erase all

# List available simulators
xcrun simctl list devices
```

## 🚀 Running Tests in Xcode

### In Xcode IDE
1. Open `PECANTV.xcodeproj`
2. Select test target (`PECANTVTests` or `PECANTVUITests`)
3. Press `Cmd+U` to run all tests
4. Or select individual test methods and press `Cmd+U`

### Test Navigator
- View test results in Xcode's Test Navigator
- See test coverage in Coverage tab
- Debug failed tests with breakpoints

### Continuous Integration
```yaml
# GitHub Actions example
name: iOS Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          cd PecanTV/PECANTV
          ./run_tests.sh
```

## 📈 Performance Testing

### Metrics
- App launch time: < 3 seconds
- View rendering time: < 1 second
- API response time: < 2 seconds
- Memory usage: < 100MB

### Performance Tests
```swift
func testProfileViewPerformance() throws {
    measure {
        let hostingController = UIHostingController(rootView: profileView)
        hostingController.loadViewIfNeeded()
    }
}
```

## 🔍 Debugging Tests

### Debug Commands
```bash
# Run specific test
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -only-testing:PECANTVTests/ProfileViewTests/testProfileViewInitialization

# Run with verbose output
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -verbose

# Run on specific simulator
xcodebuild test -project PECANTV.xcodeproj -scheme PECANTV -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
```

### Test Logs
- Check Xcode console for detailed logs
- Use `print()` statements for debugging
- Enable test logging in scheme settings

## 📝 Best Practices

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

## 🎯 Test Coverage Goals

- **Unit Tests**: 80%+ coverage
- **UI Tests**: All critical user flows
- **API Tests**: 100% endpoint coverage
- **Performance Tests**: All critical paths

## 📚 Additional Resources

- [XCTest Framework Documentation](https://developer.apple.com/documentation/xctest)
- [UI Testing Best Practices](https://developer.apple.com/documentation/xctest/user_interface_tests)
- [Performance Testing Guide](https://developer.apple.com/documentation/xctest/performance_tests)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 Contributing

When adding new features:
1. Write unit tests for new SwiftUI views
2. Write UI tests for new user flows
3. Write API tests for new endpoints
4. Update test documentation
5. Ensure all tests pass before merging

## 📞 Support

For test-related issues:
1. Check the troubleshooting section above
2. Review test logs in Xcode
3. Verify environment setup
4. Contact the development team 