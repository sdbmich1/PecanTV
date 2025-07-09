#!/bin/bash

# PecanTV Test Runner Script
# This script runs all tests and provides a summary

echo "🎬 PecanTV Test Runner"
echo "========================"

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode command line tools not found. Please install Xcode."
    exit 1
fi

# Check if API is running
echo "🔍 Checking API status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running on localhost:8000"
else
    echo "⚠️  API is not running. Some tests may fail."
fi

# Set project path
PROJECT_PATH="PECANTV.xcodeproj"
SCHEME="PECANTV"
DESTINATION="platform=iOS Simulator,name=iPhone 16"

echo ""
echo "🧪 Running Unit Tests..."
echo "------------------------"

# Run unit tests
UNIT_TEST_RESULT=$(xcodebuild test \
    -project "$PROJECT_PATH" \
    -scheme "$SCHEME" \
    -destination "$DESTINATION" \
    -only-testing:PECANTVTests \
    -quiet 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Unit tests passed"
    UNIT_TESTS_PASSED=true
else
    echo "❌ Unit tests failed"
    echo "$UNIT_TEST_RESULT"
    UNIT_TESTS_PASSED=false
fi

echo ""
echo "🎯 Running UI Tests..."
echo "----------------------"

# Run UI tests
UI_TEST_RESULT=$(xcodebuild test \
    -project "$PROJECT_PATH" \
    -scheme "$SCHEME" \
    -destination "$DESTINATION" \
    -only-testing:PECANTVUITests \
    -quiet 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ UI tests passed"
    UI_TESTS_PASSED=true
else
    echo "❌ UI tests failed"
    echo "$UI_TEST_RESULT"
    UI_TESTS_PASSED=false
fi

echo ""
echo "📊 Test Summary"
echo "==============="

if [ "$UNIT_TESTS_PASSED" = true ] && [ "$UI_TESTS_PASSED" = true ]; then
    echo "🎉 All tests passed!"
    echo "✅ Unit Tests: PASSED"
    echo "✅ UI Tests: PASSED"
    exit 0
else
    echo "💥 Some tests failed!"
    if [ "$UNIT_TESTS_PASSED" = false ]; then
        echo "❌ Unit Tests: FAILED"
    else
        echo "✅ Unit Tests: PASSED"
    fi
    
    if [ "$UI_TESTS_PASSED" = false ]; then
        echo "❌ UI Tests: FAILED"
    else
        echo "✅ UI Tests: PASSED"
    fi
    exit 1
fi 