"""FastAPI application for Jira webhook to Kafka"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from kafka.errors import NoBrokersAvailable

from .models import JiraWebhookPayload
from .kafka_producer import kafka_producer
from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Jira Webhook to Kafka application")
    try:
        # Test Kafka connection
        if not kafka_producer.is_connected():
            logger.warning("Kafka producer not connected on startup")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jira Webhook to Kafka application")
    kafka_producer.close()


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Webhook endpoint to receive Jira events and publish to Kafka",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "kafka_connected": kafka_producer.is_connected()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    kafka_status = kafka_producer.is_connected()
    
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


@app.post("/webhook/jira", status_code=status.HTTP_202_ACCEPTED)
async def jira_webhook(payload: JiraWebhookPayload):
    """
    Receive Jira webhook events and publish to Kafka
    
    Args:
        payload: Validated Jira webhook payload
        
    Returns:
        Acceptance confirmation with message details
        
    Raises:
        HTTPException: 503 if Kafka is unavailable, 500 if publish fails
    """
    logger.info(
        f"Received Jira webhook event: {payload.webhookEvent} "
        f"for issue {payload.issue.key}"
    )
    
    # Check Kafka connection
    if not kafka_producer.is_connected():
        logger.error("Kafka producer is not connected")
        try:
            kafka_producer.reconnect()
        except NoBrokersAvailable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Service Unavailable",
                    "message": "Kafka broker is not available. Please try again later.",
                    "retry_after": 60
                }
            )
        except Exception as e:
            logger.error(f"Failed to reconnect to Kafka: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Service Unavailable",
                    "message": "Unable to connect to Kafka broker",
                    "retry_after": 60
                }
            )
    
    # Prepare message for Kafka
    message = payload.model_dump()
    message_key = payload.issue.key  # Use issue key as partition key
    
    # Send to Kafka
    try:
        success = kafka_producer.send_message(
            topic=settings.kafka_topic,
            message=message,
            key=message_key
        )
        
        if not success:
            logger.error(f"Failed to publish message for issue {payload.issue.key}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal Server Error",
                    "message": "Failed to publish message to Kafka",
                    "issue_key": payload.issue.key
                }
            )
        
        logger.info(f"Successfully published message for issue {payload.issue.key} to Kafka")
        
        return {
            "status": "accepted",
            "message": "Webhook event received and published to Kafka",
            "issue_key": payload.issue.key,
            "webhook_event": payload.webhookEvent,
            "kafka_topic": settings.kafka_topic
        }
        
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing the webhook",
                "issue_key": payload.issue.key
            }
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )

# Made with Bob
