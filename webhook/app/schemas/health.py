"""Health check response schemas"""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    kafka: str
    message: str | None = None

# Made with Bob
