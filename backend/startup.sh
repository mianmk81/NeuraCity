#!/bin/bash
# NeuraCity Backend Startup Script (Linux/Mac)

echo "====================================="
echo "   NeuraCity Backend Startup"
echo "====================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys."
    echo ""
    echo "Run: cp .env.example .env"
    exit 1
fi

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p uploads

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Dependencies already installed."
fi

echo ""
echo "Starting NeuraCity API server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python run.py
