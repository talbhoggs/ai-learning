"""Webhook response schemas"""
from pydantic import BaseModel


class WebhookResponse(BaseModel):
    """Response model for webhook endpoint"""
    status: str
    message: str
    issue_key: str
    webhook_event: str
    kafka_topic: str

# Made with Bob
