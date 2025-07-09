# 🚀 Cloudflare Images Setup for PecanTV

## Quick Setup (5 minutes)

### 1. Create Cloudflare Account
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up for free account
3. Add your domain (or use a subdomain)

### 2. Enable Cloudflare Images
1. In Cloudflare dashboard, go to **Images**
2. Click **Get started with Cloudflare Images**
3. Choose **Free** plan (100k images/month)

### 3. Configure Image Resizing
1. Go to **Speed > Optimization**
2. Enable **Image Resizing** and **Polish**
3. Set Polish to **Lossy** for best compression

### 4. Set up DNS
1. Go to **DNS** in dashboard
2. Add A record:
   - Name: `images`
   - IPv4: `192.0.2.1` (placeholder)
   - Proxy: ✅ Proxied (orange cloud)

### 5. Update iOS App
The ImageOptimizationService is already configured to use:
- Base URL: `https://images.pecantv.com`
- Automatic WebP conversion
- Responsive sizing
- Quality optimization

## Cost Breakdown
- **Free tier**: 100,000 images/month
- **Paid tier**: $5/month for 1M images
- **Perfect for**: 1000s of devices

## Performance Benefits
- **Global delivery**: 200+ locations
- **30-70% smaller files**: WebP optimization
- **Faster loading**: CDN edge caching
- **Automatic resizing**: Responsive images
- **Format conversion**: WebP/AVIF support

## Implementation Status
✅ iOS app ready (ImageOptimizationService.swift)
✅ Backend ready (FastAPI static serving)
✅ Database optimized (proper poster URLs)
🔄 CDN setup needed (run this guide)

## Next Steps
1. Set up Cloudflare account
2. Configure DNS
3. Test with sample images
4. Monitor performance
