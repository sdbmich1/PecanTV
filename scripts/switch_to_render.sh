#!/bin/bash

# Script to switch PecanTV iOS app to use Render deployment
# Usage: ./scripts/switch_to_render.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}🎬 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# API config file
API_CONFIG_FILE="PecanTV/PECANTV/PECANTV/Core/Config/APIConfig.swift"

print_status "Switching PecanTV iOS app to use Render deployment"

# Check if API config file exists
if [ ! -f "$API_CONFIG_FILE" ]; then
    echo "❌ Error: API config file not found at $API_CONFIG_FILE"
    exit 1
fi

# Render deployment URL
RENDER_URL="https://pecantv-api.onrender.com"

print_status "Updating API configuration to use Render deployment: $RENDER_URL"

# Backup the original file
cp "$API_CONFIG_FILE" "${API_CONFIG_FILE}.backup"
print_success "Created backup: ${API_CONFIG_FILE}.backup"

# Update the baseURL to use Render
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|static let baseURL = \"http://localhost:8000\"|static let baseURL = \"$RENDER_URL\"|g" "$API_CONFIG_FILE"
else
    # Linux
    sed -i "s|static let baseURL = \"http://localhost:8000\"|static let baseURL = \"$RENDER_URL\"|g" "$API_CONFIG_FILE"
fi

print_success "Updated baseURL to use Render deployment"

# Test the API endpoint
print_status "Testing Render API endpoint..."
if curl -s "$RENDER_URL/health" > /dev/null; then
    print_success "Render API is responding correctly!"
else
    print_warning "Render API might not be ready yet. Please check your deployment status."
fi

echo ""
print_status "Next steps:"
echo "1. Open your iOS project in Xcode"
echo "2. Build and run the app"
echo "3. The app will now connect to: $RENDER_URL"
echo ""
print_warning "To switch back to local development:"
echo "   ./scripts/switch_api_environment.sh local"
echo ""
print_success "Render deployment configuration complete!" 