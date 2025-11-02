#!/bin/bash
# Frontend startup script for Information Trust Analysis System

echo "🎨 Starting Information Trust Analysis Frontend"
echo "================================================"

# Check if we're in the frontend directory
if [ ! -f "index.html" ] || [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the frontend directory"
    echo "   cd frontend && ./start_frontend.sh"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if serve is installed, if not install it
if ! command -v npx &> /dev/null; then
    echo "❌ npx is not available. Please update Node.js."
    exit 1
fi

echo "🔧 Installing dependencies..."
npm install

echo ""
echo "🚀 Starting frontend server on port 3000..."
echo "📝 Make sure backend is running on port 8000"
echo "   Backend: cd ../backend && python start_backend.py"
echo ""
echo "🌐 Frontend will be available at:"
echo "   http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start