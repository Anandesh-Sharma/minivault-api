#!/bin/bash

# MiniVault API Quick Start Script
# This script sets up and starts the MiniVault API server

echo "🚀 MiniVault API Quick Start"
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Please check your internet connection and try again."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if port 8001 is available
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8001 is already in use"
    echo "Please stop the existing service or change the port in app.py"
    exit 1
fi

# Start the server
echo "🎯 Starting MiniVault API server..."
echo "📍 Server will be available at: http://localhost:8001"
echo "📚 API documentation: http://localhost:8001/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python app.py 