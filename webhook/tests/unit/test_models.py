"""Unit tests for Pydantic models"""
import pytest
from pydantic import ValidationError

from app.models.jira import JiraWebhookPayload


def test_jira_webhook_payload_valid(sample_jira_payload):
    """Test valid Jira webhook payload"""
    payload = JiraWebhookPayload(**sample_jira_payload)
    
    assert payload.timestamp == 1713782400000
    assert payload.webhookEvent == "jira:issue_created"
    assert payload.user.name == "charles"
    assert payload.issue.key == "PROJ-123"
    assert payload.issue.fields.summary == "API returns 500 on login"


def test_jira_webhook_payload_missing_required_field():
    """Test Jira webhook payload with missing required field"""
    invalid_payload = {
        "timestamp": 1713782400000,
        "webhookEvent": "jira:issue_created"
        # Missing user and issue fields
    }
    
    with pytest.raises(ValidationError):
        JiraWebhookPayload(**invalid_payload)


def test_jira_webhook_payload_invalid_type():
    """Test Jira webhook payload with invalid type"""
    invalid_payload = {
        "timestamp": "not_a_number",  # Should be int
        "webhookEvent": "jira:issue_created",
        "user": {},
        "issue": {}
    }
    
    with pytest.raises(ValidationError):
        JiraWebhookPayload(**invalid_payload)

# Made with Bob
