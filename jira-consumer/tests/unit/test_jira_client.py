"""Unit tests for Jira client"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from jira.exceptions import JIRAError

from app.clients.jira_client import JiraClient


@pytest.fixture
def mock_jira():
    """Mock JIRA client"""
    with patch('app.clients.jira_client.JIRA') as mock:
        yield mock


@pytest.fixture
def mock_settings():
    """Mock settings"""
    with patch('app.clients.jira_client.settings') as mock:
        mock.jira_enabled = True
        mock.jira_server = "https://test.atlassian.net"
        mock.jira_email = "test@example.com"
        mock.jira_api_token = "test-token"
        yield mock


class TestJiraClientInitialization:
    """Test Jira client initialization"""
    
    def test_init_with_valid_config(self, mock_jira, mock_settings):
        """Test initialization with valid configuration"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        
        client = JiraClient()
        
        assert client.client is not None
        mock_jira.assert_called_once()
    
    def test_init_disabled(self, mock_jira):
        """Test initialization when Jira is disabled"""
        with patch('app.clients.jira_client.settings') as mock_settings:
            mock_settings.jira_enabled = False
            
            client = JiraClient()
            
            assert client.client is None
            mock_jira.assert_not_called()
    
    def test_init_missing_config(self, mock_jira):
        """Test initialization with missing configuration"""
        with patch('app.clients.jira_client.settings') as mock_settings:
            mock_settings.jira_enabled = True
            mock_settings.jira_server = ""
            mock_settings.jira_email = "test@example.com"
            mock_settings.jira_api_token = "token"
            
            client = JiraClient()
            
            assert client.client is None
            mock_jira.assert_not_called()
    
    def test_init_connection_error(self, mock_jira, mock_settings):
        """Test initialization with connection error"""
        mock_jira.side_effect = JIRAError(status_code=401, text="Unauthorized")
        
        with pytest.raises(JIRAError):
            JiraClient()


class TestAddComment:
    """Test add_comment method"""
    
    def test_add_comment_success(self, mock_jira, mock_settings):
        """Test successful comment addition"""
        # Setup mock
        mock_comment = Mock()
        mock_comment.id = "12345"
        mock_comment.body = "Test comment"
        mock_comment.created = "2024-04-29T10:00:00"
        mock_comment.author.displayName = "Test User"
        
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        mock_jira.return_value.add_comment.return_value = mock_comment
        
        client = JiraClient()
        result = client.add_comment("TEST-123", "Test comment")
        
        assert result is not None
        assert result["id"] == "12345"
        assert result["body"] == "Test comment"
        assert result["author"] == "Test User"
        mock_jira.return_value.add_comment.assert_called_once_with("TEST-123", "Test comment")
    
    def test_add_comment_client_not_initialized(self):
        """Test add_comment when client is not initialized"""
        with patch('app.clients.jira_client.settings') as mock_settings:
            mock_settings.jira_enabled = False
            
            client = JiraClient()
            result = client.add_comment("TEST-123", "Test comment")
            
            assert result is None
    
    def test_add_comment_issue_not_found(self, mock_jira, mock_settings):
        """Test add_comment with non-existent issue"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        mock_jira.return_value.add_comment.side_effect = JIRAError(
            status_code=404,
            text="Issue not found"
        )
        
        client = JiraClient()
        
        with pytest.raises(JIRAError):
            client.add_comment("NONEXISTENT-999", "Test comment")
    
    def test_add_comment_permission_denied(self, mock_jira, mock_settings):
        """Test add_comment with permission error"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        mock_jira.return_value.add_comment.side_effect = JIRAError(
            status_code=403,
            text="Permission denied"
        )
        
        client = JiraClient()
        
        with pytest.raises(JIRAError):
            client.add_comment("TEST-123", "Test comment")
    
    def test_add_comment_rate_limited(self, mock_jira, mock_settings):
        """Test add_comment with rate limiting"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        mock_jira.return_value.add_comment.side_effect = JIRAError(
            status_code=429,
            text="Rate limit exceeded"
        )
        
        client = JiraClient()
        
        with pytest.raises(JIRAError):
            client.add_comment("TEST-123", "Test comment")


class TestGetIssue:
    """Test get_issue method"""
    
    def test_get_issue_success(self, mock_jira, mock_settings):
        """Test successful issue retrieval"""
        # Setup mock issue
        mock_issue = Mock()
        mock_issue.key = "TEST-123"
        mock_issue.fields.summary = "Test issue"
        mock_issue.fields.status.name = "In Progress"
        mock_issue.fields.assignee.displayName = "Test User"
        mock_issue.fields.created = "2024-04-29T10:00:00"
        
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        mock_jira.return_value.issue.return_value = mock_issue
        
        client = JiraClient()
        result = client.get_issue("TEST-123")
        
        assert result is not None
        assert result["key"] == "TEST-123"
        assert result["summary"] == "Test issue"
        assert result["status"] == "In Progress"
        assert result["assignee"] == "Test User"
    
    def test_get_issue_not_found(self, mock_jira, mock_settings):
        """Test get_issue with non-existent issue"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        mock_jira.return_value.issue.side_effect = JIRAError(
            status_code=404,
            text="Issue not found"
        )
        
        client = JiraClient()
        result = client.get_issue("NONEXISTENT-999")
        
        assert result is None


class TestHealthCheck:
    """Test health_check method"""
    
    def test_health_check_success(self, mock_jira, mock_settings):
        """Test successful health check"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        
        client = JiraClient()
        result = client.health_check()
        
        assert result is True
    
    def test_health_check_client_not_initialized(self):
        """Test health check when client is not initialized"""
        with patch('app.clients.jira_client.settings') as mock_settings:
            mock_settings.jira_enabled = False
            
            client = JiraClient()
            result = client.health_check()
            
            assert result is False
    
    def test_health_check_connection_error(self, mock_jira, mock_settings):
        """Test health check with connection error"""
        mock_jira.return_value.server_info.side_effect = [
            {"version": "9.0.0"},  # First call in __init__
            JIRAError(status_code=500, text="Server error")  # Second call in health_check
        ]
        
        client = JiraClient()
        result = client.health_check()
        
        assert result is False


class TestIsEnabled:
    """Test is_enabled method"""
    
    def test_is_enabled_true(self, mock_jira, mock_settings):
        """Test is_enabled when client is initialized"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        
        client = JiraClient()
        
        assert client.is_enabled() is True
    
    def test_is_enabled_false(self):
        """Test is_enabled when client is not initialized"""
        with patch('app.clients.jira_client.settings') as mock_settings:
            mock_settings.jira_enabled = False
            
            client = JiraClient()
            
            assert client.is_enabled() is False


class TestClose:
    """Test close method"""
    
    def test_close_success(self, mock_jira, mock_settings):
        """Test successful close"""
        mock_jira.return_value.server_info.return_value = {"version": "9.0.0"}
        
        client = JiraClient()
        client.close()
        
        assert client.client is None
        mock_jira.return_value.close.assert_called_once()
    
    def test_close_when_not_initialized(self):
        """Test close when client is not initialized"""
        with patch('app.clients.jira_client.settings') as mock_settings:
            mock_settings.jira_enabled = False
            
            client = JiraClient()
            client.close()  # Should not raise error
            
            assert client.client is None

