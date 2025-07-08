#!/bin/bash

echo "🚀 Setting up MiniVault API with Ollama"
echo "======================================"

# Function to wait for Ollama to be ready
wait_for_ollama() {
    echo "⏳ Waiting for Ollama service to be ready..."
    while ! curl -s http://localhost:11434/api/tags > /dev/null; do
        sleep 2
        echo "   Still waiting for Ollama..."
    done
    echo "✅ Ollama service is ready!"
}

# Function to pull the model
pull_model() {
    local model=${1:-"llama3.2:1b"}
    echo "📥 Pulling Ollama model: $model"
    echo "   This may take a few minutes for the first time..."
    
    curl -X POST http://localhost:11434/api/pull \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$model\"}" \
        --no-progress-meter

    if [ $? -eq 0 ]; then
        echo "✅ Model $model pulled successfully!"
    else
        echo "❌ Failed to pull model $model"
        exit 1
    fi
}

# Main setup
echo "🔧 Starting setup process..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "❌ Docker and docker-compose are required but not found"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found"

# Start services
echo "🚀 Starting services with docker-compose..."
docker-compose up -d

# Wait for Ollama to be ready
wait_for_ollama

# Pull the default model
MODEL=${OLLAMA_MODEL:-"llama3.2:1b"}
pull_model "$MODEL"

# Ensure API container is running after Ollama is ready
echo "🔧 Starting API container..."
docker-compose up -d api

# Wait a moment and verify API is running
sleep 3
if docker ps --filter "name=minivault-api" --filter "status=running" | grep -q minivault-api; then
    echo "✅ API container is running!"
else
    echo "⚠️  Starting API container manually..."
    docker start minivault-api || docker-compose restart api
fi

# Final health check
echo "🔍 Verifying services..."
sleep 2

# Check API health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is healthy and responding!"
else
    echo "⚠️  API might still be starting up. Check docker logs if needed:"
    echo "   docker logs minivault-api"
fi

echo ""
echo "🎉 Setup complete!"
echo "======================================"
echo "📍 API is available at: http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo "🧠 Ollama: http://localhost:11434"
echo "🧪 Test endpoint:"
echo "   curl -X POST http://localhost:8000/generate \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"prompt\": \"Hello, how are you?\"}'"
echo ""
echo "For streaming:"
echo "   curl -X POST http://localhost:8000/generate \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"prompt\": \"Tell me a story\", \"stream\": true}'"
echo ""
echo "📋 Check container status: docker ps"
echo "📄 View API logs: docker logs minivault-api"
echo "📄 View Ollama logs: docker logs minivault-ollama" 