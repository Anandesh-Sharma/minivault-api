# MiniVault API

A lightweight REST API with Ollama integration for language model interaction, featuring streaming responses and comprehensive logging.

## 🚀 Features

- **Ollama Integration**: Real language model responses using Ollama
- **Streaming Support**: Token-by-token streaming responses
- **Docker Ready**: Complete containerization with docker-compose
- **CPU-Only**: Optimized for CPU-only Ollama deployment
- **Comprehensive Logging**: All interactions logged in JSONL format
- **Health Monitoring**: Built-in health checks and statistics
- **Easy Deployment**: One-command setup and deployment

## 📋 Project Structure

```
minivault-api/
├── app.py                 # Main FastAPI application with Ollama
├── Dockerfile             # API container configuration
├── docker-compose.yml     # Multi-service orchestration
├── setup.sh               # Automated setup script
├── test_client.py         # Comprehensive test client
├── requirements.txt       # Python dependencies
├── logs/                  # Auto-created logs directory
│   └── log.jsonl         # Interaction logs (JSONL format)
└── README.md             # This file
```

## 🔧 Quick Start

### Prerequisites
- Docker and Docker Compose
- At least 4GB RAM available
- Internet connection for model download

### 🚀 One-Command Setup

```bash
# Clone the repository
git clone https://github.com/Anandesh-Sharma/minivault-api.git
cd minivault-api

# Run the automated setup
./setup.sh
```

This will:
1. Start Ollama container
2. Build and start the API container  
3. Pull the Llama 3.2 1B model
4. Verify everything is working

### Manual Setup

```bash
# Start services
docker-compose up -d

# Wait for Ollama to be ready, then pull model
curl -X POST http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "llama3.2:1b"}'
```

## 🎯 API Endpoints

### 📍 Service URLs
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

### 🔥 Main Endpoints

#### `POST /generate`
Generate responses using Ollama:

**Regular Response:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain machine learning"}'
```

**Streaming Response:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me a story", "stream": true}'
```

**Request Format:**
```json
{
  "prompt": "Your question or prompt here",
  "stream": false  // Optional: true for streaming
}
```

**Response Format:**
```json
{
  "response": "Generated response text",
  "model": "minivault-ollama", 
  "response_time_ms": 1250
}
```

#### `GET /health`
Check API and Ollama status:
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:45.123Z",
  "api_version": "2.0.0",
  "ollama_host": "http://ollama:11434",
  "ollama_model": "llama3.2:1b",
  "ollama_status": "connected"
}
```

#### `GET /logs/stats`
View interaction statistics:
```bash
curl http://localhost:8000/logs/stats
```

**Response:**
```json
{
  "total_interactions": 42,
  "avg_response_time_ms": 1250.5,
  "recent_interactions": 10,
  "streaming_requests": 15,
  "regular_requests": 27,
  "ollama_model": "llama3.2:1b"
}
```

## 🧪 Testing

### Automated Tests
```bash
# Run comprehensive test suite
python test_client.py

# Interactive testing mode
python test_client.py --interactive
```

### Quick Manual Tests
```bash
# Test regular generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'

# Test streaming
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Count from 1 to 5", "stream": true}'

# Check health
curl http://localhost:8000/health

# View statistics  
curl http://localhost:8000/logs/stats
```

## 🐳 Docker Configuration

### Environment Variables
- `OLLAMA_HOST`: Ollama service URL (default: http://ollama:11434)
- `OLLAMA_MODEL`: Model to use (default: llama3.2:1b)

### Containers
- **ollama**: Runs Ollama service with CPU-only configuration
- **api**: Runs the FastAPI application

### Volumes
- **ollama_data**: Persistent storage for Ollama models
- **./logs**: Local logs directory mounted to container

## 📊 Logging

All interactions are logged to `logs/log.jsonl`:

```json
{
  "timestamp": "2025-01-20T10:30:45.123Z",
  "prompt": "user input here",
  "response": "ollama generated response",
  "response_time_ms": 1250,
  "model": "minivault-ollama",
  "stream": false,
  "prompt_length": 42,
  "response_length": 235
}
```

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2:1b

# Run API locally
python app.py
```

### Container Logs
```bash
# View API logs
docker-compose logs api

# View Ollama logs  
docker-compose logs ollama

# Follow logs in real-time
docker-compose logs -f
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill processes using ports 8000 or 11434
   lsof -ti:8000,11434 | xargs kill -9
   ```

2. **Ollama model not loaded**
   ```bash
   # Manually pull the model
   curl -X POST http://localhost:11434/api/pull \
     -H "Content-Type: application/json" \
     -d '{"name": "llama3.2:1b"}'
   ```

3. **Container health check failing**
   ```bash
   # Check container status
   docker-compose ps
   
   # View container logs
   docker-compose logs ollama
   docker-compose logs api
   ```

4. **Low memory issues**
   ```bash
   # Use smaller model
   export OLLAMA_MODEL=llama3.2:1b  # Already smallest
   
   # Or increase Docker memory allocation
   ```

## 🎯 Model Information

**Default Model**: Llama 3.2 1B
- **Size**: ~1.3GB download
- **Parameters**: 1 billion
- **CPU Compatible**: Optimized for CPU inference
- **Use Case**: Lightweight, fast responses

## 📈 Performance

**Expected Performance** (CPU-only):
- **Cold start**: 30-60 seconds (model loading)
- **Regular responses**: 1-3 seconds
- **Streaming responses**: Real-time token generation
- **Memory usage**: ~2-3GB (including Ollama)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test with Docker
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License. 