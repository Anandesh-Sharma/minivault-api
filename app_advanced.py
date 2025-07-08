import json
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator
import random
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
import uvicorn
from dotenv import load_dotenv
import psutil

# Load environment variables
load_dotenv()

# Global model storage
model_cache: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for model loading and cleanup"""
    # Startup: Load models if configured
    model_type = os.getenv("MODEL_TYPE", "stubbed")
    if model_type == "transformers":
        await load_transformers_model()
    
    print(f"🚀 MiniVault API (Advanced) started with {model_type} model")
    yield
    
    # Shutdown: Cleanup models
    global model_cache
    model_cache.clear()
    print("🔄 Model cache cleared")

# Pydantic models for request/response validation
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        if len(v.strip()) > 10000:
            raise ValueError('Prompt too long (max 10000 characters)')
        return v.strip()
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        if v is not None and (v < 1 or v > 1000):
            raise ValueError('max_tokens must be between 1 and 1000')
        return v
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v is not None and (v < 0.0 or v > 2.0):
            raise ValueError('temperature must be between 0.0 and 2.0')
        return v

class GenerateResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    response: str
    model: str
    response_time_ms: int
    tokens_generated: Optional[int] = None
    model_info: Optional[Dict[str, Any]] = None

class StreamChunk(BaseModel):
    token: str
    is_final: bool = False
    chunk_id: int
    total_tokens: Optional[int] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    status: str
    timestamp: str
    logs_directory: bool
    api_version: str
    model_type: str
    model_loaded: bool
    system_info: Dict[str, Any]

class LogStatsResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    total_requests: int
    avg_response_time_ms: float
    last_24h_requests: int
    model_usage: Dict[str, int]
    performance_metrics: Dict[str, Any]

# Initialize FastAPI with lifespan
app = FastAPI(
    title="MiniVault API (Advanced)",
    description="Advanced lightweight REST API simulating ModelVault functionality with streaming and local LLM support",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response templates (enhanced with more variety)
RESPONSE_TEMPLATES = {
    "technical": [
        "Here's a technical explanation of {topic}: {explanation}",
        "From a technical perspective, {topic} involves {details}",
        "The implementation of {topic} typically requires {requirements}",
        "Key technical considerations for {topic} include {considerations}"
    ],
    "creative": [
        "Let me paint a picture of {concept}: {description}",
        "Imagine {scenario} where {details}",
        "In a world where {premise}, {story}",
        "Picture this: {creative_response}"
    ],
    "question": [
        "That's an excellent question about {subject}. {answer}",
        "To address your question about {topic}: {response}",
        "Great question! Regarding {subject}, {explanation}",
        "Your question touches on {area}. Here's my perspective: {answer}"
    ],
    "general": [
        "Based on your prompt about {topic}, {response}",
        "Regarding {subject}, here are some key points: {details}",
        "Your request about {topic} brings up {considerations}",
        "In response to your query about {subject}: {answer}"
    ]
}

async def load_transformers_model():
    """Load Hugging Face transformers model"""
    try:
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
        
        model_name = os.getenv("HF_MODEL_NAME", "distilgpt2")
        print(f"🔄 Loading model: {model_name}")
        
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Add padding token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model_cache['tokenizer'] = tokenizer
        model_cache['model'] = model
        model_cache['model_name'] = model_name
        model_cache['loaded_at'] = datetime.utcnow().isoformat()
        
        print(f"✅ Model {model_name} loaded successfully")
        
    except ImportError:
        print("⚠️ Transformers not available, falling back to stubbed responses")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("🔄 Falling back to stubbed responses")

async def generate_with_transformers(prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
    """Generate response using Hugging Face transformers"""
    try:
        import torch
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
        
        if 'model' not in model_cache or 'tokenizer' not in model_cache:
            raise Exception("Model not loaded")
        
        tokenizer = model_cache['tokenizer']
        model = model_cache['model']
        
        # Encode the prompt
        inputs = tokenizer.encode(prompt, return_tensors='pt', truncation=True, max_length=512)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=2
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part
        generated_text = response[len(prompt):].strip()
        
        return generated_text if generated_text else "I understand your request. Let me provide a helpful response."
        
    except Exception as e:
        print(f"❌ Transformers generation failed: {e}")
        # Fallback to stubbed response
        return generate_stubbed_response(prompt)

async def stream_transformers_response(prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> AsyncGenerator[str, None]:
    """Stream response token by token using transformers"""
    try:
        import torch
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
        
        if 'model' not in model_cache or 'tokenizer' not in model_cache:
            raise Exception("Model not loaded")
        
        tokenizer = model_cache['tokenizer']
        model = model_cache['model']
        
        # Encode the prompt
        inputs = tokenizer.encode(prompt, return_tensors='pt', truncation=True, max_length=512)
        
        generated_tokens = 0
        current_length = inputs.shape[1]
        
        while generated_tokens < max_tokens:
            # Generate next token
            with torch.no_grad():
                outputs = model(inputs)
                logits = outputs.logits[0, -1, :] / temperature
                
                # Apply temperature and sample
                probabilities = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probabilities, 1)
                
                # Check for end token
                if next_token.item() == tokenizer.eos_token_id:
                    break
                
                # Decode token
                token_text = tokenizer.decode([next_token.item()], skip_special_tokens=True)
                
                # Yield token
                yield token_text
                
                # Add token to inputs for next iteration
                inputs = torch.cat([inputs, next_token.unsqueeze(0)], dim=-1)
                generated_tokens += 1
                
                # Add small delay for realistic streaming
                await asyncio.sleep(0.05)
                
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        # Fallback to stubbed streaming
        async for token in stream_stubbed_response(prompt, max_tokens):
            yield token

async def stream_stubbed_response(prompt: str, max_tokens: int = 100) -> AsyncGenerator[str, None]:
    """Stream stubbed response token by token"""
    response = generate_stubbed_response(prompt)
    words = response.split()
    
    for i, word in enumerate(words[:max_tokens]):
        if i > 0:
            yield " "
        yield word
        await asyncio.sleep(0.1)  # Simulate generation delay

def generate_stubbed_response(prompt: str) -> str:
    """Generate intelligent stubbed response (enhanced version)"""
    prompt_lower = prompt.lower()
    
    # Enhanced categorization
    if any(keyword in prompt_lower for keyword in ['function', 'code', 'implement', 'algorithm', 'technical', 'api', 'database', 'system']):
        category = "technical"
        template = random.choice(RESPONSE_TEMPLATES["technical"])
        return template.format(
            topic="the technical implementation",
            explanation="a systematic approach involving careful design and robust architecture",
            details="proper planning, scalable design patterns, and thorough testing",
            requirements="understanding of core principles, appropriate tools, and best practices",
            considerations="performance optimization, security measures, and maintainability"
        )
    
    elif any(keyword in prompt_lower for keyword in ['story', 'creative', 'imagine', 'write', 'poem', 'fiction']):
        category = "creative"
        template = random.choice(RESPONSE_TEMPLATES["creative"])
        return template.format(
            concept="a vivid narrative",
            description="rich details that bring the story to life",
            scenario="creativity meets inspiration",
            details="characters develop and plots unfold naturally",
            premise="imagination knows no bounds",
            story="every word contributes to a compelling tale",
            creative_response="a unique perspective that captures the essence of your request"
        )
    
    elif prompt.endswith('?') or any(keyword in prompt_lower for keyword in ['what', 'how', 'why', 'when', 'where', 'explain']):
        category = "question"
        template = random.choice(RESPONSE_TEMPLATES["question"])
        return template.format(
            subject="your inquiry",
            answer="comprehensive information that addresses your specific needs",
            topic="the subject you've raised",
            response="detailed insights based on established knowledge",
            explanation="clear reasoning and practical examples",
            area="an important domain that requires careful consideration"
        )
    
    else:
        category = "general"
        template = random.choice(RESPONSE_TEMPLATES["general"])
        return template.format(
            topic="your request",
            response="thoughtful analysis and relevant information",
            subject="the matter at hand",
            details="key insights, practical considerations, and actionable recommendations",
            considerations="multiple perspectives and potential approaches",
            answer="a well-rounded response that addresses your needs effectively"
        )

async def log_interaction(prompt: str, response: str, response_time_ms: int, model_type: str, stream: bool = False, tokens_generated: Optional[int] = None):
    """Enhanced logging with performance metrics"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "response": response,
        "response_time_ms": response_time_ms,
        "model": model_type,
        "stream": stream,
        "tokens_generated": tokens_generated,
        "prompt_length": len(prompt),
        "response_length": len(response),
        "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        "cpu_percent": psutil.cpu_percent()
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    try:
        with open("logs/log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Warning: Failed to write to log file: {e}")

