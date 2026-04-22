"""Pydantic models for Jira webhook payload validation"""
from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """Jira user model"""
    self: str
    name: str
    displayName: str
    emailAddress: Optional[str] = None


class IssueType(BaseModel):
    """Jira issue type model"""
    id: str
    name: str


class Project(BaseModel):
    """Jira project model"""
    id: str
    key: str
    name: str


class Reporter(BaseModel):
    """Jira reporter/creator model"""
    name: str
    displayName: str


class Priority(BaseModel):
    """Jira priority model"""
    id: str
    name: str


class Status(BaseModel):
    """Jira status model"""
    id: str
    name: str


class IssueFields(BaseModel):
    """Jira issue fields model"""
    summary: str
    description: Optional[str] = None
    issuetype: IssueType
    project: Project
    reporter: Reporter
    creator: Reporter
    priority: Priority
    status: Status


class Issue(BaseModel):
    """Jira issue model"""
    id: str
    self: str
    key: str
    fields: IssueFields


class JiraWebhookPayload(BaseModel):
    """Complete Jira webhook payload model"""
    timestamp: int
    webhookEvent: str
    user: User
    issue: Issue

    class Config:
        json_schema_extra = {
            "example": {
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
        }

# Made with Bob
