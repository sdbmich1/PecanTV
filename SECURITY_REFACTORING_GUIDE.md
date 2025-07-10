# Security Refactoring Guide

## Critical Security Fixes

### 1. Fix Broken Access Control

**File**: `api/main.py`

**Current Code** (Vulnerable):
```python
@app.get("/favorites/{user_id}")
def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    """Get all favorites for a user"""
    favorites = crud.get_user_favorites(db, user_id=user_id)
    # ... rest of function
```

**Refactored Code** (Secure):
```python
from fastapi import Depends, HTTPException, status
from enhanced_auth_service import EnhancedAuthService

def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    auth_service = EnhancedAuthService()
    try:
        user_data = auth_service.verify_token(token)
        user = crud.get_user_by_id(db, user_data.get("user_id"))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/favorites/{user_id}")
def get_user_favorites(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all favorites for a user"""
    # Authorization check
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only view your own favorites"
        )
    
    favorites = crud.get_user_favorites(db, user_id=user_id)
    # ... rest of function
```

### 2. Fix Password Hashing

**File**: `api/crud.py`

**Current Code** (Vulnerable):
```python
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # Hash the password
    password_hash = hashlib.sha256(user.password.encode()).hexdigest()
    
    db_user = models.User(
        email=user.email,
        password_hash=password_hash,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

**Refactored Code** (Secure):
```python
from enhanced_auth_service import EnhancedAuthService

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # Use enhanced auth service for secure password handling
    auth_service = EnhancedAuthService()
    
    # Validate password strength
    password_validation = auth_service.validate_password_strength(user.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
        )
    
    # Hash password securely
    password_hash = auth_service.get_password_hash(user.password)
    
    db_user = models.User(
        email=user.email,
        password_hash=password_hash,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_password(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if user:
        auth_service = EnhancedAuthService()
        if auth_service.verify_password(password, user.password_hash):
            return user
    return None
```

### 3. Fix Input Validation

**File**: `api/crud.py`

**Current Code** (Vulnerable):
```python
def search_content(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.Content]:
    return db.query(models.Content).filter(
        or_(
            models.Content.title.ilike(f"%{query}%"),
            models.Content.description.ilike(f"%{query}%")
        )
    ).offset(skip).limit(limit).all()
```

**Refactored Code** (Secure):
```python
from security_middleware import InputValidator
from fastapi import HTTPException, status

def search_content(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.Content]:
    # Input validation
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    if len(query) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query too long (max 100 characters)"
        )
    
    # Sanitize input
    is_valid, error_msg = InputValidator.validate_input(query, "search_query")
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search query: {error_msg}"
        )
    
    # Sanitize the query
    sanitized_query = InputValidator.sanitize_input(query)
    
    return db.query(models.Content).filter(
        or_(
            models.Content.title.ilike(f"%{sanitized_query}%"),
            models.Content.description.ilike(f"%{sanitized_query}%")
        )
    ).offset(skip).limit(limit).all()
```

### 4. Fix API Endpoints with Parameter Validation

**File**: `api/main.py`

**Current Code** (Vulnerable):
```python
def get_content(
    skip: int = 0,
    limit: int = 500,
    type: str = None,
    genre: str = None,
    db: Session = Depends(get_db)
):
```

**Refactored Code** (Secure):
```python
from fastapi import Query, HTTPException, status
from typing import Optional

def get_content(
    skip: int = Query(0, ge=0, le=1000, description="Number of items to skip"),
    limit: int = Query(500, ge=1, le=1000, description="Number of items to return"),
    type: Optional[str] = Query(None, regex="^(FILM|SERIES)$", description="Content type filter"),
    genre: Optional[str] = Query(None, max_length=50, description="Genre filter"),
    db: Session = Depends(get_db)
):
    # Additional validation
    if type and type not in ["FILM", "SERIES"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type"
        )
    
    if genre:
        # Validate genre input
        is_valid, error_msg = InputValidator.validate_input(genre, "genre")
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid genre: {error_msg}"
            )
    
    return crud.get_content(db, skip=skip, limit=limit, type=type, genre=genre)
```

### 5. Add Security Headers Middleware

**File**: `api/security_middleware.py`

**Add to existing middleware**:
```python
class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "media-src 'self' https:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        }
    
    def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response

