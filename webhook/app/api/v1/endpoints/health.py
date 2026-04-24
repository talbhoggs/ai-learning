"""Health check endpoints"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.schemas.health import HealthResponse
from app.services.kafka_service import KafkaService
from app.api.dependencies import get_kafka_service
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    kafka_service = get_kafka_service()
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "kafka_connected": kafka_service.is_connected()
    }


@router.get("/health")
async def health_check(
    kafka_service: KafkaService = Depends(get_kafka_service)
):
    """Health check endpoint"""
    kafka_status = kafka_service.is_connected()
    
    if not kafka_status:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "kafka": "disconnected",
                "message": "Kafka producer is not connected"
            }
        )
    
    return {
        "status": "healthy",
        "kafka": "connected"
    }

