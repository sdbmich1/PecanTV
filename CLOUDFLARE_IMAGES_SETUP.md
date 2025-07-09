# Cloudflare Images Setup for PecanTV

## Overview
This guide sets up Cloudflare Images and Image Resizing for optimal image performance in the PecanTV app.

## 1. Cloudflare Dashboard Setup

### Step 1: Enable Cloudflare Images
1. Log into your Cloudflare dashboard
2. Go to **Images** in the left sidebar
3. Click **Get started with Cloudflare Images**
4. Choose a plan (Free tier includes 100,000 images/month)

### Step 2: Configure Image Resizing
1. Go to **Speed > Optimization** in your Cloudflare dashboard
2. Scroll down to **Image Resizing**
3. Enable **Image Resizing** and **Polish**
4. Set Polish to **Lossless** or **Lossy** (recommended for photos)

### Step 3: Set up DNS for images.pecantv.com
1. Go to **DNS** in your Cloudflare dashboard
2. Add a new A record:
   - **Name**: `images`
   - **IPv4 address**: `192.0.2.1` (or your server IP)
   - **Proxy status**: Proxied (orange cloud)
3. Add a CNAME record for image resizing:
   - **Name**: `images-resize`
   - **Target**: `images.pecantv.com`
   - **Proxy status**: Proxied (orange cloud)

## 2. Backend Configuration

### Update API Configuration
Add Cloudflare settings to your environment:

```bash
# Add to api/.env
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
CLOUDFLARE_IMAGES_DOMAIN=images.pecantv.com
```

### Install Cloudflare SDK
```bash
cd api
pip install cloudflare
```

## 3. iOS App Updates

### Update ImageOptimizationService.swift
The service will now generate Cloudflare-optimized URLs:

```swift
// Example optimized URLs:
// Original: https://storage.googleapis.com/pecantv_series/movie/poster.jpg
// Optimized: https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85/https://storage.googleapis.com/pecantv_series/movie/poster.jpg
```

## 4. Testing and Verification

### Test Image Optimization
```bash
# Test original image
curl -I "https://storage.googleapis.com/pecantv_series/movie/poster.jpg"

# Test optimized image
curl -I "https://images.pecantv.com/cdn-cgi/image/format=webp,width=300,quality=85/https://storage.googleapis.com/pecantv_series/movie/poster.jpg"
```

## 5. Performance Benefits

### Expected Improvements:
- **File size reduction**: 30-70% smaller images
- **Faster loading**: CDN delivery from Cloudflare's global network
- **Automatic format conversion**: WebP for modern browsers, JPEG fallback
- **Responsive images**: Automatic resizing for different screen sizes

### Supported Parameters:
- `width`: Image width in pixels
- `height`: Image height in pixels
- `format`: webp, jpeg, png, gif
- `quality`: 1-100 (default: 85)
- `fit`: scale-down, contain, cover, crop, pad

## 6. Implementation Steps

1. **Set up Cloudflare Images** (steps above)
2. **Update backend code** (see below)
3. **Update iOS app** (see below)
4. **Test and monitor** performance improvements

## 7. Monitoring

### Cloudflare Analytics
- Monitor image requests in Cloudflare dashboard
- Track bandwidth savings
- Monitor cache hit rates

### App Performance
- Track image load times in iOS app
- Monitor memory usage improvements
- Track user experience metrics 