# Add to main.py
app.middleware("http")(SecurityHeadersMiddleware())
```

### 6. Fix CDN Endpoint SSRF Protection

**File**: `api/main.py`

**Current Code** (Vulnerable):
```python
@app.get("/cdn-cgi/image/{params:path}")
async def cdn_image_optimization(params: str, url: str = None, request: Request = None):
    # ... existing code
    if (url.startswith('http://') or url.startswith('https://')):
        response = requests.get(url, timeout=10)
```

**Refactored Code** (Secure):
```python
from urllib.parse import urlparse
import ipaddress
from typing import List

class URLValidator:
    """Validate URLs to prevent SSRF attacks"""
    
    ALLOWED_DOMAIN_SUFFIXES = [
        '.googleapis.com',
        '.cloudflare.com',
        '.amazonaws.com',
        '.yourdomain.com'  # Add your domains
    ]
    
    BLOCKED_IP_RANGES = [
        '127.0.0.0/8',      # Localhost
        '10.0.0.0/8',       # Private network
        '172.16.0.0/12',    # Private network
        '192.168.0.0/16',   # Private network
        '169.254.0.0/16',   # Link-local
        '::1/128',          # IPv6 localhost
        'fe80::/10',        # IPv6 link-local
    ]
    
    @classmethod
    def is_allowed_url(cls, url: str) -> bool:
        """Check if URL is allowed (no internal IPs, valid domain)"""
        try:
            parsed = urlparse(url)
            
            # Check if it's an IP address
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                
                # Block private and loopback IPs
                if ip.is_private or ip.is_loopback:
                    return False
                
                # Check against blocked IP ranges
                for blocked_range in cls.BLOCKED_IP_RANGES:
                    if ip in ipaddress.ip_network(blocked_range):
                        return False
                        
            except ValueError:
                # Not an IP address, check domain
                pass
            
            # Check domain against allowed suffixes
            hostname = parsed.hostname.lower()
            return any(hostname.endswith(suffix) for suffix in cls.ALLOWED_DOMAIN_SUFFIXES)
            
        except Exception:
            return False

@app.get("/cdn-cgi/image/{params:path}")
async def cdn_image_optimization(params: str, url: str = None, request: Request = None):
    """
    CDN-style image optimization endpoint with SSRF protection
    """
    try:
        # Validate URL parameter
        if not url:
            raise HTTPException(status_code=400, detail="URL parameter required")
        
        # Decode URL if percent-encoded
        url = urllib.parse.unquote(url)
        
        # Handle remote URLs with SSRF protection
        if (url.startswith('http://') or url.startswith('https://')):
            # Validate URL to prevent SSRF
            if not URLValidator.is_allowed_url(url):
                raise HTTPException(
                    status_code=400, 
                    detail="URL not allowed for security reasons"
                )
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return FileResponse(
                        io.BytesIO(response.content),
                        media_type=response.headers.get('content-type', 'image/jpeg'),
                        headers={
                            'Cache-Control': 'public, max-age=86400',
                            'CDN-Optimized': 'true'
                        }
                    )
                else:
                    raise HTTPException(status_code=502, detail="Failed to fetch remote image")
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Failed to fetch remote image: {e}")
        
        # ... rest of existing code for local files
