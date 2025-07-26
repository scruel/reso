#!/bin/bash

# Deployment script for demo.scruel.com:3000

echo "🚀 Starting deployment process..."

# Build the application
echo "📦 Building application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"

# Start the application on port 3000
echo "🌟 Starting application on port 3000..."
npm start

echo "🎉 Application deployed successfully!"
echo "Frontend URL: http://demo.scruel.com:3000"
echo ""
echo "Available API Endpoints:"
echo "  GET  /api/products      - Get product list"
echo "  POST /api/vibe          - Search with intent analysis"
echo "  GET  /api/thread/{id}   - Get thread details"
echo ""
echo "Frontend is now accessible at: http://demo.scruel.com:3000"
