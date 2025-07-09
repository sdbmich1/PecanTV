"""
Security configuration for PecanTV API
Centralized security settings that can be customized per environment
"""

import os
from typing import List

class SecurityConfig:
    """Security configuration class"""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Rate Limiting
    RATE_LIMIT_MINUTE = int(os.getenv("RATE_LIMIT_MINUTE", "60"))
    RATE_LIMIT_HOUR = int(os.getenv("RATE_LIMIT_HOUR", "1000"))
    
    # Account Security
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
    
    # Password Policy
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_DIGITS = os.getenv("PASSWORD_REQUIRE_DIGITS", "true").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    
    # CORS Configuration
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOWED_METHODS = os.getenv("CORS_ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
    
    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }
    
    # Content Security Policy
    CSP_DEFAULT_SRC = os.getenv("CSP_DEFAULT_SRC", "'self'")
    CSP_SCRIPT_SRC = os.getenv("CSP_SCRIPT_SRC", "'self' 'unsafe-inline' 'unsafe-eval'")
    CSP_STYLE_SRC = os.getenv("CSP_STYLE_SRC", "'self' 'unsafe-inline'")
    CSP_IMG_SRC = os.getenv("CSP_IMG_SRC", "'self' data: https:")
    CSP_FONT_SRC = os.getenv("CSP_FONT_SRC", "'self'")
    CSP_CONNECT_SRC = os.getenv("CSP_CONNECT_SRC", "'self'")
    CSP_MEDIA_SRC = os.getenv("CSP_MEDIA_SRC", "'self' https:")
    CSP_OBJECT_SRC = os.getenv("CSP_OBJECT_SRC", "'none'")
    CSP_BASE_URI = os.getenv("CSP_BASE_URI", "'self'")
    CSP_FORM_ACTION = os.getenv("CSP_FORM_ACTION", "'self'")
    
    @classmethod
    def get_csp_header(cls) -> str:
        """Get Content Security Policy header"""
        return (
            f"default-src {cls.CSP_DEFAULT_SRC}; "
            f"script-src {cls.CSP_SCRIPT_SRC}; "
            f"style-src {cls.CSP_STYLE_SRC}; "
            f"img-src {cls.CSP_IMG_SRC}; "
            f"font-src {cls.CSP_FONT_SRC}; "
            f"connect-src {cls.CSP_CONNECT_SRC}; "
            f"media-src {cls.CSP_MEDIA_SRC}; "
            f"object-src {cls.CSP_OBJECT_SRC}; "
            f"base-uri {cls.CSP_BASE_URI}; "
            f"form-action {cls.CSP_FORM_ACTION}"
        )
    
    @classmethod
    def get_security_headers(cls) -> dict:
        """Get all security headers"""
        headers = cls.SECURITY_HEADERS.copy()
        headers["Content-Security-Policy"] = cls.get_csp_header()
        return headers
    
    # Database Security
    DB_SSL_MODE = os.getenv("DB_SSL_MODE", "require" if ENVIRONMENT == "production" else "prefer")
    DB_CONNECTION_TIMEOUT = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))
    
    # File Upload Security
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,gif,webp").split(",")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_SECURITY_EVENTS = os.getenv("LOG_SECURITY_EVENTS", "true").lower() == "true"
    
    # Monitoring
    ENABLE_SECURITY_MONITORING = os.getenv("ENABLE_SECURITY_MONITORING", "true").lower() == "true"
    SECURITY_ALERT_EMAIL = os.getenv("SECURITY_ALERT_EMAIL", "")
    
    # API Security
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
    
    # Session Management
    MAX_SESSIONS_PER_USER = int(os.getenv("MAX_SESSIONS_PER_USER", "5"))
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    
    # Input Validation
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "1000"))
    ENABLE_INPUT_SANITIZATION = os.getenv("ENABLE_INPUT_SANITIZATION", "true").lower() == "true"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT.lower() == "development"
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """Get a summary of security configuration"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "rate_limiting": {
                "minute_limit": cls.RATE_LIMIT_MINUTE,
                "hour_limit": cls.RATE_LIMIT_HOUR
            },
            "account_security": {
                "max_login_attempts": cls.MAX_LOGIN_ATTEMPTS,
                "lockout_duration_minutes": cls.LOCKOUT_DURATION_MINUTES
            },
            "password_policy": {
                "min_length": cls.PASSWORD_MIN_LENGTH,
                "require_uppercase": cls.PASSWORD_REQUIRE_UPPERCASE,
                "require_lowercase": cls.PASSWORD_REQUIRE_LOWERCASE,
                "require_digits": cls.PASSWORD_REQUIRE_DIGITS,
                "require_special": cls.PASSWORD_REQUIRE_SPECIAL
            },
            "cors": {
                "allowed_origins": cls.CORS_ALLOWED_ORIGINS,
                "allow_credentials": cls.CORS_ALLOW_CREDENTIALS
            },
            "monitoring": {
                "enabled": cls.ENABLE_SECURITY_MONITORING,
                "log_security_events": cls.LOG_SECURITY_EVENTS
            }
        }

# Global configuration instance
security_config = SecurityConfig() 