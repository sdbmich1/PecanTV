#!/bin/bash

# PecanTV API Deployment Script
# This script helps you deploy your FastAPI app to various platforms

echo "🚀 PecanTV API Deployment Helper"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: Please run this script from the root of your PecanTV project"
    exit 1
fi

echo "✅ Found API directory"

# Check if requirements.txt exists
if [ ! -f "api/requirements.txt" ]; then
    echo "❌ Error: api/requirements.txt not found"
    exit 1
fi

echo "✅ Found requirements.txt"

# Test local API
echo "🔍 Testing local API..."
cd api
python -c "from main import app; print('✅ API imports successfully')" || {
    echo "❌ Error: API failed to import"
    exit 1
}

echo ""
echo "🎯 Deployment Options:"
echo "1. Render (Recommended - Free)"
echo "2. Railway"
echo "3. Vercel"
echo "4. Manual deployment"
echo ""

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Deploying to Render..."
        echo ""
        echo "📋 Steps:"
        echo "1. Go to https://render.com and sign up"
        echo "2. Click 'New +' → 'Web Service'"
        echo "3. Connect your GitHub repository"
        echo "4. Configure:"
        echo "   - Name: pecantv-api"
        echo "   - Root Directory: api"
        echo "   - Environment: Python 3"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
        echo ""
        echo "5. Add Environment Variables:"
        echo "   - DATABASE_URL: postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"
        echo "   - SECRET_KEY: (auto-generated)"
        echo "   - ALGORITHM: HS256"
        echo "   - ACCESS_TOKEN_EXPIRE_MINUTES: 30"
        echo ""
        echo "6. Click 'Create Web Service'"
        echo ""
        echo "🌐 Your API will be available at: https://your-app-name.onrender.com"
        ;;
    2)
        echo ""
        echo "🚀 Deploying to Railway..."
        echo ""
        echo "📋 Steps:"
        echo "1. Go to https://railway.app and sign up"
        echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "3. Select your repository"
        echo "4. Set root directory to 'api'"
        echo "5. Add environment variables (same as Render)"
        echo "6. Deploy!"
        ;;
    3)
        echo ""
        echo "🚀 Deploying to Vercel..."
        echo ""
        echo "📋 Steps:"
        echo "1. Go to https://vercel.com and sign up"
        echo "2. Import your GitHub repository"
        echo "3. Configure:"
        echo "   - Framework Preset: Other"
        echo "   - Root Directory: api"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "4. Add environment variables"
        echo "5. Deploy!"
        ;;
    4)
        echo ""
        echo "📋 Manual Deployment Steps:"
        echo "1. Choose your preferred platform"
        echo "2. Follow the detailed guide in DEPLOYMENT.md"
        echo "3. Make sure to set environment variables"
        echo "4. Test your deployed API"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📱 After deployment, update your iOS app:"
echo "Replace all instances of 'localhost' with your deployed URL"
echo "Example: https://your-app-name.onrender.com"
echo ""
echo "🔍 Test your deployment:"
echo "curl https://your-app-name.onrender.com/health"
echo "curl https://your-app-name.onrender.com/content"
echo ""
echo "✅ Deployment guide complete!" 