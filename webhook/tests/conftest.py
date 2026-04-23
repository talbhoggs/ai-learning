"""Pytest configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_jira_payload():
    """Sample Jira webhook payload for testing"""
    return {
        "timestamp": 1713782400000,
        "webhookEvent": "jira:issue_created",
        "user": {
            "self": "https://your-jira/rest/api/2/user?username=charles",
            "name": "charles",
            "displayName": "Charles D",
            "emailAddress": "charles@example.com"
        },
        "issue": {
            "id": "10001",
            "self": "https://your-jira/rest/api/2/issue/10001",
            "key": "PROJ-123",
            "fields": {
                "summary": "API returns 500 on login",
                "description": "Steps to reproduce...",
                "issuetype": {
                    "id": "10004",
                    "name": "Bug"
                },
                "project": {
                    "id": "10000",
                    "key": "PROJ",
                    "name": "Project Alpha"
                },
                "reporter": {
                    "name": "charles",
                    "displayName": "Charles D"
                },
                "creator": {
                    "name": "charles",
                    "displayName": "Charles D"
                },
                "priority": {
                    "id": "3",
                    "name": "Medium"
                },
                "status": {
                    "id": "1",
                    "name": "To Do"
                }
            }
        }
    }

# Made with Bob
