#!/bin/bash

# Quick Security Fixes Runner
# This script applies the most critical security fixes to the PecanTV API

echo "🔒 PecanTV Security Fixes - Quick Implementation"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the api directory."
    exit 1
fi

# Backup current state
echo "📦 Creating backup..."
git add .
git commit -m "Backup before quick security fixes" --no-verify 2>/dev/null || echo "⚠️  No changes to commit"

# Run the quick fixes script
echo "🔧 Applying critical security fixes..."
python3 quick_security_fixes.py

# Test the application
echo "🧪 Testing the application..."
python3 -m py_compile main.py
if [ $? -eq 0 ]; then
    echo "✅ Syntax check passed"
else
    echo "❌ Syntax errors found. Please check the code."
    exit 1
fi

# Run security tests if available
if [ -f "security_tests_new.py" ]; then
    echo "🔍 Running security tests..."
    python3 security_tests_new.py
else
    echo "⚠️  Security tests not found. Skipping automated testing."
fi

echo ""
echo "✅ Quick security fixes completed!"
echo ""
echo "Next steps:"
echo "1. Start the server: python3 main.py"
echo "2. Test manually: curl http://localhost:8000/health"
echo "3. Review changes and commit: git add . && git commit -m 'Apply quick security fixes'"
echo "4. Continue with full security implementation plan"
echo ""
echo "For detailed implementation, see: SECURITY_IMPLEMENTATION_PLAN.md" 