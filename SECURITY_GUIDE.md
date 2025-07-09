# PecanTV Security Guide

## Overview
This document provides comprehensive security information for the PecanTV application, including security features, best practices, and guidelines for developers and users.

## Security Features Implemented

### 1. API Security
- **Rate Limiting**: Prevents abuse with configurable limits (60 requests/minute, 1000/hour)
- **Input Validation**: Comprehensive sanitization and validation of all inputs
- **CORS Protection**: Properly configured Cross-Origin Resource Sharing
- **Security Headers**: Multiple security headers including CSP, XSS protection, and more
- **Request Logging**: Enhanced logging for security monitoring

### 2. Authentication & Authorization
- **JWT Tokens**: Secure JWT implementation with proper expiration
- **Password Hashing**: Bcrypt with 12 rounds for strong password protection
- **Account Lockout**: Automatic lockout after 5 failed login attempts
- **Session Management**: Secure session handling with activity tracking
- **Password Policy**: Enforced strong password requirements

### 3. Data Protection
- **Input Sanitization**: All inputs are sanitized to prevent injection attacks
- **SQL Injection Prevention**: Parameterized queries and input validation
- **XSS Protection**: Content Security Policy and input sanitization
- **Error Handling**: Secure error messages that don't leak sensitive information

### 4. Infrastructure Security
- **Environment Variables**: Secure handling of configuration
- **Database Security**: SSL connections and connection timeouts
- **File Upload Security**: Validation of file types and sizes
- **Dependency Security**: Regular security audits of dependencies

## Security Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-secure-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_MINUTE=60
RATE_LIMIT_HOUR=1000

# Account Security
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL=true

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://pecantv.com
CORS_ALLOW_CREDENTIALS=true

# Security Monitoring
ENABLE_SECURITY_MONITORING=true
LOG_SECURITY_EVENTS=true
```

### Security Headers
The application automatically adds the following security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: [configured policy]`

## Security Testing

### Running Security Tests
```bash
# Run comprehensive security tests
python3 api/security_tests.py

# Test with custom base URL
python3 api/security_tests.py http://your-api-url.com
```

### Security Test Coverage
- Rate limiting functionality
- Security headers validation
- CORS configuration testing
- Input validation (SQL injection, XSS)
- Authentication security
- Endpoint protection
- File upload security
- Concurrent request handling
- Error handling security

## Security Monitoring

### Security Events Logged
- Failed login attempts
- Rate limit violations
- Invalid input attempts
- Security middleware errors
- Authentication failures
- Suspicious activity patterns

### Monitoring Endpoints
- `GET /security/stats` - Get security statistics
- `GET /health` - Health check with security status

### Security Alerts
The system can be configured to send security alerts via email for:
- Multiple failed login attempts
- Rate limit violations
- Suspicious IP addresses
- Security middleware errors

## Best Practices for Developers

### 1. Input Validation
```python
# Always validate and sanitize inputs
from security_middleware import InputValidator

is_valid, error_msg = InputValidator.validate_input(user_input, "user_input")
if not is_valid:
    raise HTTPException(status_code=400, detail=error_msg)
```

### 2. Password Handling
```python
# Use the enhanced authentication service
from enhanced_auth_service import enhanced_auth_service

# Register with password validation
response = enhanced_auth_service.register_user_secure(db, user_data, request)

# Login with security features
response = enhanced_auth_service.login_user_secure(db, login_data, request)
```

### 3. Error Handling
```python
# Never expose sensitive information in errors
try:
    # Your code here
    pass
except Exception as e:
    logger.error(f"Internal error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 4. Database Security
```python
# Always use parameterized queries
from sqlalchemy import text

# Good
result = db.execute(text("SELECT * FROM users WHERE id = :user_id"), {"user_id": user_id})

# Bad - vulnerable to SQL injection
result = db.execute(text(f"SELECT * FROM users WHERE id = {user_id}"))
```

## Best Practices for Users

### 1. Password Security
- Use strong passwords (minimum 8 characters)
- Include uppercase, lowercase, numbers, and special characters
- Don't reuse passwords from other services
- Consider using a password manager

### 2. Account Security
- Keep your email address updated
- Enable two-factor authentication if available
- Monitor your account for suspicious activity
- Log out from shared devices

### 3. General Security
- Keep your browser and operating system updated
- Use HTTPS connections only
- Be cautious of phishing attempts
- Report suspicious activity

## Security Incident Response

### 1. Detecting Incidents
- Monitor security logs regularly
- Watch for unusual activity patterns
- Pay attention to security alerts
- Review failed authentication attempts

### 2. Responding to Incidents
1. **Immediate Response**
   - Isolate affected systems if necessary
   - Document the incident
   - Preserve evidence

2. **Investigation**
   - Analyze logs and security events
   - Identify the root cause
   - Assess the impact

3. **Remediation**
   - Fix security vulnerabilities
   - Update security configurations
   - Implement additional protections

4. **Recovery**
   - Restore normal operations
   - Monitor for recurrence
   - Update incident response procedures

### 3. Reporting Security Issues
If you discover a security vulnerability:
1. **Do not** publicly disclose the issue
2. Contact the development team immediately
3. Provide detailed information about the vulnerability
4. Allow time for investigation and remediation

## Compliance and Standards

### GDPR Compliance
- Data minimization and purpose limitation
- User consent and rights management
- Data protection by design
- Breach notification procedures

### Security Standards
- OWASP Top 10 compliance
- NIST Cybersecurity Framework alignment
- Industry best practices implementation
- Regular security assessments

## Security Updates and Maintenance

### Regular Security Tasks
- [ ] Update dependencies monthly
- [ ] Review security logs weekly
- [ ] Conduct security assessments quarterly
- [ ] Update security configurations as needed
- [ ] Train team on security best practices

### Security Monitoring Checklist
- [ ] Monitor failed login attempts
- [ ] Track rate limit violations
- [ ] Review suspicious IP addresses
- [ ] Check for unusual traffic patterns
- [ ] Monitor error rates and types

## Contact Information

For security-related questions or to report security issues:
- **Security Team**: security@pecantv.com
- **Emergency Contact**: security-emergency@pecantv.com
- **Bug Bounty Program**: https://pecantv.com/security

---

**Last Updated**: December 2024
**Version**: 1.0
**Next Review**: March 2025 