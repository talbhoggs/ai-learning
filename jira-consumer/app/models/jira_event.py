"""Pydantic models for Jira webhook events"""
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    """Jira user model"""
    accountId: str
    displayName: str
    active: bool
    timeZone: str
    accountType: str


class IssueType(BaseModel):
    """Jira issue type model"""
    id: str
    name: str
    description: Optional[str] = None


class Project(BaseModel):
    """Jira project model"""
    id: str
    key: str
    name: str


class Assignee(BaseModel):
    """Jira assignee model"""
    accountId: str
    displayName: str


class Priority(BaseModel):
    """Jira priority model"""
    id: str
    name: str


class Status(BaseModel):
    """Jira status model"""
    id: str
    name: str
    description: Optional[str] = None


class Comment(BaseModel):
    """Jira comment model"""
    id: str
    body: str
    author: User
    updateAuthor: User
    created: str
    updated: str
    jsdPublic: bool


class IssueFields(BaseModel):
    """Jira issue fields model"""
    summary: str
    issuetype: IssueType
    project: Project
    assignee: Optional[Assignee] = None
    priority: Priority
    status: Status


class Issue(BaseModel):
    """Jira issue model"""
    id: str
    key: str
    fields: IssueFields


class JiraEvent(BaseModel):
    """Complete Jira webhook event model"""
    timestamp: int
    webhookEvent: str
    comment: Optional[Comment] = None
    issue: Issue
    eventType: Optional[str] = None
    
    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "timestamp": 1777011862928,
                "webhookEvent": "comment_created",
                "issue": {
                    "id": "10000",
                    "key": "SCRUM-1",
                    "fields": {
                        "summary": "Http issue with server",
                        "issuetype": {
                            "id": "10003",
                            "name": "Task"
                        },
                        "project": {
                            "id": "10000",
                            "key": "SCRUM",
                            "name": "My Scrum Project"
                        },
                        "priority": {
                            "id": "3",
                            "name": "Medium"
                        },
                        "status": {
                            "id": "10001",
                            "name": "In Progress"
                        }
                    }
                }
            }
        }

# Made with Bob
