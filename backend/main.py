from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Nexalyze GrowthOS API",
    version="0.1.0",
    description="AI-powered Growth Operating System backend"
)

class ContentRequest(BaseModel):
    topic: str
    platform: str
    tone: str = "professional"

@app.get("/")
def root():
    return {
        "message": "Nexalyze GrowthOS API is running",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/generate-content")
def generate_content(request: ContentRequest):
    return {
        "topic": request.topic,
        "platform": request.platform,
        "tone": request.tone,
        "draft": f"Draft {request.platform} post about {request.topic} in a {request.tone} tone."
    }
