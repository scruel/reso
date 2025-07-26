#!/bin/bash

BACKEND_URL="http://demo.scruel.com:8000"
FRONTEND_URL="http://localhost:3000"

echo "🔗 Testing frontend-backend connectivity..."
echo ""

# Test backend health
echo "1️⃣ Testing backend health at $BACKEND_URL"
curl -s "$BACKEND_URL/" || echo "❌ Backend not accessible"
echo ""
echo ""

# Test backend API endpoints
echo "2️⃣ Testing backend API endpoints..."

echo "📦 GET $BACKEND_URL/api/products"
curl -s "$BACKEND_URL/api/products" | head -3 || echo "❌ Products endpoint not available"
echo ""

echo "🧠 POST $BACKEND_URL/api/vibe"
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"uuid":"test-user-123","query":"手機"}' \
  "$BACKEND_URL/api/vibe" | head -3 || echo "❌ Vibe endpoint not available"
echo ""

echo "🧵 GET $BACKEND_URL/api/thread?id=1"
curl -s "$BACKEND_URL/api/thread?id=1" | head -3 || echo "❌ Thread endpoint not available"
echo ""

echo ""
echo "3️⃣ Frontend configuration:"
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL configured in frontend: $BACKEND_URL"
echo ""

echo "✅ Connection test completed!"
echo ""
echo "📋 Endpoints Status:"
echo "  Backend Health: $BACKEND_URL/"
echo "  Products API:   $BACKEND_URL/api/products"
echo "  Search API:     $BACKEND_URL/api/vibe"
echo "  Thread API:     $BACKEND_URL/api/thread/{id}"
echo ""
echo "🌐 Frontend: http://demo.scruel.com:3000"