```

### 7. Add Comprehensive Logging

**File**: `api/security_logging.py`

**Create new file**:
```python
import structlog
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import Request

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class SecurityLogger:
    """Centralized security logging"""
    
    @staticmethod
    def log_security_event(
        event_type: str,
        user_id: int = None,
        ip_address: str = None,
        user_agent: str = None,
        details: Dict[str, Any] = None,
        severity: str = "INFO"
    ):
        """Log security events"""
        log_data = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "details": details or {}
        }
        
        if user_id:
            log_data["user_id"] = user_id
        if ip_address:
            log_data["ip_address"] = ip_address
        if user_agent:
            log_data["user_agent"] = user_agent
        
        if severity == "ERROR":
            logger.error("security_event", **log_data)
        elif severity == "WARNING":
            logger.warning("security_event", **log_data)
        else:
            logger.info("security_event", **log_data)
    
    @staticmethod
    def log_authentication_attempt(
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        details: Dict[str, Any] = None
    ):
        """Log authentication attempts"""
        SecurityLogger.log_security_event(
            event_type="authentication_attempt",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "email": email,
                "success": success,
                **details or {}
            },
            severity="WARNING" if not success else "INFO"
        )
    
    @staticmethod
    def log_access_attempt(
        user_id: int,
        resource: str,
        action: str,
        success: bool,
        ip_address: str,
        details: Dict[str, Any] = None
    ):
        """Log access attempts"""
        SecurityLogger.log_security_event(
            event_type="access_attempt",
            user_id=user_id,
            ip_address=ip_address,
            details={
                "resource": resource,
                "action": action,
                "success": success,
                **details or {}
            },
            severity="WARNING" if not success else "INFO"
        )
    
    @staticmethod
    def log_input_validation_failure(
        input_type: str,
        input_value: str,
        ip_address: str,
        details: Dict[str, Any] = None
    ):
        """Log input validation failures"""
        SecurityLogger.log_security_event(
            event_type="input_validation_failure",
            ip_address=ip_address,
            details={
                "input_type": input_type,
                "input_value": input_value[:100],  # Truncate for security
                **details or {}
            },
            severity="WARNING"
        )

# Usage in endpoints
def get_user_favorites(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Get all favorites for a user"""
    # Authorization check
    if current_user.id != user_id:
        SecurityLogger.log_access_attempt(
            user_id=current_user.id,
            resource=f"favorites/{user_id}",
            action="read",
            success=False,
            ip_address=request.client.host if request else None,
            details={"attempted_access_user_id": user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only view your own favorites"
        )
    
    SecurityLogger.log_access_attempt(
        user_id=current_user.id,
        resource=f"favorites/{user_id}",
        action="read",
        success=True,
        ip_address=request.client.host if request else None
    )
    
    favorites = crud.get_user_favorites(db, user_id=user_id)
    # ... rest of function
```

### 8. Environment Configuration

**File**: `api/config.py`

**Create new file**:
```python
import os
from typing import List
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Database
    DATABASE_URL: str
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Security settings
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v):
        if not v or v == "your-secret-key-change-in-production":
            raise ValueError("JWT_SECRET_KEY must be set and secure")
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    class Config:
        env_file = ".env"

# Validate settings on startup
settings = Settings()
```

## Implementation Steps

### Phase 1: Critical Fixes (Immediate)
1. Fix broken access control in favorites endpoint
2. Replace SHA-256 with bcrypt
3. Add input validation to search
4. Remove debug endpoints

### Phase 2: Security Headers (Week 1)
1. Add security headers middleware
2. Implement CSP
3. Add rate limiting headers

### Phase 3: Input Validation (Week 2)
1. Add comprehensive input validation
2. Implement URL validation for CDN
3. Add parameter validation to all endpoints

### Phase 4: Logging & Monitoring (Week 3)
1. Implement security logging
2. Add audit trails
3. Set up monitoring alerts

### Phase 5: Testing & Validation (Week 4)
1. Add security tests
2. Conduct penetration testing
3. Validate all fixes

## Testing the Fixes

### 1. Test Access Control
```bash
# Test unauthorized access
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/favorites/999
# Should return 403 Forbidden
```

### 2. Test Input Validation
```bash
# Test SQL injection
curl "http://localhost:8000/search?q=';%20DROP%20TABLE%20users;%20--"
# Should return 400 Bad Request

# Test XSS
curl "http://localhost:8000/search?q=<script>alert('xss')</script>"
# Should return 400 Bad Request
```

### 3. Test Security Headers
```bash
curl -I http://localhost:8000/health
# Should include security headers
```

### 4. Test Rate Limiting
```bash
# Make many requests quickly
for i in {1..70}; do curl http://localhost:8000/health; done
# Should get rate limited after 60 requests
```

## Monitoring

After implementing these fixes, monitor:

1. **Security Events**: Check logs for failed authentication attempts, access violations
2. **Rate Limiting**: Monitor for excessive requests
3. **Input Validation**: Track blocked malicious inputs
4. **Performance**: Ensure security measures don't impact performance

## Conclusion

These refactoring changes will significantly improve the security posture of the PecanTV application. Implement them in phases, test thoroughly, and monitor for any issues. Remember to update documentation and train the development team on the new security practices. 