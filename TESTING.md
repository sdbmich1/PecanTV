# PecanTV Testing Documentation

## Overview

This document covers the testing setup for PecanTV, including the new Netflix-style profile and settings features, along with comprehensive E2E tests using Cypress.

## New Features Added

### 1. Enhanced Profile View
- **Location**: `PecanTV/PECANTV/PECANTV/Features/Profile/Views/ProfileView.swift`
- **Features**:
  - Netflix-style profile header with gradient avatar
  - Subscription status display
  - Quick action cards (My List, Watch History, Downloads, Help)
  - Account information section
  - Settings navigation

### 2. Settings View
- **Location**: `PecanTV/PECANTV/PECANTV/Features/Profile/Views/SettingsView.swift`
- **Features**:
  - Account management (details, billing, devices)
  - Preferences (auto-play, streaming quality, notifications)
  - Data & Storage settings
  - Support section
  - Danger zone (sign out, delete account)

### 3. Subscription Details View
- **Location**: `PecanTV/PECANTV/PECANTV/Features/Profile/Views/SubscriptionDetailsView.swift`
- **Features**:
  - Current plan display
  - Billing information
  - Plan features list
  - Upgrade/downgrade options
  - Cancellation management

## Cypress E2E Testing

### Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Install Cypress**:
   ```bash
   npx cypress install
   ```

3. **Configure Cypress**:
   - Update `cypress.config.js` with your API base URL
   - Ensure your API server is running on the configured port

### Running Tests

#### Interactive Mode
```bash
npm run cypress:open
```

#### Headless Mode
```bash
npm run cypress:run
```

#### Specific Test Suites
```bash
# Profile and Settings tests
npm run test:profile

# Authentication tests
npm run test:auth

# Subscription management tests
npm run test:subscription

# All E2E tests
npm run test:e2e
```

#### CI/CD Mode
```bash
npm run test:ci
```

### Test Structure

#### 1. Profile Tests (`cypress/e2e/profile.cy.js`)
- Profile page display
- User information validation
- Subscription status display
- Quick actions functionality
- Settings navigation
- Accessibility testing
- Responsive design testing

#### 2. Authentication Tests (`cypress/e2e/authentication.cy.js`)
- Sign up functionality
- Sign in functionality
- Password reset
- Profile management
- Session handling
- Security validation

#### 3. Subscription Tests (`cypress/e2e/subscription.cy.js`)
- Plan selection
- Payment processing
- Subscription management
- Billing operations
- Limit enforcement
- Notification handling

### Custom Commands

The tests use several custom Cypress commands:

```javascript
// Authentication
cy.login(email, password)
cy.logout()

// Navigation
cy.navigateToProfile()
cy.navigateToSettings()

// Subscription
cy.checkSubscriptionStatus()

// Settings
cy.toggleSetting(settingName)
cy.selectQuality(quality)

// Utilities
cy.waitForLoading()
cy.checkError(errorMessage)
cy.checkSuccess(successMessage)
cy.checkResponsive()
cy.checkAccessibility()
```

### Test Data

Tests use mock data for consistent testing:

```javascript
// User data
const testUser = {
  email: 'test@pecantv.com',
  password: 'password123',
  firstName: 'Test',
  lastName: 'User'
}

// Subscription data
const subscriptionData = {
  plan: 'Premium',
  price: '$14.99',
  status: 'Active',
  features: ['4K Ultra HD', '4 devices', 'Downloads', 'No ads']
}
```

## API Integration

### Backend Requirements

The tests expect the following API endpoints:

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

#### Profile
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `PUT /api/user/password` - Change password

#### Subscription
- `GET /api/subscriptions/plans` - Get available plans
- `POST /api/subscriptions/create` - Create subscription
- `PUT /api/subscriptions/update` - Update subscription
- `DELETE /api/subscriptions/cancel` - Cancel subscription

### Environment Variables

Set these environment variables for testing:

```bash
CYPRESS_BASE_URL=http://localhost:3000
CYPRESS_API_URL=http://localhost:8000
CYPRESS_TEST_USER_EMAIL=test@pecantv.com
CYPRESS_TEST_USER_PASSWORD=password123
```

## Accessibility Testing

All tests include accessibility checks using `cypress-axe`:

```javascript
cy.checkAccessibility()
```

This validates:
- ARIA labels
- Color contrast
- Keyboard navigation
- Screen reader compatibility

## Responsive Testing

Tests verify the app works across different screen sizes:

```javascript
cy.checkResponsive()
```

Tests mobile (375x667), tablet (768x1024), and desktop (1280x720) viewports.

## Error Handling

Tests verify proper error handling:

```javascript
// Network errors
cy.intercept('GET', '/api/user/profile', { forceNetworkError: true })
cy.checkError('Unable to load profile')

// API errors
cy.intercept('POST', '/api/auth/login', { statusCode: 500 })
cy.checkError('Server error')
```

## Performance Testing

Tests include performance checks:

```javascript
// Page load time
cy.visit('/profile')
cy.get('[data-testid=profile-header]').should('be.visible')
cy.get('@pageLoad').should('be.lessThan', 3000)

// API response time
cy.waitForAPI('GET', '/api/user/profile', 'profileLoad')
cy.get('@profileLoad').should('have.property', 'response.statusCode', 200)
```

## Continuous Integration

### GitHub Actions

Create `.github/workflows/cypress.yml`:

```yaml
name: Cypress Tests
on: [push, pull_request]
jobs:
  cypress-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cypress-io/github-action@v6
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          browser: chrome
          record: true
```

### Local Development

For local development, run tests in watch mode:

```bash
npm run cypress:open
```

This opens the Cypress Test Runner for interactive testing.

## Troubleshooting

### Common Issues

1. **Tests failing due to timing**:
   - Increase `defaultCommandTimeout` in `cypress.config.js`
   - Add explicit waits for dynamic content

2. **API not responding**:
   - Ensure your API server is running
   - Check the `baseUrl` in `cypress.config.js`
   - Verify API endpoints are accessible

3. **Authentication issues**:
   - Check test user credentials
   - Ensure authentication endpoints are working
   - Verify session management

### Debug Mode

Run tests with debug information:

```bash
DEBUG=cypress:* npm run cypress:run
```

### Video Recording

Tests automatically record videos in `cypress/videos/` for failed tests.

### Screenshots

Failed tests automatically capture screenshots in `cypress/screenshots/`.

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Data Cleanup**: Clean up test data after each test
3. **Realistic Data**: Use realistic test data
4. **Error Scenarios**: Test both success and error paths
5. **Accessibility**: Always include accessibility checks
6. **Performance**: Monitor test execution time
7. **Maintenance**: Keep tests updated with UI changes

## Contributing

When adding new features:

1. Write corresponding E2E tests
2. Include accessibility checks
3. Test error scenarios
4. Update this documentation
5. Ensure tests pass in CI/CD

## Support

For testing issues:
1. Check the Cypress documentation
2. Review test logs and screenshots
3. Verify API endpoints are working
4. Check environment configuration 