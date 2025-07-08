import json
import os
import time
from datetime import datetime
import random

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import uvicorn

# Pydantic models for request/response validation
class GenerateRequest(BaseModel):
    prompt: str
    
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
    model: str = "minivault-stubbed"
    response_time_ms: int

class ErrorResponse(BaseModel):
    error: str
    detail: str

# Initialize FastAPI app
app = FastAPI(
    title="MiniVault API",
    description="A lightweight local REST API simulating core ModelVault functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response templates for intelligent stubbing
RESPONSE_TEMPLATES = {
    "code": [
        "Here's a Python solution for your request:\n\n```python\n# Your code implementation\nprint('Hello, World!')\n```",
        "I can help you with that coding task. Here's an approach:\n\n```python\n# Implementation example\nresult = process_data(input_data)\nreturn result\n```",
        "Based on your requirements, here's a code snippet:\n\n```python\n# Solution\ndef solve_problem():\n    return 'Solution implemented'\n```"
    ],
    "explanation": [
        "Let me explain this concept clearly. The key points are: 1) Understanding the fundamentals, 2) Applying the principles, and 3) Implementing the solution effectively.",
        "This is an interesting topic. To break it down: The main idea involves analyzing the problem, considering different approaches, and selecting the most appropriate solution.",
        "Great question! Here's how this works: First, we need to understand the context, then we can explore the various options and their implications."
    ],
    "question": [
        "That's a thought-provoking question. Let me provide some insights based on current understanding and best practices in this area.",
        "Excellent question! There are several factors to consider here, including the context, requirements, and potential trade-offs involved.",
        "Good question! The answer depends on various factors, but generally speaking, the recommended approach would be to analyze the situation carefully."
    ],
    "creative": [
        "What an interesting creative challenge! Here's an imaginative approach that combines innovation with practical considerations.",
        "I love creative projects like this! Let me suggest some unique ideas that could make this really engaging and effective.",
        "Creative tasks are exciting! Here's a fresh perspective that brings together different elements in an innovative way."
    ],
    "default": [
        "Thank you for your request. Based on your input, here's a comprehensive response that addresses your key points and provides actionable insights.",
        "I understand what you're looking for. Let me provide a detailed response that covers the important aspects of your query.",
        "Great input! Here's a thoughtful response that takes into account the nuances of your request and provides valuable information."
    ]
}

class ResponseGenerator:
    """Intelligent response generator with pattern matching and variability"""
    
    @staticmethod
    def categorize_prompt(prompt: str) -> str:
        """Categorize the prompt to select appropriate response template"""
        prompt_lower = prompt.lower()
        
        # Code-related keywords
        code_keywords = ['code', 'python', 'javascript', 'function', 'class', 'algorithm', 'program', 'script', 'debug']
        if any(keyword in prompt_lower for keyword in code_keywords):
            return "code"
        
        # Question keywords
        question_keywords = ['what', 'how', 'why', 'when', 'where', 'which', '?']
        if any(keyword in prompt_lower for keyword in question_keywords):
            return "question"
        
        # Explanation keywords
        explain_keywords = ['explain', 'describe', 'tell me about', 'what is', 'definition']
        if any(keyword in prompt_lower for keyword in explain_keywords):
            return "explanation"
        
        # Creative keywords
        creative_keywords = ['create', 'design', 'imagine', 'story', 'creative', 'brainstorm']
        if any(keyword in prompt_lower for keyword in creative_keywords):
            return "creative"
        
        return "default"
    
    @staticmethod
    def generate_response(prompt: str) -> str:
        """Generate an intelligent stubbed response based on prompt analysis"""
        category = ResponseGenerator.categorize_prompt(prompt)
        templates = RESPONSE_TEMPLATES[category]
        
        # Select random template
        base_response = random.choice(templates)
        
        # Add some personalization based on prompt content
        if len(prompt) > 100:
            suffix = "\n\nGiven the complexity of your request, I've provided a comprehensive response that should address your main concerns."
        elif '?' in prompt:
            suffix = "\n\nI hope this answers your question! Feel free to ask if you need clarification on any part."
        else:
            suffix = "\n\nThis approach should work well for your use case. Let me know if you'd like me to elaborate on any aspect."
        
        return base_response + suffix

class Logger:
    """Handles logging of all API interactions"""
    
    def __init__(self, log_file: str = "logs/log.jsonl"):
        self.log_file = log_file
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Ensure the logs directory exists"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log_interaction(self, prompt: str, response: str, response_time_ms: int, model: str = "minivault-stubbed"):
        """Log an interaction to the JSONL file"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "response": response,
            "response_time_ms": response_time_ms,
            "model": model,
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
response_generator = ResponseGenerator()
logger = Logger()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "MiniVault API is running",
        "version": "1.0.0",
        "endpoints": {
            "generate": "POST /generate",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "logs_directory": os.path.exists("logs"),
        "api_version": "1.0.0"
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest, http_request: Request):
    """Main endpoint for generating responses to prompts"""
    start_time = time.time()
    
    try:
        # Generate response
        response_text = response_generator.generate_response(request.prompt)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Create response object
        response_obj = GenerateResponse(
            response=response_text,
            response_time_ms=response_time_ms
        )
        
        # Log the interaction
        logger.log_interaction(
            prompt=request.prompt,
            response=response_text,
            response_time_ms=response_time_ms
        )
        
        return response_obj
        
    except Exception as e:
        # Calculate response time even for errors
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log the error
        error_msg = f"Internal server error: {str(e)}"
        logger.log_interaction(
            prompt=request.prompt,
            response=error_msg,
            response_time_ms=response_time_ms,
            model="error"
        )
        
        raise HTTPException(status_code=500, detail=error_msg)

@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    return HTTPException(status_code=400, detail=str(exc))

@app.get("/logs/stats")
async def get_log_stats():
    """Get statistics about logged interactions"""
    try:
        if not os.path.exists("logs/log.jsonl"):
            return {"message": "No logs found", "total_interactions": 0}
        
        with open("logs/log.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        total_interactions = len(lines)
        
        if total_interactions == 0:
            return {"message": "No interactions logged", "total_interactions": 0}
        
        # Parse last few entries for recent stats
        recent_logs = []
        for line in lines[-10:]:  # Last 10 entries
            try:
                recent_logs.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
        
        if recent_logs:
            avg_response_time = sum(log.get("response_time_ms", 0) for log in recent_logs) / len(recent_logs)
            avg_prompt_length = sum(log.get("prompt_length", 0) for log in recent_logs) / len(recent_logs)
        else:
            avg_response_time = 0
            avg_prompt_length = 0
        
        return {
            "total_interactions": total_interactions,
            "avg_response_time_ms": round(avg_response_time, 2),
            "avg_prompt_length": round(avg_prompt_length, 2),
            "recent_interactions": len(recent_logs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 