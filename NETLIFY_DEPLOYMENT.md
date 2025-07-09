# Netlify Deployment Guide for PecanTV API

This guide explains how to deploy your FastAPI application to Netlify with access to your Neon database.

## Prerequisites

1. A Netlify account
2. Your Neon database credentials
3. Git repository with your code

## Step 1: Environment Variables Setup

In your Netlify dashboard, go to **Site settings** > **Environment variables** and add the following:

### Required Environment Variables

```
DATABASE_URL=postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
```

### Optional Environment Variables (if using Stripe)

```
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
ENVIRONMENT=production
DEBUG=false
```

## Step 2: Deploy to Netlify

### Option A: Deploy via Netlify UI

1. Go to [Netlify](https://netlify.com) and click "New site from Git"
2. Connect your GitHub/GitLab/Bitbucket repository
3. Configure the build settings:
   - **Build command**: `cd api && pip install -r requirements.txt`
   - **Publish directory**: `api`
   - **Functions directory**: `api/functions`
4. Click "Deploy site"

### Option B: Deploy via Netlify CLI

1. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Login to Netlify:
   ```bash
   netlify login
   ```

3. Initialize and deploy:
   ```bash
   netlify init
   netlify deploy --prod
   ```

## Step 3: Verify Deployment

After deployment, your API will be available at:
- `https://your-site-name.netlify.app/.netlify/functions/main/`

Test the endpoints:
- Health check: `https://your-site-name.netlify.app/.netlify/functions/main/health`
- Content: `https://your-site-name.netlify.app/.netlify/functions/main/content`
- Series: `https://your-site-name.netlify.app/.netlify/functions/main/series`

## Step 4: Update iOS App Configuration

Update your iOS app's base URL to point to your Netlify deployment:

```swift
// In your iOS app configuration
let baseURL = "https://your-site-name.netlify.app/.netlify/functions/main"
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify the `DATABASE_URL` environment variable is set correctly
   - Check that your Neon database allows connections from Netlify's IP ranges
   - Ensure SSL mode is set to `require`

2. **Function Timeout**
   - Netlify functions have a 10-second timeout limit
   - Optimize database queries and reduce response time
   - Consider using connection pooling (already configured)

3. **Build Failures**
   - Check that all dependencies are in `api/requirements.txt`
   - Verify Python version compatibility (3.11)
   - Check build logs in Netlify dashboard

### Database Connection Pooling

The application is configured with connection pooling to handle multiple concurrent requests:

```python
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "connect_timeout": 10,
        "application_name": "pecantv_api"
    }
)
```

### Security Considerations

1. **Environment Variables**: Never commit sensitive credentials to your repository
2. **CORS**: The API is configured to allow all origins (`*`) - consider restricting this in production
3. **Database Access**: Ensure your Neon database has proper security settings

## Monitoring

- Use Netlify's built-in analytics to monitor function performance
- Check function logs in the Netlify dashboard
- Monitor database connection usage in Neon dashboard

## Cost Considerations

- Netlify Functions: 125,000 invocations per month on free tier
- Neon Database: Check your current plan limits
- Consider upgrading if you exceed free tier limits 