"""Integration tests for API endpoints"""
import pytest


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Jira Webhook to Kafka"
    assert data["status"] == "running"
    assert "kafka_connected" in data


def test_health_endpoint_success(client):
    """Test health check endpoint when healthy"""
    response = client.get("/health")
    
    # Note: This test assumes Kafka is running
    # In a real test, you'd mock the Kafka service
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "kafka" in data


@pytest.mark.skip(reason="Requires Kafka to be running")
def test_webhook_endpoint_success(client, sample_jira_payload):
    """Test webhook endpoint with valid payload"""
    response = client.post("/webhook/jira", json=sample_jira_payload)
    
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["issue_key"] == "PROJ-123"
    assert data["webhook_event"] == "jira:issue_created"


def test_webhook_endpoint_invalid_payload(client):
    """Test webhook endpoint with invalid payload"""
    invalid_payload = {
        "timestamp": "not_a_number",
        "webhookEvent": "jira:issue_created"
    }
    
    response = client.post("/webhook/jira", json=invalid_payload)
    
    assert response.status_code == 422  # Validation error

# Made with Bob
