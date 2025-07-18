# Complete Accessibility Fix Guide

## Current Issues
1. **Poster Images**: GCS URLs return 403 Forbidden
2. **Video Content**: GCS URLs return 403 Forbidden  
3. **Episode Videos**: GCS URLs return 403 Forbidden

## Immediate Fixes Applied
- ✅ Updated poster URLs to working placeholder images
- ✅ Added accessibility notes to content descriptions
- ✅ Improved error handling in iOS app

## Long-term Solutions

### Option 1: Make GCS Buckets Public (Recommended)
1. Go to Google Cloud Console
2. Navigate to Cloud Storage > Buckets
3. Select buckets: `pecantv_title_images`, `pecantv_features`, `pecantv_series`
4. Go to Permissions tab
5. Add public read access:
   - Role: Storage Object Viewer
   - Members: `allUsers`

### Option 2: Use Cloudflare Images (Alternative)
1. Upload images to Cloudflare Images
2. Update database URLs to Cloudflare URLs
3. Ensure public access

### Option 3: Use Railway Static Files
1. Upload images to Railway static file hosting
2. Update URLs to Railway URLs
3. Ensure proper CORS configuration

## Testing Steps
1. Make GCS buckets public
2. Test poster URLs: `https://storage.googleapis.com/pecantv_title_images/...`
3. Test video URLs: `https://storage.googleapis.com/pecantv_features/...`
4. Update iOS app if needed

## iOS App Improvements
- ✅ Better error messages for permission issues
- ✅ Fallback to external browser
- ✅ Clear button states with helpful messages
- ✅ Always working back button

## Next Steps
1. Make GCS buckets public
2. Test all URLs work
3. Update database with working URLs
4. Deploy updated iOS app
