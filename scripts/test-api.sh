#!/bin/bash
# Simple API test script for ClipKit

set -e

API_URL="${API_URL:-http://localhost:8000}"

echo "🧪 Testing ClipKit API at $API_URL"
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$API_URL/health" | grep -q "healthy" && echo "✅ Health check passed" || echo "❌ Health check failed"
echo ""

# Test root endpoint
echo "2. Testing root endpoint..."
curl -s "$API_URL/" | grep -q "ClipKit" && echo "✅ Root endpoint passed" || echo "❌ Root endpoint failed"
echo ""

# Test jobs list (should be empty initially)
echo "3. Testing jobs list..."
curl -s "$API_URL/api/jobs" && echo "" && echo "✅ Jobs list accessible" || echo "❌ Jobs list failed"
echo ""

echo "✅ Basic API tests complete!"
echo ""
echo "📝 To test file upload:"
echo "   curl -X POST -F 'file=@your-video.mp4' $API_URL/api/upload"
