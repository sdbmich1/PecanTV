# PecanTV API Connection Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Issue: App Rebuild Fails Due to Missing Server Connection

**Symptoms:**
- iOS app fails to build or run
- "Server Unavailable" message appears
- Network connection errors
- API health check failures

**Root Cause:**
The iOS app is trying to connect to an API server that isn't running or is configured with the wrong URL.

## 🔧 Quick Fixes

### 1. Start the API Server

```bash
# Navigate to the project root
cd /path/to/pecantv_app

# Start the API server
./quick_start.sh run

# Or manually start it
cd api
python3 main.py
```

**Expected Output:**
```
✅ API server starting on http://localhost:8000
✅ API documentation: http://localhost:8000/docs
⚠️  Press Ctrl+C to stop the server
```

### 2. Test API Connection

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response: {"status":"ok"}

# Test content endpoint
curl http://localhost:8000/content | head -c 100
```

### 3. Switch API Environment (if needed)

The app supports multiple API environments. Use the environment switcher script:

```bash
# Show current environment
./scripts/switch_api_environment.sh current

# Switch to local development
./scripts/switch_api_environment.sh local

# Switch to ngrok tunnel (for external access)
./scripts/switch_api_environment.sh ngrok

# Switch to production
./scripts/switch_api_environment.sh production
```

## 🏗️ Architecture Overview

### API Configuration Structure

The app uses a centralized configuration system:

```
PecanTV/PECANTV/PECANTV/Core/Config/APIConfig.swift
```

**Key Components:**
- `APIConfig.baseURL` - Centralized API base URL
- `APIConfig.Endpoints.*` - All API endpoints
- Environment-specific URLs (local, ngrok, production)

### Files Using API Configuration

1. **APIHealthChecker.swift** - Health check endpoint
2. **ContentViewModel.swift** - Content loading
3. **FavoritesManager.swift** - Favorites management
4. **AuthViewModel.swift** - Authentication
5. **EpisodesView.swift** - Episode loading and video URLs

## 🔍 Diagnostic Steps

### Step 1: Check API Server Status

```bash
# Check if API server is running
ps aux | grep "python.*main.py"

# Check if port 8000 is in use
lsof -i :8000

# Test API directly
curl -v http://localhost:8000/health
```

### Step 2: Check iOS App Configuration

```bash
# Show current API configuration
./scripts/switch_api_environment.sh current

# Check if configuration file exists
ls -la PecanTV/PECANTV/PECANTV/Core/Config/APIConfig.swift
```

### Step 3: Verify Network Connectivity

```bash
# Test localhost connectivity
ping localhost

# Test specific port
telnet localhost 8000

# Check firewall settings (macOS)
sudo pfctl -s rules
```

## 🛠️ Advanced Troubleshooting

### Database Connection Issues

If the API server starts but can't connect to the database:

```bash
# Check database configuration
cat api/database.py

# Test database connection
cd api
python3 -c "
from database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful')
"
```

### Environment Variables

The API server uses environment variables. Check if `.env` file exists:

```bash
# Check for .env file
ls -la api/.env

# If missing, create one with database URL
echo "DATABASE_URL=postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require" > api/.env
```

### iOS Simulator Network Issues

Sometimes the iOS Simulator has network connectivity issues:

1. **Reset Simulator:**
   - iOS Simulator → Device → Erase All Content and Settings

2. **Check Simulator Network:**
   - iOS Simulator → Device → Network → Network Link Conditioner

3. **Use Device IP Instead of localhost:**
   ```bash
   # Get your machine's IP address
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Update API config to use IP instead of localhost
   ./scripts/switch_api_environment.sh local
   # Then manually edit APIConfig.swift to use your IP
   ```

## 🔄 Environment Switching Guide

### Local Development
```bash
# Start local API server
./quick_start.sh run

# Configure app for local development
./scripts/switch_api_environment.sh local

# Build and run iOS app
# The app will connect to http://localhost:8000
```

### Ngrok Tunnel (External Access)
```bash
# Start local API server
./quick_start.sh run

# Start ngrok tunnel (in separate terminal)
ngrok http 8000

# Copy ngrok URL and update script
# Edit scripts/switch_api_environment.sh with new ngrok URL

# Switch to ngrok environment
./scripts/switch_api_environment.sh ngrok

# Build and run iOS app
# The app will connect to ngrok URL
```

### Production Deployment
```bash
# Deploy API to production (Render, Railway, etc.)
# Get production URL

# Switch to production environment
./scripts/switch_api_environment.sh production

# Build and run iOS app
# The app will connect to production URL
```

## 📱 iOS App Debugging

### Enable Network Logging

Add this to your iOS app for debugging:

```swift
// In your network requests, add logging
print("🌐 Making request to: \(url)")
print("📤 Request data: \(requestData)")
print("📥 Response: \(response)")
```

### Check Console Logs

1. Open Xcode
2. Window → Devices and Simulators
3. Select your device/simulator
4. View Console logs for network errors

### Common iOS Network Errors

- **NSURLErrorCannotConnectToHost** - API server not running
- **NSURLErrorTimedOut** - Network timeout
- **NSURLErrorNotConnectedToInternet** - No internet connection
- **NSURLErrorCannotFindHost** - Wrong API URL

## 🚀 Quick Start Checklist

Before building the iOS app, ensure:

- [ ] API server is running (`./quick_start.sh run`)
- [ ] API responds to health check (`curl http://localhost:8000/health`)
- [ ] App is configured for correct environment (`./scripts/switch_api_environment.sh current`)
- [ ] Database connection is working
- [ ] No firewall blocking port 8000

## 📞 Getting Help

If you're still experiencing issues:

1. **Check the logs:**
   ```bash
   # API server logs
   tail -f api/debug_log.txt
   
   # iOS console logs (in Xcode)
   ```

2. **Verify all components:**
   ```bash
   # Run comprehensive test
   ./quick_start.sh test
   ```

3. **Reset to known good state:**
   ```bash
   # Restore API config from backup
   ./scripts/switch_api_environment.sh restore
   
   # Restart API server
   pkill -f "python.*main.py"
   ./quick_start.sh run
   ```

## 🔗 Useful Commands Reference

```bash
# Start API server
./quick_start.sh run

# Test API endpoints
./quick_start.sh test

# Switch API environment
./scripts/switch_api_environment.sh [local|ngrok|production|current]

# Check API status
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check running processes
ps aux | grep python

# Kill API server
pkill -f "python.*main.py"
``` 