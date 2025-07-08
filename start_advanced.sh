#!/bin/bash

# MiniVault API Advanced Quick Start Script
# This script sets up and starts the advanced MiniVault API server with bonus features

echo "🚀 MiniVault API Advanced Quick Start"
echo "====================================="

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

# Install/upgrade dependencies (including advanced ones)
echo "📥 Installing dependencies (including ML libraries)..."
echo "⚠️  Note: This may take a few minutes for first-time setup due to PyTorch..."
pip install -r requirements.txt > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "Please check your internet connection and Python version"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create config file if it doesn't exist
if [ ! -f "config.env" ]; then
    echo "📋 Creating configuration file..."
    cp config.env.example config.env
    echo "✅ Configuration file created (config.env)"
    echo "💡 You can edit config.env to customize model settings"
fi

# Check if port 8002 is available
if lsof -Pi :8002 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8002 is already in use"
    echo "Please stop the existing service or change the port in app_advanced.py"
    exit 1
fi

# Ask user about model type
echo ""
echo "🤖 Model Configuration:"
echo "1. Stubbed responses (fast, no ML dependencies)"
echo "2. Local LLM with Hugging Face Transformers (slower, requires ML libraries)"
echo ""
read -p "Choose model type (1 or 2, default=1): " model_choice

if [ "$model_choice" = "2" ]; then
    echo "MODEL_TYPE=transformers" > config.env
    echo "HF_MODEL_NAME=distilgpt2" >> config.env
    echo "🧠 Configured for local LLM (DistilGPT-2)"
    echo "⚠️  First startup will download the model (~250MB)"
else
    echo "MODEL_TYPE=stubbed" > config.env
    echo "🎭 Configured for intelligent stubbed responses"
fi

echo "API_HOST=0.0.0.0" >> config.env
echo "API_PORT=8002" >> config.env

# Ensure logs directory exists
mkdir -p logs

# Start the server
echo ""
echo "🎯 Starting MiniVault API Advanced server..."
echo "📍 Server will be available at: http://localhost:8002"
echo "📚 API documentation: http://localhost:8002/docs"
echo "🌊 Features: Streaming responses, enhanced logging, model info"
echo ""
echo "🔄 Starting server (press Ctrl+C to stop)..."

# Load environment and start
export $(cat config.env | grep -v '^#' | xargs)
python app_advanced.py 