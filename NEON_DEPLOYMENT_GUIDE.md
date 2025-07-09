# Neon Database Deployment Guide

## 🚨 Current Issue

Your PecanTV app is currently using hardcoded Neon database credentials in the code, which is **not secure for production**. We need to move these to environment variables for live app testing.

## ✅ What We've Fixed

1. **Removed hardcoded credentials** from `api/database.py`
2. **Added proper Neon connection handling** with pooled connections
3. **Created environment configuration** system
4. **Added connection testing** functionality

## 🔧 Quick Setup

### Step 1: Run the Setup Script

```bash
./scripts/setup_neon_database.sh
```

This script will:
- Create a `.env` file in the `api/` directory
- Help you configure your Neon database URL
- Test the database connection
- Set up proper environment variables

### Step 2: Verify Your Neon Database

1. **Go to Neon Console:** https://console.neon.tech
2. **Select your project:** `pecantv` (or your project name)
3. **Get connection details:**
   - Click on "Connection Details"
   - Copy the **Pooled connection** URL
   - It should look like: `postgresql://username:password@ep-example-123456-pooler.us-west-2.aws.neon.tech/database_name?sslmode=require`

### Step 3: Update Environment Variables

Edit `api/.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://your_actual_neon_url_here

# Other configurations...
STRIPE_SECRET_KEY=your_stripe_key
JWT_SECRET=your_jwt_secret
```

## 🏗️ Deployment Platforms

### Render (Recommended)

1. **Create a new Web Service**
2. **Connect your GitHub repository**
3. **Set environment variables:**
   ```
   DATABASE_URL=your_neon_pooled_connection_url
   STRIPE_SECRET_KEY=your_stripe_secret_key
   JWT_SECRET=your_jwt_secret
   ```
4. **Build command:** `pip install -r api/requirements.txt`
5. **Start command:** `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Railway

1. **Deploy from GitHub**
2. **Add environment variables** in Railway dashboard
3. **Set the same variables** as above

### Heroku

1. **Create Heroku app**
2. **Add PostgreSQL addon** (or use Neon)
3. **Set config vars:**
   ```bash
   heroku config:set DATABASE_URL=your_neon_url
   heroku config:set STRIPE_SECRET_KEY=your_stripe_key
   heroku config:set JWT_SECRET=your_jwt_secret
   ```

### Vercel

1. **Deploy as serverless function**
2. **Set environment variables** in Vercel dashboard
3. **Note:** May need to adjust for serverless limitations

## 🔍 Testing Your Setup

### Local Testing

```bash
# Test database connection
cd api
python3 -c "from database import test_database_connection; test_database_connection()"

# Start API server
./quick_start.sh run

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/content
```

### Production Testing

```bash
# Test your deployed API
curl https://your-api-domain.com/health
curl https://your-api-domain.com/content
```

## 🛡️ Security Best Practices

### Environment Variables

✅ **Do:**
- Use environment variables for all secrets
- Use different databases for dev/staging/prod
- Rotate credentials regularly
- Use Neon's pooled connections

❌ **Don't:**
- Commit `.env` files to version control
- Use hardcoded credentials in code
- Share database URLs publicly
- Use the same credentials everywhere

### Neon Database Security

1. **Use Pooled Connections:**
   ```
   postgresql://user:pass@ep-example-pooler.neon.tech/db
   ```

2. **Enable SSL:**
   ```
   ?sslmode=require
   ```

3. **Set Connection Limits:**
   - Pool size: 5-10 connections
   - Max overflow: 10-20 connections
   - Recycle time: 300 seconds

## 🔄 Environment Management

### Development Environment

```bash
# Local development
DATABASE_URL=postgresql://dev_user:dev_pass@ep-dev-pooler.neon.tech/dev_db
DEBUG=true
LOG_LEVEL=DEBUG
```

### Staging Environment

```bash
# Staging/testing
DATABASE_URL=postgresql://staging_user:staging_pass@ep-staging-pooler.neon.tech/staging_db
DEBUG=false
LOG_LEVEL=INFO
```

### Production Environment

```bash
# Production
DATABASE_URL=postgresql://prod_user:prod_pass@ep-prod-pooler.neon.tech/prod_db
DEBUG=false
LOG_LEVEL=WARNING
```

## 📊 Monitoring & Maintenance

### Database Monitoring

1. **Neon Dashboard:**
   - Monitor connection usage
   - Check query performance
   - Review logs

2. **API Health Checks:**
   ```bash
   curl https://your-api.com/health
   ```

3. **Database Connection Testing:**
   ```python
   from database import test_database_connection
   test_database_connection()
   ```

### Backup Strategy

1. **Neon Automatic Backups:**
   - Neon provides automatic backups
   - Configure backup retention

2. **Manual Backups:**
   ```bash
   # Export data
   pg_dump $DATABASE_URL > backup.sql
   
   # Import data
   psql $DATABASE_URL < backup.sql
   ```

## 🚀 Live App Testing Checklist

Before testing your live app:

- [ ] Database connection configured in `.env`
- [ ] API deployed and accessible
- [ ] Health endpoint responding
- [ ] Content endpoint returning data
- [ ] iOS app configured for production API
- [ ] Stripe keys configured (if using subscriptions)
- [ ] JWT secrets configured
- [ ] CORS settings updated for your domain
- [ ] SSL certificates valid
- [ ] Database performance acceptable

## 🔧 Troubleshooting

### Common Issues

1. **Connection Timeout:**
   ```bash
   # Check if Neon is accessible
   telnet ep-your-db-pooler.neon.tech 5432
   ```

2. **SSL Issues:**
   ```bash
   # Ensure sslmode=require in URL
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   ```

3. **Pool Exhaustion:**
   ```python
   # Reduce pool size
   pool_size=3
   max_overflow=5
   ```

4. **Authentication Errors:**
   - Check username/password in Neon console
   - Verify database name
   - Ensure user has proper permissions

### Debug Commands

```bash
# Test database connection
cd api && python3 -c "from database import test_database_connection; test_database_connection()"

# Check environment variables
echo $DATABASE_URL

# Test API endpoints
curl -v https://your-api.com/health

# Check logs
tail -f api/debug_log.txt
```

## 📞 Support

If you encounter issues:

1. **Check Neon Status:** https://status.neon.tech
2. **Review Neon Documentation:** https://neon.tech/docs
3. **Check API logs** in your deployment platform
4. **Test database connection** using the provided scripts

## 🎯 Next Steps

1. **Run the setup script:** `./scripts/setup_neon_database.sh`
2. **Deploy your API** to your chosen platform
3. **Update iOS app** to use production API URL
4. **Test thoroughly** before going live
5. **Monitor performance** and adjust as needed

Your Neon database connection is now properly configured for secure, production-ready live app testing! 