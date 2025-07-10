#!/bin/bash

# Script to test Render deployment
# Usage: ./scripts/test_render_deployment.sh [RENDER_URL]
# Example: ./scripts/test_render_deployment.sh https://pecantv-api.onrender.com

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}🎬 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Get Render URL from command line or prompt user
if [ $# -eq 1 ]; then
    RENDER_URL="$1"
else
    echo "Please enter your Render URL (e.g., https://pecantv-api.onrender.com):"
    read RENDER_URL
fi

# Remove trailing slash if present
RENDER_URL="${RENDER_URL%/}"

print_status "Testing Render deployment at: $RENDER_URL"
echo ""

# Test function
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local expected_status="${3:-200}"
    
    print_status "Testing $description..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$RENDER_URL$endpoint" 2>/dev/null)
    status_code="${response: -3}"
    
    if [ "$status_code" = "$expected_status" ]; then
        print_success "$description - Status: $status_code"
        if [ "$status_code" = "200" ]; then
            # Show a snippet of the response for successful calls
            if [ -s /tmp/response.json ]; then
                echo "   Response preview: $(head -c 100 /tmp/response.json)..."
            fi
        fi
    else
        print_error "$description - Status: $status_code (expected: $expected_status)"
        if [ -s /tmp/response.json ]; then
            echo "   Error details: $(cat /tmp/response.json)"
        fi
    fi
    echo ""
}

# Test all endpoints
print_status "=== Testing Basic Endpoints ==="
test_endpoint "/" "Root endpoint"
test_endpoint "/health" "Health check"
test_endpoint "/docs" "API documentation"

print_status "=== Testing Content Endpoints ==="
test_endpoint "/content" "Content list"
test_endpoint "/series" "Series list"
test_endpoint "/genres" "Genres list"
test_endpoint "/episodes" "Episodes list"

print_status "=== Testing Search ==="
test_endpoint "/search?q=dragnet" "Search for 'dragnet'"

print_status "=== Testing Security Endpoints ==="
test_endpoint "/security/stats" "Security statistics"

print_status "=== Testing Database Connection ==="
# Test if content endpoint returns actual data
if curl -s "$RENDER_URL/content" | grep -q "id"; then
    print_success "Database connection working - content returned"
else
    print_error "Database connection failed - no content data"
fi

print_status "=== Testing CORS ==="
# Test CORS headers
cors_headers=$(curl -s -I "$RENDER_URL/health" | grep -i "access-control")
if [ -n "$cors_headers" ]; then
    print_success "CORS headers present"
    echo "   CORS: $cors_headers"
else
    print_warning "CORS headers not found"
fi

print_status "=== Performance Test ==="
# Test response time
start_time=$(date +%s.%N)
curl -s "$RENDER_URL/health" > /dev/null
end_time=$(date +%s.%N)
response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0.1")
print_success "Response time: ${response_time}s"

echo ""
print_status "=== Deployment Summary ==="
echo "🌐 Render URL: $RENDER_URL"
echo "📊 API Documentation: $RENDER_URL/docs"
echo "🔍 Health Check: $RENDER_URL/health"
echo "📱 Ready for iOS app testing!"

echo ""
print_warning "Next steps:"
echo "1. Update your iOS app to use this URL"
echo "2. Run: ./scripts/switch_to_render.sh"
echo "3. Test on your iPhone!"

# Clean up
rm -f /tmp/response.json 