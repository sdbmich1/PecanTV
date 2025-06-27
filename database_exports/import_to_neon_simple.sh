#!/bin/bash
# Simple Neon Import Script
# Generated on 2025-06-22 19:24:35

echo "🔄 Importing data to Neon database from SQL file..."

echo ""
echo "📝 SETUP INSTRUCTIONS FOR NEW NEON USERS:"
echo "1. Go to https://console.neon.tech/"
echo "2. Sign up with your email and create a password"
echo "3. Create a new project (e.g., 'PecanTV')"
echo "4. Go to Settings > Users and create a database user with a password"
echo "5. Go to Connection Details and copy the connection string"
echo ""

# Replace this with your actual Neon connection string
# Format: postgresql://username:password@host:port/database?sslmode=require
# Example: postgresql://pecantv_user:mypassword123@ep-cool-name-123456.us-east-2.aws.neon.tech:5432/neondb?sslmode=require
NEON_CONNECTION_STRING="postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

echo "🔧 Current connection string:"
echo "$NEON_CONNECTION_STRING"
echo ""

# Check if connection string has been updated
if [[ "$NEON_CONNECTION_STRING" == *"YOUR_USERNAME"* ]]; then
    echo "❌ Please update the connection string above with your actual Neon credentials"
    echo ""
    echo "📋 How to find your connection string:"
    echo "1. In your Neon project, go to 'Connection Details'"
    echo "2. Look for 'Connection string' section"
    echo "3. Copy the entire string (it includes username, password, host, etc.)"
    echo ""
    echo "🔧 Edit this script and replace the line:"
    echo "NEON_CONNECTION_STRING=\"postgresql://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST:5432/YOUR_DATABASE?sslmode=require\""
    echo ""
    echo "With your actual connection string, then run this script again."
    exit 1
fi

echo "🔄 Testing connection to Neon..."
psql "$NEON_CONNECTION_STRING" -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Connection to Neon successful! Importing data from SQL file..."
    
    # Import the data from our exported SQL file
    psql "$NEON_CONNECTION_STRING" < database_exports/pecantv_full_20250622_192434.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Import completed successfully!"
        echo ""
        echo "🎉 Your PecanTV database has been migrated to Neon!"
        echo "You can now update your app's DATABASE_URL to use Neon."
        echo ""
        echo "📋 Next steps:"
        echo "1. Update your app's database configuration to use Neon"
        echo "2. Test your app with the new database"
        echo "3. Consider removing the Docker database if no longer needed"
    else
        echo "❌ Import failed. Please check the error messages above."
    fi
else
    echo "❌ Connection to Neon failed. Please check your credentials and try again."
    echo ""
    echo "Common issues:"
    echo "1. Make sure you've created a database user with a password"
    echo "2. Verify the connection string format"
    echo "3. Check that your IP is allowed in Neon's settings"
    echo ""
    echo "You can test the connection manually:"
    echo "psql \"$NEON_CONNECTION_STRING\""
fi 