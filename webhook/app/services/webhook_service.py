"""Webhook processing service"""
from fastapi import HTTPException, status
from kafka.errors import NoBrokersAvailable

from app.models.jira import JiraWebhookPayload
from app.schemas.webhook import WebhookResponse
from app.services.kafka_service import KafkaService
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class WebhookService:
    """Service for processing webhook events"""
    
    def __init__(self, kafka_service: KafkaService):
        self.kafka_service = kafka_service
    
    async def process_jira_webhook(self, payload: JiraWebhookPayload) -> WebhookResponse:
        """
        Process Jira webhook event and publish to Kafka
        
        Args:
            payload: Validated Jira webhook payload
            
        Returns:
            WebhookResponse with processing details
            
        Raises:
            HTTPException: If Kafka is unavailable or publish fails
        """
        logger.info(
            f"Processing Jira webhook event: {payload.webhookEvent} "
            f"for issue {payload.issue.key}"
        )
        
        # Check Kafka connection
        if not self.kafka_service.is_connected():
            logger.error("Kafka producer is not connected")
            try:
                self.kafka_service.reconnect()
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
        
        # Publish to Kafka
        try:
            success = self.kafka_service.publish(
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
            
            return WebhookResponse(
                status="accepted",
                message="Webhook event received and published to Kafka",
                issue_key=payload.issue.key,
                webhook_event=payload.webhookEvent,
                kafka_topic=settings.kafka_topic
            )
            
        except HTTPException:
            raise
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

