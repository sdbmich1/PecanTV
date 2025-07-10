# 🚀 Production Deployment Guide for PecanTV

## Overview
This guide covers deploying PecanTV for testing with a real iPhone, connecting to Neon database, and using a production CDN.

## 📱 **iPhone Testing Requirements**

### 1. **API Configuration Changes**

**Current Issue:** The app is hardcoded to `localhost:8000` which won't work on a real iPhone.

**Solution:** Update `PecanTV/PECANTV/PECANTV/Core/Config/APIConfig.swift`:

```swift
struct APIConfig {
    // Production API URL - Update this for iPhone testing
    static let baseURL = "https://your-api-domain.com" // Production URL
    
    // Alternative URLs for different environments
    static let ngrokURL = "https://your-ngrok-url.ngrok.io" // For temporary testing
    static let productionURL = "https://api.pecantv.com" // Final production URL
    
    // ... rest of the file
}
```

### 2. **Temporary Testing Options**

**Option A: Ngrok Tunnel (Quick Testing)**
```bash
# Install ngrok
brew install ngrok

# Create tunnel to your local API
ngrok http 8000

# Update APIConfig.swift with the ngrok URL
static let baseURL = "https://abc123.ngrok.io"
```

**Option B: Deploy to Cloud (Recommended)**
- Deploy API to Heroku, Railway, or similar
- Update `baseURL` to your deployed API URL

## 🗄️ **Neon Database Configuration**

### 1. **Environment Variables**

Create `api/.env` file:
```bash
# Production Environment
ENVIRONMENT=production
DEBUG=false

# Neon Database (Get from Neon dashboard)
DATABASE_URL=postgresql://username:password@your-neon-host.neon.tech/pecantv?sslmode=require

# JWT Security (Generate a secure key)
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_MINUTE=100
RATE_LIMIT_HOUR=1000

# CORS for Production
CORS_ALLOWED_ORIGINS=https://your-app-domain.com,https://www.your-app-domain.com
CORS_ALLOW_CREDENTIALS=true
```

### 2. **Database Migration**

```bash
# Test Neon connection
cd api
python3 -c "from database import test_database_connection; test_database_connection()"

# If using SQLite currently, migrate to Neon:
# 1. Export current data
# 2. Import to Neon
# 3. Update DATABASE_URL
```

## 🖼️ **CDN Configuration**

### 1. **Image Optimization Service**

Update `PecanTV/PECANTV/PECANTV/Services/ImageOptimizationService.swift`:

```swift
class ImageOptimizationService {
    // CDN Configuration - Update for production
    static let cloudflareDomain = "https://images.pecantv.com"  // Your CDN domain
    // static let cloudflareDomain = "https://your-cdn-domain.com"  // Alternative CDN
    
    // For testing, you can use:
    // static let cloudflareDomain = "https://your-ngrok-url.ngrok.io"  // Ngrok testing
}
```

### 2. **CDN Setup Options**

**Option A: Cloudflare Images**
- Upload images to Cloudflare Images
- Use Cloudflare's image optimization API

**Option B: AWS CloudFront + S3**
- Store images in S3
- Serve through CloudFront with image optimization

**Option C: Cloudinary**
- Upload to Cloudinary
- Use their transformation API

## 🔒 **Security Configuration**

### 1. **Production Security Settings**

The security middleware is already configured for production. Key settings:

```python
# In security_config.py - these are already production-ready
ENVIRONMENT = "production"
DEBUG = False
JWT_SECRET_KEY = "your-secure-key"  # Change this!
CORS_ALLOWED_ORIGINS = ["https://your-domain.com"]
```

### 2. **SSL/HTTPS Requirements**

- **API must be served over HTTPS** for iPhone testing
- **CDN must be HTTPS**
- **All image URLs must be HTTPS**

## 🚀 **Deployment Steps**

### 1. **API Deployment**

**Option A: Heroku**
```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-pecantv-api
heroku config:set DATABASE_URL="your-neon-url"
heroku config:set JWT_SECRET_KEY="your-secret"
git push heroku main
```

**Option B: Railway**
```bash
# Connect GitHub repo to Railway
# Set environment variables in Railway dashboard
# Deploy automatically
```

### 2. **Database Migration**

```bash
# Export current SQLite data
sqlite3 pecantv.db ".dump" > backup.sql

# Import to Neon (using psql or similar)
psql "your-neon-connection-string" < backup.sql
```

### 3. **Image Migration**

```bash
# Upload all images from pecantv_series/ to your CDN
# Update database with new CDN URLs
python3 update_image_urls_to_cdn.py
```

## 📱 **iPhone Testing Checklist**

### 1. **Build Configuration**
- [ ] Update `APIConfig.swift` with production URL
- [ ] Update `ImageOptimizationService.swift` with CDN URL
- [ ] Test with ngrok first, then deploy to cloud

### 2. **Network Requirements**
- [ ] API accessible over HTTPS
- [ ] CDN accessible over HTTPS
- [ ] CORS properly configured
- [ ] No localhost references

### 3. **Security Verification**
- [ ] JWT tokens working
- [ ] Rate limiting active
- [ ] Input validation working
- [ ] Security headers present

## 🔧 **Testing Commands**

### 1. **API Health Check**
```bash
curl https://your-api-domain.com/health
```

### 2. **Security Test**
```bash
cd api
python3 run_security_tests.py
```

### 3. **Database Connection**
```bash
cd api
python3 -c "from database import test_database_connection; test_database_connection()"
```

## 🚨 **Common Issues & Solutions**

### 1. **"Could not connect to server" on iPhone**
- **Cause:** localhost URL in app
- **Solution:** Update `APIConfig.swift` with production URL

### 2. **CORS Errors**
- **Cause:** CORS not configured for your domain
- **Solution:** Update `CORS_ALLOWED_ORIGINS` in `.env`

### 3. **Database Connection Failed**
- **Cause:** Wrong Neon URL or SSL settings
- **Solution:** Check `DATABASE_URL` format and SSL mode

### 4. **Images Not Loading**
- **Cause:** CDN URLs not updated
- **Solution:** Update image URLs in database and app

## 📊 **Performance Optimization**

### 1. **Database Optimization**
- Neon connection pooling already configured
- Indexes on frequently queried columns
- Query optimization

### 2. **CDN Optimization**
- Image compression and WebP conversion
- Caching headers
- Geographic distribution

### 3. **API Optimization**
- Rate limiting configured
- Security middleware optimized
- Response caching where appropriate

## ✅ **Final Checklist**

Before iPhone testing:
- [ ] API deployed and accessible over HTTPS
- [ ] Database migrated to Neon
- [ ] Images uploaded to CDN
- [ ] App configured with production URLs
- [ ] Security tests passing
- [ ] CORS properly configured
- [ ] JWT authentication working
- [ ] All endpoints responding correctly

## 🆘 **Support**

If you encounter issues:
1. Check API logs: `heroku logs --tail` (if using Heroku)
2. Test API endpoints directly with curl
3. Verify database connection
4. Check CORS configuration
5. Review security test results 