"""Jira API client"""
from typing import Optional, Dict, Any
from jira import JIRA
from jira.exceptions import JIRAError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class JiraClient:
    """Client for Jira API operations"""
    
    def __init__(self):
        """Initialize Jira client"""
        self.client: Optional[JIRA] = None
        
        if not settings.jira_enabled:
            logger.warning("Jira integration is disabled (JIRA_ENABLED=false)")
            return
        
        if not settings.jira_server or not settings.jira_email or not settings.jira_api_token:
            logger.warning(
                "Jira integration disabled: Missing configuration "
                "(JIRA_SERVER, JIRA_EMAIL, or JIRA_API_TOKEN)"
            )
            return
        
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Jira"""
        try:
            logger.info(f"Connecting to Jira at {settings.jira_server}")
            self.client = JIRA(
                server=settings.jira_server,
                basic_auth=(settings.jira_email, settings.jira_api_token),
                options={'verify': True}  # Verify SSL certificates
            )
            logger.info("Successfully connected to Jira")
            
            # Log server info
            server_info = self.client.server_info()
            logger.info(f"Jira version: {server_info.get('version', 'unknown')}")
            
        except JIRAError as e:
            logger.error(f"Failed to connect to Jira: {str(e)}")
            if e.status_code == 401:
                logger.error("Authentication failed - check JIRA_EMAIL and JIRA_API_TOKEN")
            elif e.status_code == 403:
                logger.error("Access forbidden - check user permissions")
            self.client = None
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Jira: {str(e)}")
            self.client = None
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((JIRAError,)),
        reraise=True
    )
    def add_comment(self, issue_key: str, comment: str) -> Optional[Dict[str, Any]]:
        """
        Add a comment to a Jira issue with retry logic
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            comment: Comment text (supports Jira markdown)
            
        Returns:
            Comment object with id, body, created fields or None if failed
            
        Raises:
            JIRAError: If API call fails after retries
        """
        if not self.client:
            logger.warning("Jira client not initialized - cannot add comment")
            return None
        
        try:
            logger.info(f"Adding comment to {issue_key}")
            logger.debug(f"Comment preview: {comment[:100]}...")
            
            comment_obj = self.client.add_comment(issue_key, comment)
            
            result = {
                "id": comment_obj.id,
                "body": comment_obj.body,
                "created": comment_obj.created,
                "author": comment_obj.author.displayName if hasattr(comment_obj, 'author') else "unknown"
            }
            
            logger.info(f"✓ Successfully added comment {result['id']} to {issue_key}")
            return result
            
        except JIRAError as e:
            if e.status_code == 404:
                logger.error(f"Issue {issue_key} not found")
            elif e.status_code == 403:
                logger.error(f"No permission to comment on {issue_key}")
            elif e.status_code == 401:
                logger.error("Authentication failed - token may have expired")
            elif e.status_code == 429:
                logger.warning(f"Rate limited when commenting on {issue_key}")
            else:
                logger.error(f"Failed to add comment to {issue_key}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding comment to {issue_key}: {str(e)}")
            return None
    
    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Get issue details
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            
        Returns:
            Issue details or None if failed
        """
        if not self.client:
            logger.warning("Jira client not initialized")
            return None
        
        try:
            logger.debug(f"Fetching issue {issue_key}")
            issue = self.client.issue(issue_key)
            
            return {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                "created": issue.fields.created
            }
        except JIRAError as e:
            logger.error(f"Failed to get issue {issue_key}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting issue {issue_key}: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if Jira connection is healthy
        
        Returns:
            True if connection is healthy, False otherwise
        """
        if not self.client:
            logger.debug("Jira client not initialized")
            return False
        
        try:
            # Try to get server info
            server_info = self.client.server_info()
            logger.debug(f"Jira health check passed - version: {server_info.get('version')}")
            return True
        except JIRAError as e:
            logger.error(f"Jira health check failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in Jira health check: {str(e)}")
            return False
    
    def is_enabled(self) -> bool:
        """
        Check if Jira integration is enabled and configured
        
        Returns:
            True if enabled and configured, False otherwise
        """
        return self.client is not None
    
    def close(self) -> None:
        """Close Jira client connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("Jira client closed")
            except Exception as e:
                logger.error(f"Error closing Jira client: {str(e)}")
            finally:
                self.client = None

