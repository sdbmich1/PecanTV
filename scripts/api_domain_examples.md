# PecanTV API Domain Examples & Instructions

## What is `your-api-domain.com`?

In the README documentation, `your-api-domain.com` is a placeholder that represents the actual domain where your PecanTV API is hosted. Here are real examples and instructions for finding your actual API domain.

## 🌐 Real Examples of API Domains

### 1. Local Development (ngrok)
```bash
PECANTV_API_URL=https://77b9-192-69-240-171.ngrok-free.app
```
*This is the ngrok URL from your current setup*

### 2. Production Deployment Examples

**Render (Recommended):**
```bash
PECANTV_API_URL=https://pecantv-api.onrender.com
```

**Railway:**
```bash
PECANTV_API_URL=https://pecantv-api.railway.app
```

**Vercel:**
```bash
PECANTV_API_URL=https://pecantv-api.vercel.app
```

**Heroku:**
```bash
PECANTV_API_URL=https://pecantv-api.herokuapp.com
```

**Custom Domain:**
```bash
PECANTV_API_URL=https://api.pecantv.com
```

### 3. Local Network Access
```bash
PECANTV_API_URL=http://192.168.1.100:8000
```
*Your local machine's IP address*

### 4. Current Setup (Based on your logs)
From your terminal output, you're using ngrok:
```bash
PECANTV_API_URL=https://77b9-192-69-240-171.ngrok-free.app
```

## 🔍 How to Find Your Actual API Domain

### If using ngrok:
1. Look at the "Forwarding" line in your ngrok terminal
2. Copy the HTTPS URL (e.g., `https://77b9-192-69-240-171.ngrok-free.app`)
3. Use this as your `PECANTV_API_URL`

### If deployed to a hosting service:
1. Check your hosting provider's dashboard
2. Look for the deployment URL or domain
3. Copy the base URL (without any path)

### If running locally:
1. Use your machine's IP address: `http://YOUR_IP:8000`
2. Or use localhost: `http://localhost:8000` (for same machine access)

## 📝 Environment Variable Setup

### For Netlify Functions:
```bash
# In Netlify Dashboard > Site settings > Environment variables
PECANTV_API_URL=https://77b9-192-69-240-171.ngrok-free.app
API_TOKEN=your_api_token_here
WEBHOOK_SECRET=your_webhook_secret_here
```

### For Local Development:
```bash
# In your .env file
PECANTV_API_URL=https://77b9-192-69-240-171.ngrok-free.app
DATABASE_URL=postgresql://neondb_owner:password@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
```

### For Production:
```bash
# Replace with your actual production domain
PECANTV_API_URL=https://pecantv-api.onrender.com
```

## 🧪 Testing Your API Domain

### Test API Health:
```bash
curl -X GET "https://77b9-192-69-240-171.ngrok-free.app/health"
```

### Test Content Endpoint:
```bash
curl -X GET "https://77b9-192-69-240-171.ngrok-free.app/content"
```

### Test Series Endpoint:
```bash
curl -X GET "https://77b9-192-69-240-171.ngrok-free.app/series"
```

## 🔧 Common Issues & Solutions

### Issue: "Address already in use"
**Solution:** Kill existing processes and restart
```bash
pkill -f "python main.py"
cd api && python main.py
```

### Issue: ngrok URL changes
**Solution:** Update your environment variables with the new URL
```bash
# Check ngrok terminal for new URL
# Update PECANTV_API_URL in your .env file
```

### Issue: CORS errors
**Solution:** Ensure your API allows your frontend domain
```python
# In your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 iOS App Configuration

### Update API Base URL in Xcode:
1. Open your iOS project in Xcode
2. Find the API configuration file
3. Update the base URL to your actual domain:
   ```swift
   let baseURL = "https://77b9-192-69-240-171.ngrok-free.app"
   ```

## 🚀 Deployment Checklist

- [ ] API is running and accessible
- [ ] Environment variables are set correctly
- [ ] CORS is configured for your frontend
- [ ] Database connection is working
- [ ] All endpoints are responding correctly
- [ ] iOS app is pointing to the correct API URL

## 📞 Support

If you need help finding your API domain:
1. Check your terminal for ngrok output
2. Check your hosting provider's dashboard
3. Test the URL with curl or a web browser
4. Verify the API is running and accessible

---

**Current Working URL:** `https://77b9-192-69-240-171.ngrok-free.app`
**Last Updated:** Based on your current ngrok session 