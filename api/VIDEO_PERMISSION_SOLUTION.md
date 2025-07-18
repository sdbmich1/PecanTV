# Video Permission Error Solution Guide

## Problem
All video URLs point to Google Cloud Storage (GCS) URLs that are not publicly accessible:
- Films: https://storage.googleapis.com/pecantv_features/...
- Episodes: https://storage.googleapis.com/pecantv_series/...

These URLs return 403 Forbidden, causing "permission denied" errors in the app.

## Solutions

### Option 1: Make GCS Bucket Public (Recommended)
1. Go to Google Cloud Console
2. Navigate to Cloud Storage > Buckets
3. Select your bucket (pecantv_features, pecantv_series)
4. Go to Permissions tab
5. Add public read access:
   - Role: Storage Object Viewer
   - Members: allUsers

### Option 2: Use Signed URLs
1. Generate signed URLs with expiration
2. Update database with signed URLs
3. Implement URL refresh mechanism

### Option 3: Different CDN
1. Upload videos to Cloudflare, AWS CloudFront, or similar
2. Update database URLs
3. Ensure public access

### Option 4: Local Development
1. Download videos to local server
2. Serve via FastAPI static files
3. Update URLs to localhost:8000/...

## Immediate Fix
For testing, you can:
1. Use sample videos from public sources
2. Create placeholder videos
3. Implement proper error handling in iOS app

## iOS App Improvements
- Better error messages for permission issues
- Fallback to external browser
- Retry mechanism with different URLs
