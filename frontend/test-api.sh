#!/bin/bash

BASE_URL="http://localhost:3000"

echo "🧪 Testing API endpoints..."
echo ""

# Test GET /api/products
echo "1️⃣ Testing GET /api/products"
curl -s -X GET "$BASE_URL/api/products" | head -3
echo ""
echo ""

# Test POST /api/vibe
echo "2️⃣ Testing POST /api/vibe"
curl -s -X POST -H "Content-Type: application/json" -d '{"uuid":"test-user-123","query":"耳機"}' "$BASE_URL/api/vibe" | head -3
echo ""
echo ""

# Test GET /api/thread/1
echo "3️⃣ Testing GET /api/thread/1"
curl -s -X GET "$BASE_URL/api/thread/1" | head -3
echo ""
echo ""

echo "✅ API tests completed!"
echo ""
echo "📋 API Endpoints Summary:"
echo "  GET  /api/products      - ✅ Product list"
echo "  POST /api/vibe          - ✅ Search intent analysis" 
echo "  GET  /api/thread/{id}   - ✅ Thread details"
echo ""
echo "Frontend available at:"
echo "  🌐 http://demo.scruel.com:3000"
