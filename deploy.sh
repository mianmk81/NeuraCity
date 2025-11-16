#!/bin/bash
# Railway deployment helper script

echo "🚀 Preparing NeuraCity for Railway deployment..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: backend/ and frontend/ directories not found"
    exit 1
fi

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Check if build was successful
if [ ! -d "frontend/dist" ]; then
    echo "❌ Error: Frontend build failed"
    exit 1
fi

echo "✅ Frontend built successfully"

# Check backend requirements
echo "🔍 Checking backend requirements..."
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: backend/requirements.txt not found"
    exit 1
fi

echo "✅ Backend requirements found"

echo ""
echo "✅ Ready for Railway deployment!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your repo to Railway"
echo "3. Set environment variables in Railway dashboard"
echo "4. Deploy!"
echo ""
echo "See RAILWAY_DEPLOYMENT.md for detailed instructions."

