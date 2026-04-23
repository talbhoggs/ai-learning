"""FastAPI application for Jira webhook to Kafka"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1.router import api_router
from app.api.dependencies import get_kafka_service

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Jira Webhook to Kafka application")
    kafka_service = get_kafka_service()
    try:
        # Test Kafka connection
        if not kafka_service.is_connected():
            logger.warning("Kafka producer not connected on startup")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jira Webhook to Kafka application")
    kafka_service.close()


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Webhook endpoint to receive Jira events and publish to Kafka",
    lifespan=lifespan
)

# Include API router
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )

# Made with Bob
