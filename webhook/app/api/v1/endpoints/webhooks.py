"""Webhook endpoints"""
from fastapi import APIRouter, Depends, Request, status
import json

from app.models.jira import JiraWebhookPayload
from app.schemas.webhook import WebhookResponse
from app.services.webhook_service import WebhookService
from app.api.dependencies import get_webhook_service
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/jira", status_code=status.HTTP_202_ACCEPTED, response_model=WebhookResponse)
async def jira_webhook(
    request: Request,
    payload: JiraWebhookPayload,
    webhook_service: WebhookService = Depends(get_webhook_service)
) -> WebhookResponse:
    """
    Receive Jira webhook events and publish to Kafka
    
    Args:
        request: FastAPI request object for logging
        payload: Validated Jira webhook payload
        webhook_service: Injected webhook service
        
    Returns:
        Acceptance confirmation with message details
        
    Raises:
        HTTPException: 503 if Kafka is unavailable, 500 if publish fails
    """
    # Debug logging for incoming requests
    logger.debug(f"Received webhook request from {request.client.host if request.client else 'unknown'}")
    logger.debug(f"Query params: {dict(request.query_params)}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    # Log the validated payload
    logger.info(f"Processing Jira webhook event: {payload.webhookEvent} for issue {payload.issue.key}")
    logger.debug(f"Payload: {payload.model_dump_json(indent=2)}")
    
    return await webhook_service.process_jira_webhook(payload)

