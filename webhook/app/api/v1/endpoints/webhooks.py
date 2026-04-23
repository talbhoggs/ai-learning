"""Webhook endpoints"""
from fastapi import APIRouter, Depends, status

from app.models.jira import JiraWebhookPayload
from app.schemas.webhook import WebhookResponse
from app.services.webhook_service import WebhookService
from app.api.dependencies import get_webhook_service

router = APIRouter()


@router.post("/jira", status_code=status.HTTP_202_ACCEPTED, response_model=WebhookResponse)
async def jira_webhook(
    payload: JiraWebhookPayload,
    webhook_service: WebhookService = Depends(get_webhook_service)
) -> WebhookResponse:
    """
    Receive Jira webhook events and publish to Kafka
    
    Args:
        payload: Validated Jira webhook payload
        webhook_service: Injected webhook service
        
    Returns:
        Acceptance confirmation with message details
        
    Raises:
        HTTPException: 503 if Kafka is unavailable, 500 if publish fails
    """
    return await webhook_service.process_jira_webhook(payload)

# Made with Bob
