# MiniVault API

A lightweight local REST API simulating core ModelVault functionality. The API receives prompts and returns generated responses with comprehensive logging, designed as a production-ready prototype for machine learning model management.

## 🚀 Features

- **RESTful API**: Clean `/generate` endpoint for prompt processing
- **Intelligent Response Generation**: Context-aware stubbed responses with variability
- **Comprehensive Logging**: All interactions logged to JSONL format with metadata
- **Input Validation**: Robust validation and error handling
- **Health Monitoring**: Built-in health checks and statistics
- **CORS Support**: Ready for web frontend integration
- **Production Ready**: Clean code structure with proper error handling

## 📋 Project Structure

```
minivault-api/
├── app.py                 # Main FastAPI application
├── test_client.py         # Comprehensive test client
├── requirements.txt       # Python dependencies
├── logs/                  # Auto-created logs directory
│   └── log.jsonl         # Interaction logs (JSONL format)
└── README.md             # This file
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Anandesh-Sharma/minivault-api.git
   cd minivault-api
   ```

2. **Create and activate virtual environment** (recommended)
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the API server**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8001`

## 🎯 Usage Examples

### Quick Test with curl

```bash
# Health check
curl http://localhost:8001/health

# Generate response
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is machine learning?"}'

# Get log statistics
curl http://localhost:8001/logs/stats
```

### Using the Test Client

Run comprehensive tests:
```bash
python test_client.py
```

Interactive testing mode:
```bash
python test_client.py --interactive
```

### Python requests example

```python
import requests

# Generate response
response = requests.post(
    "http://localhost:8001/generate",
    json={"prompt": "Write a Python function to calculate fibonacci"}
)

print(response.json())
```

## 📚 API Documentation

### Endpoints

#### `POST /generate`
Generate a response to a given prompt.

**Request:**
```json
{
  "prompt": "Your prompt text here"
}
```

**Response:**
```json
{
  "response": "Generated response text",
  "model": "minivault-stubbed",
  "response_time_ms": 150
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid prompt (empty, too long)
- `500 Internal Server Error`: Server error

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:45.123Z",
  "logs_directory": true,
  "api_version": "1.0.0"
}
```

#### `GET /logs/stats`
Get statistics about logged interactions.

**Response:**
```json
{
  "total_interactions": 42,
  "avg_response_time_ms": 125.5,
  "avg_prompt_length": 85.2,
  "recent_interactions": 10
}
```

#### `GET /`
Root endpoint with API information.

### Interactive API Documentation

When the server is running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## 🔍 Implementation Notes

### Response Generation Strategy

The API uses an intelligent stubbing system that:

1. **Categorizes prompts** based on keywords:
   - **Code**: Python, function, algorithm, etc.
   - **Questions**: What, how, why, etc.
   - **Explanations**: Explain, describe, etc.
   - **Creative**: Create, design, story, etc.
   - **Default**: General responses

2. **Selects appropriate templates** for each category
3. **Adds contextual suffixes** based on prompt characteristics
4. **Provides consistent, varied responses**

### Logging System

All interactions are logged to `logs/log.jsonl` with:

```json
{
  "timestamp": "2025-01-20T10:30:45.123Z",
  "prompt": "user input here",
  "response": "generated response here",
  "response_time_ms": 150,
  "model": "minivault-stubbed",
  "prompt_length": 42,
  "response_length": 235
}
```

### Error Handling

- **Input validation** with Pydantic models
- **Graceful error responses** with proper HTTP status codes
- **Comprehensive logging** including errors
- **Fallback mechanisms** for file I/O issues

## 🧪 Testing

### Automated Testing

The test client provides comprehensive testing:

```bash
# Run all tests
python test_client.py

# Expected output:
# 🚀 Starting MiniVault API Comprehensive Tests
# ✅ Health check passed: healthy
# ✅ Response generated successfully...
# 🎯 Test Results: 15/15 tests passed
# 🎉 All tests passed! API is working correctly.
```

### Manual Testing Scenarios

1. **Valid prompts**: Various categories and lengths
2. **Invalid prompts**: Empty, whitespace-only, too long
3. **Edge cases**: Special characters, JSON-like input, multiline
4. **Error handling**: Malformed requests, server errors
5. **Performance**: Response time measurement

## 🚀 Future Improvements

### Immediate Enhancements
1. **Streaming Responses**: Token-by-token output for better UX
2. **Local LLM Integration**: Hugging Face Transformers or Ollama
3. **Authentication**: API key-based access control
4. **Rate Limiting**: Prevent API abuse
5. **Enhanced Logging**: Request IDs, user tracking, detailed metrics

### Advanced Features
1. **Model Management**: Multiple model backends
2. **Prompt Templates**: Pre-defined prompt patterns
3. **Response Caching**: Cache common responses
4. **Async Processing**: Background job processing
5. **Database Integration**: Persistent storage for logs and responses

## 🛠️ Development

### Code Quality
- **Type hints** throughout codebase
- **Comprehensive error handling**
- **Modular design** with clear separation of concerns
- **Production-ready** logging and monitoring

### Architecture Decisions
- **FastAPI**: Modern, fast, with automatic API documentation
- **Pydantic**: Data validation and serialization
- **JSONL logging**: Efficient, streamable log format
- **Stubbed responses**: Intelligent, categorized responses

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in app.py or kill existing process
   lsof -ti:8001 | xargs kill -9
   ```

2. **Module not found errors**
   ```bash
   # Ensure virtual environment is activated and dependencies installed
   pip install -r requirements.txt
   ```

3. **Permission errors with logs**
   ```bash
   # Ensure write permissions for logs directory
   chmod 755 logs/
   ```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the test client output for debugging
3. Check server logs for detailed error information
4. Open an issue on GitHub with reproduction steps 