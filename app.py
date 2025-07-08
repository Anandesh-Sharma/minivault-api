import json
import os
import time
from datetime import datetime
from typing import Optional, AsyncGenerator
import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
import uvicorn
import ollama

# Pydantic models for request/response validation
class GenerateRequest(BaseModel):
    prompt: str
    stream: Optional[bool] = False
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        if len(v.strip()) > 10000:  # Reasonable limit
            raise ValueError('Prompt too long (max 10000 characters)')
        return v.strip()

class GenerateResponse(BaseModel):
    response: str
    model: str = "minivault-ollama"
    response_time_ms: int

class ErrorResponse(BaseModel):
    error: str
    detail: str



# Initialize FastAPI app
app = FastAPI(
    title="MiniVault API",
    description="A lightweight local REST API with Ollama integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

class OllamaClient:
    """Ollama client for generating responses"""
    
    def __init__(self):
        # Configure ollama client to use our host
        self.client = ollama.Client(host=OLLAMA_HOST)
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response using Ollama"""
        try:
            response = self.client.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            # Fallback response if Ollama is unavailable
            return f"I understand your request about '{prompt[:50]}...'. However, I'm currently unable to connect to the language model service. Please ensure the Ollama service is running and try again."
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using Ollama"""
        try:
            response = self.client.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                stream=True
            )
            
            for chunk in response:
                if 'response' in chunk and chunk['response']:
                    yield chunk['response']
                    # Minimal delay to ensure proper streaming without blocking
                    await asyncio.sleep(0.001)
                    
        except Exception as e:
            # Fallback streaming response
            fallback_text = f"I understand your request about '{prompt[:50]}...'. However, I'm currently unable to connect to the language model service."
            words = fallback_text.split()
            for word in words:
                yield word + " "
                await asyncio.sleep(0.05)

class Logger:
    """Handles logging of all API interactions"""
    
    def __init__(self, log_file: str = "logs/log.jsonl"):
        self.log_file = log_file
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Ensure the logs directory exists"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log_interaction(self, prompt: str, response: str, response_time_ms: int, model: str = "minivault-ollama", stream: bool = False):
        """Log an interaction to the JSONL file"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "response": response,
            "response_time_ms": response_time_ms,
            "model": model,
            "stream": stream,
            "prompt_length": len(prompt),
            "response_length": len(response)
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            # Log to stderr if file logging fails
            print(f"Failed to write to log file: {e}")

# Initialize components
ollama_client = OllamaClient()
logger = Logger()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MiniVault API with Ollama integration",
        "version": "2.0.0",
        "endpoints": {
            "generate": "POST /generate",
            "health": "GET /health",
            "logs/stats": "GET /logs/stats"
        },
        "features": ["ollama_integration", "streaming_responses", "comprehensive_logging"]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    # Test Ollama connection
    ollama_status = "connected"
    try:
        # Quick test to see if Ollama is responsive
        ollama_client.client.list()
    except Exception:
        ollama_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "logs_directory": os.path.exists("logs"),
        "api_version": "2.0.0",
        "ollama_host": OLLAMA_HOST,
        "ollama_model": OLLAMA_MODEL,
        "ollama_status": ollama_status
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """Main endpoint for generating responses using Ollama"""
    start_time = time.time()
    
    try:
        if request.stream:
            # Return streaming response
            async def generate():
                full_response = ""
                async for chunk in ollama_client.generate_stream(request.prompt):
                    full_response += chunk
                    yield chunk
                
                # Log the complete interaction
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.log_interaction(request.prompt, full_response, response_time_ms, stream=True)
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache", 
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # Disable nginx buffering if present
                }
            )
        else:
            # Regular response
            response_text = await ollama_client.generate_response(request.prompt)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log the interaction
            logger.log_interaction(request.prompt, response_text, response_time_ms)
            
            return GenerateResponse(
                response=response_text,
                response_time_ms=response_time_ms
            )
            
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        error_response = f"Error generating response: {str(e)}"
        
        # Log the error
        logger.log_interaction(request.prompt, error_response, response_time_ms)
        
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Generation failed",
                detail=str(e)
            ).model_dump()
        )

@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    return HTTPException(
        status_code=400,
        detail=ErrorResponse(
            error="Validation error",
            detail=str(exc)
        ).model_dump()
    )

@app.get("/logs/stats")
async def get_log_stats():
    """Get statistics about logged interactions"""
    log_file = "logs/log.jsonl"
    
    if not os.path.exists(log_file):
        return {
            "total_interactions": 0,
            "avg_response_time_ms": 0,
            "avg_prompt_length": 0,
            "recent_interactions": 0
        }
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = [json.loads(line.strip()) for line in f if line.strip()]
        
        if not logs:
            return {
                "total_interactions": 0,
                "avg_response_time_ms": 0,
                "avg_prompt_length": 0,
                "recent_interactions": 0
            }
        
        # Calculate statistics
        total_interactions = len(logs)
        avg_response_time = sum(log.get("response_time_ms", 0) for log in logs) / total_interactions
        avg_prompt_length = sum(log.get("prompt_length", 0) for log in logs) / total_interactions
        
        # Recent interactions (last 24 hours)
        now = datetime.utcnow()
        recent_count = 0
        for log in logs:
            try:
                log_time = datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))
                if (now - log_time.replace(tzinfo=None)).total_seconds() < 86400:
                    recent_count += 1
            except:
                continue
        
        # Streaming vs regular requests
        streaming_requests = sum(1 for log in logs if log.get("stream", False))
        regular_requests = total_interactions - streaming_requests
        
        return {
            "total_interactions": total_interactions,
            "avg_response_time_ms": round(avg_response_time, 2),
            "avg_prompt_length": round(avg_prompt_length, 2),
            "recent_interactions": recent_count,
            "streaming_requests": streaming_requests,
            "regular_requests": regular_requests,
            "ollama_model": OLLAMA_MODEL
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to read log statistics",
                detail=str(e)
            ).model_dump()
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 