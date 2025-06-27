#!/bin/bash

# Update iOS App API URL Script
# This script helps you update your iOS app to use the deployed API URL

echo "📱 PecanTV iOS App URL Updater"
echo "================================"

if [ $# -eq 0 ]; then
    echo "❌ Error: Please provide your deployed API URL"
    echo "Usage: ./update_ios_url.sh https://your-app-name.onrender.com"
    echo ""
    echo "Example:"
    echo "  ./update_ios_url.sh https://pecantv-api.onrender.com"
    exit 1
fi

API_URL=$1

# Remove trailing slash if present
API_URL=${API_URL%/}

echo "🔧 Updating iOS app to use: $API_URL"
echo ""

# Files to update
FILES=(
    "PecanTV/PECANTV/PECANTV/Core/Services/APIHealthChecker.swift"
    "PecanTV/PECANTV/PECANTV/Features/Content/ViewModels/ContentViewModel.swift"
    "PecanTV/PECANTV/PECANTV/Features/Content/Models/FavoritesManager.swift"
    "PecanTV/PECANTV/PECANTV/Features/Authentication/ViewModels/AuthViewModel.swift"
)

# Backup directory
BACKUP_DIR="ios_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backup in: $BACKUP_DIR"

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "🔧 Updating: $file"
        
        # Create backup
        cp "$file" "$BACKUP_DIR/"
        
        # Update the URL
        if [[ "$file" == *"APIHealthChecker.swift" ]]; then
            # Update health check URL
            sed -i '' "s|http://[0-9.]*:[0-9]*/health|$API_URL/health|g" "$file"
        elif [[ "$file" == *"ContentViewModel.swift" ]]; then
            # Update content URL
            sed -i '' "s|http://[0-9.]*:[0-9]*/content|$API_URL/content|g" "$file"
        elif [[ "$file" == *"FavoritesManager.swift" ]]; then
            # Update base URL
            sed -i '' "s|http://[0-9.]*:[0-9]*|$API_URL|g" "$file"
        elif [[ "$file" == *"AuthViewModel.swift" ]]; then
            # Update base URL
            sed -i '' "s|http://[0-9.]*:[0-9]*|$API_URL|g" "$file"
        fi
        
        echo "✅ Updated: $file"
    else
        echo "⚠️  Warning: $file not found"
    fi
done

echo ""
echo "✅ URL update complete!"
echo ""
echo "🔍 Testing the new URL..."
if curl -s "$API_URL/health" > /dev/null; then
    echo "✅ API is responding at: $API_URL/health"
else
    echo "❌ Warning: API not responding at: $API_URL/health"
    echo "   Make sure your deployment is complete and running"
fi

echo ""
echo "📱 Next steps:"
echo "1. Build and test your iOS app"
echo "2. Verify it connects to the deployed API"
echo "3. Test all features (content loading, authentication, favorites)"
echo ""
echo "🔄 To revert changes:"
echo "   cp -r $BACKUP_DIR/* PecanTV/PECANTV/PECANTV/"
echo ""
echo "🌐 Your API endpoints:"
echo "   Health: $API_URL/health"
echo "   Content: $API_URL/content"
echo "   Auth: $API_URL/auth/login"
echo "   Register: $API_URL/auth/register" 