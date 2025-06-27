# PecanTV API Deployment Guide

This guide will help you deploy your FastAPI backend to various cloud platforms so your iOS app can connect to it from anywhere.

## 🚀 **Quick Deploy Options**

### **Option 1: Render (Recommended - Free)**
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `pecantv-api`
   - **Root Directory**: `api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `DATABASE_URL`: `postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require`
   - `SECRET_KEY`: (auto-generated)
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
6. Click "Create Web Service"

### **Option 2: Railway**
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set the root directory to `api`
5. Add the same environment variables as above
6. Deploy!

### **Option 3: Vercel**
1. Go to [vercel.com](https://vercel.com) and sign up
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: `api`
   - **Install Command**: `pip install -r requirements.txt`
4. Add environment variables
5. Deploy!

## 🔧 **Pre-Deployment Checklist**

### **1. Update API Configuration**
Make sure your `api/main.py` uses environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
```

### **2. Test Locally**
```bash
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### **3. Verify Database Connection**
Your Neon database should be accessible from cloud platforms.

## 📱 **Update iOS App**

Once deployed, update your iOS app to use the new API URL:

```swift
// Replace all instances of localhost with your deployed URL
private let baseURL = "https://your-app-name.onrender.com"
```

## 🔍 **Post-Deployment Testing**

1. **Health Check**: `https://your-app-name.onrender.com/health`
2. **Content API**: `https://your-app-name.onrender.com/content`
3. **Authentication**: `https://your-app-name.onrender.com/auth/login`

## 🛠 **Troubleshooting**

### **Common Issues:**
- **Port Issues**: Make sure to use `$PORT` environment variable
- **Database Connection**: Verify Neon database is accessible
- **Dependencies**: Check `requirements.txt` is complete
- **CORS**: Add CORS middleware if needed

### **Debug Commands:**
```bash
# Check logs
curl https://your-app-name.onrender.com/health

# Test database connection
curl https://your-app-name.onrender.com/content
```

## 📊 **Monitoring**

- **Render**: Built-in logging and monitoring
- **Railway**: Real-time logs and metrics
- **Vercel**: Analytics and performance monitoring

## 🔒 **Security Notes**

- Never commit secrets to Git
- Use environment variables for sensitive data
- Enable HTTPS (automatic on most platforms)
- Consider rate limiting for production 