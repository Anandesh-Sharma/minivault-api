# MiniVault API

A simple REST API powered by AI that generates text responses. Perfect for chatbots, content generation, and AI-powered applications.

## 🚀 Quick Start

### 1. Prerequisites
- Docker installed on your system
- At least 4GB free RAM

### 2. Setup (One Command)
```bash
git clone https://github.com/Anandesh-Sharma/minivault-api.git
cd minivault-api
./setup.sh
```

That's it! The API will be running at **http://localhost:8000**

## 🎯 How to Use

### Generate Text
Send a POST request to generate AI responses:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short poem about the ocean"}'
```

### Stream Responses (Real-time)
For real-time streaming responses:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me a story", "stream": true}'
```

### Check if API is Working
```bash
curl http://localhost:8000/health
```

## 📋 API Reference

### Request Format
```json
{
  "prompt": "Your question or instruction here",
  "stream": false
}
```

- `prompt`: Your text input (required)
- `stream`: Set to `true` for real-time streaming (optional)

### Response Format
```json
{
  "response": "AI generated text response",
  "model": "minivault-ollama",
  "response_time_ms": 1250
}
```


## 📍 Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/generate` | POST | Generate AI responses |
| `/health` | GET | Check API status |
| `/docs` | GET | Interactive API documentation |

## 🆘 Troubleshooting

### API Not Starting?
```bash
# Check container status
docker ps

# Restart everything
docker-compose down
./setup.sh
```

### View Logs
```bash
# API logs
docker logs minivault-api

# Ollama logs  
docker logs minivault-ollama
```

## 💡 Use Cases

- **Chatbots**: Real-time conversational AI
- **Content Generation**: Articles, blogs, product descriptions
- **Code Assistance**: Programming help and code generation
- **Creative Writing**: Stories, poems, creative content
- **Summarization**: Text summary and analysis
- **Q&A Systems**: Automated question answering

## 📞 Support

- **API Documentation**: http://localhost:8000/docs (when running)
- **Health Check**: http://localhost:8000/health
- **Logs**: Check `logs/log.jsonl` for interaction history

## ⚡ Performance

- **Model**: tinyllama:latest (lightweight, fast)
- **Response Time**: ~1-3 seconds typical
- **Memory Usage**: ~2-4GB RAM
- **Streaming**: Real-time token-by-token output
- **CPU Only**: No GPU required

---

**Ready to start generating AI content? Run `./setup.sh` and you're good to go!** 🚀 