def get_system_info() -> Dict[str, Any]:
    """Get system performance information"""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_gb": round(psutil.virtual_memory().available / 1024**3, 2),
        "disk_usage_percent": psutil.disk_usage('/').percent
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check with system information"""
    model_type = os.getenv("MODEL_TYPE", "stubbed")
    model_loaded = 'model' in model_cache if model_type == "transformers" else True
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        logs_directory=os.path.exists("logs"),
        api_version="2.0.0",
        model_type=model_type,
        model_loaded=model_loaded,
        system_info=get_system_info()
    )

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """Generate response with optional streaming"""
    start_time = time.time()
    model_type = os.getenv("MODEL_TYPE", "stubbed")
    
    if request.stream:
        # Return streaming response
        async def generate():
            chunk_id = 0
            full_response = ""
            
            if model_type == "transformers" and 'model' in model_cache:
                stream_gen = stream_transformers_response(request.prompt, request.max_tokens, request.temperature)
            else:
                stream_gen = stream_stubbed_response(request.prompt, request.max_tokens)
            
            async for token in stream_gen:
                full_response += token
                chunk = StreamChunk(
                    token=token,
                    chunk_id=chunk_id,
                    is_final=False
                )
                yield f"data: {chunk.model_dump_json()}\n\n"
                chunk_id += 1
            
            # Final chunk
            response_time_ms = int((time.time() - start_time) * 1000)
            final_chunk = StreamChunk(
                token="",
                chunk_id=chunk_id,
                is_final=True,
                total_tokens=len(full_response.split())
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"
            
            # Log the interaction
            await log_interaction(
                request.prompt, 
                full_response, 
                response_time_ms, 
                model_type,
                stream=True,
                tokens_generated=len(full_response.split())
            )
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    else:
        # Regular response
        try:
            if model_type == "transformers" and 'model' in model_cache:
                response_text = await generate_with_transformers(
                    request.prompt, 
                    request.max_tokens or 100, 
                    request.temperature or 0.7
                )
            else:
                response_text = generate_stubbed_response(request.prompt)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            tokens_generated = len(response_text.split())
            
            # Enhanced model info
            model_info = {}
            if model_type == "transformers" and 'model' in model_cache:
                model_info = {
                    "model_name": model_cache.get('model_name', 'unknown'),
                    "loaded_at": model_cache.get('loaded_at'),
                    "parameters": "distilgpt2 (82M parameters)" if "distilgpt2" in model_cache.get('model_name', '') else "unknown"
                }
            
            # Log the interaction
            await log_interaction(
                request.prompt, 
                response_text, 
                response_time_ms, 
                model_type,
                tokens_generated=tokens_generated
            )
            
            return GenerateResponse(
                response=response_text,
                model=f"minivault-{model_type}",
                response_time_ms=response_time_ms,
                tokens_generated=tokens_generated,
                model_info=model_info if model_info else None
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Generation failed",
                    details=str(e),
                    timestamp=datetime.utcnow().isoformat()
                ).model_dump()
            )

@app.get("/logs/stats", response_model=LogStatsResponse)
async def get_log_statistics():
    """Enhanced log statistics with performance metrics"""
    if not os.path.exists("logs/log.jsonl"):
        return LogStatsResponse(
            total_requests=0,
            avg_response_time_ms=0.0,
            last_24h_requests=0,
            model_usage={},
            performance_metrics={}
        )
    
    try:
        with open("logs/log.jsonl", "r", encoding="utf-8") as f:
            logs = [json.loads(line.strip()) for line in f if line.strip()]
        
        if not logs:
            return LogStatsResponse(
                total_requests=0,
                avg_response_time_ms=0.0,
                last_24h_requests=0,
                model_usage={},
                performance_metrics={}
            )
        
        # Calculate statistics
        total_requests = len(logs)
        avg_response_time = sum(log.get("response_time_ms", 0) for log in logs) / total_requests
        
        # Last 24h requests
        now = datetime.utcnow()
        last_24h = sum(1 for log in logs 
                      if (now - datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))).total_seconds() < 86400)
        
        # Model usage
        model_usage = {}
        for log in logs:
            model = log.get("model", "unknown")
            model_usage[model] = model_usage.get(model, 0) + 1
        
        # Performance metrics
        response_times = [log.get("response_time_ms", 0) for log in logs]
        memory_usage = [log.get("memory_usage_mb", 0) for log in logs if "memory_usage_mb" in log]
        
        performance_metrics = {
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "avg_memory_usage_mb": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            "streaming_requests": sum(1 for log in logs if log.get("stream", False)),
            "total_tokens_generated": sum(log.get("tokens_generated", 0) for log in logs if log.get("tokens_generated"))
        }
        
        return LogStatsResponse(
            total_requests=total_requests,
            avg_response_time_ms=round(avg_response_time, 2),
            last_24h_requests=last_24h,
            model_usage=model_usage,
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to read log statistics",
                details=str(e),
                timestamp=datetime.utcnow().isoformat()
            ).model_dump()
        )

# New endpoints for advanced features

@app.get("/models/info")
async def get_model_info():
    """Get information about loaded models"""
    model_type = os.getenv("MODEL_TYPE", "stubbed")
    
    if model_type == "transformers" and 'model' in model_cache:
        return {
            "model_type": "transformers",
            "model_name": model_cache.get('model_name'),
            "loaded_at": model_cache.get('loaded_at'),
            "status": "loaded",
            "capabilities": ["text_generation", "streaming"]
        }
    else:
        return {
            "model_type": "stubbed",
            "model_name": "intelligent_stubbed_responses",
            "loaded_at": datetime.utcnow().isoformat(),
            "status": "active",
            "capabilities": ["text_generation", "streaming", "category_based_responses"]
        }

@app.post("/models/reload")
async def reload_model():
    """Reload the model (useful for development)"""
    model_type = os.getenv("MODEL_TYPE", "stubbed")
    
    if model_type == "transformers":
        global model_cache
        model_cache.clear()
        await load_transformers_model()
        return {"status": "reloaded", "model_type": model_type}
    else:
        return {"status": "no_reload_needed", "model_type": model_type}

if __name__ == "__main__":
    uvicorn.run(
        "app_advanced:app",
        host="0.0.0.0",
        port=8002,  # Different port for advanced version
        reload=True,
        log_level="info"
    ) 