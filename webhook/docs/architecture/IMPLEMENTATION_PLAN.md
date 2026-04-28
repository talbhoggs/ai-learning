# Jira-LangGraph Consumer - Implementation Plan

## Overview

This document provides a detailed, step-by-step implementation plan for building the Kafka consumer service that processes Jira events and forwards them to a LangGraph orchestrator.

**Project Name**: `jira-consumer`  
**Location**: `ai-learning/jira-consumer/`  
**Approach**: Separate independent service (Option 1)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Project Setup](#phase-1-project-setup-day-1-2)
3. [Phase 2: Core Consumer Implementation](#phase-2-core-consumer-implementation-day-3-5)
4. [Phase 3: LangGraph Integration](#phase-3-langgraph-integration-day-6-8)
5. [Phase 4: Reliability & Error Handling](#phase-4-reliability--error-handling-day-9-11)
6. [Phase 5: Observability](#phase-5-observability-day-12-14)
7. [Phase 6: Testing & Documentation](#phase-6-testing--documentation-day-15-17)
8. [Phase 7: Production Deployment](#phase-7-production-deployment-day-18-20)

---

## Prerequisites

### Required Tools
- ✅ Python 3.12+
- ✅ Poetry (dependency management)
- ✅ Docker & Docker Compose
- ✅ Git
- ✅ Access to existing Kafka cluster (from webhook project)

### Required Access
- ✅ LangGraph API endpoint URL
- ✅ LangGraph API authentication credentials
- ✅ Kafka broker access (localhost:9092 for development)

### Knowledge Requirements
- Python async programming
- Kafka consumer concepts
- REST API integration
- Docker basics

---

## Phase 1: Project Setup (Day 1-2)

### Milestone: Project scaffolding complete with basic structure

### Step 1.1: Create Project Directory

```bash
cd ~/dev/java/ai-learning
mkdir jira-consumer
cd jira-consumer
```

### Step 1.2: Initialize Git Repository

```bash
git init
git branch -M main
```

### Step 1.3: Create Project Structure

```bash
# Create directory structure
mkdir -p app/{consumers,transformers,clients,models,services,core}
mkdir -p tests/{unit,integration}
mkdir -p docs

# Create __init__.py files
touch app/__init__.py
touch app/consumers/__init__.py
touch app/transformers/__init__.py
touch app/clients/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/core/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

**Expected Structure**:
```
jira-consumer/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── jira_consumer.py       # Kafka consumer
│   ├── transformers/
│   │   ├── __init__.py
│   │   └── jira_transformer.py    # Event transformation
│   ├── clients/
│   │   ├── __init__.py
│   │   └── langgraph_client.py    # LangGraph API client
│   ├── models/
│   │   ├── __init__.py
│   │   ├── jira_event.py          # Input models
│   │   └── langgraph_request.py   # Output models
│   ├── services/
│   │   ├── __init__.py
│   │   └── processor_service.py   # Main processing logic
│   └── core/
│       ├── __init__.py
│       ├── config.py               # Configuration
│       └── logging.py              # Logging setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_transformer.py
│   │   └── test_consumer.py
│   └── integration/
│       ├── __init__.py
│       └── test_end_to_end.py
├── docs/
│   └── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Step 1.4: Initialize Poetry

```bash
poetry init --name jira-consumer \
           --description "Kafka consumer for Jira events to LangGraph" \
           --author "Your Name <your.email@example.com>" \
           --python "^3.12" \
           --no-interaction
```

### Step 1.5: Add Core Dependencies

```bash
# Core dependencies
poetry add kafka-python
poetry add pydantic
poetry add pydantic-settings
poetry add httpx
poetry add tenacity
poetry add python-dotenv

# Development dependencies
poetry add --group dev pytest
poetry add --group dev pytest-asyncio
poetry add --group dev pytest-cov
poetry add --group dev black
poetry add --group dev flake8
poetry add --group dev mypy
```

### Step 1.6: Create Configuration Files

**`.env.example`**:
```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=jira-events
KAFKA_GROUP_ID=jira-consumer-group
KAFKA_AUTO_OFFSET_RESET=earliest

# LangGraph Configuration
LANGGRAPH_API_URL=https://your-langgraph-api.com
LANGGRAPH_API_KEY=your-api-key-here

# Processing Configuration
BATCH_SIZE=10
MAX_RETRIES=3
RETRY_BACKOFF_MS=1000

# Dead Letter Queue
DLQ_TOPIC=jira-events-dlq

# Logging
LOG_LEVEL=INFO
```

**`.gitignore`**:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Poetry
poetry.lock

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

### Step 1.7: Create README.md

```markdown
# Jira-LangGraph Consumer

Kafka consumer service that processes Jira webhook events and forwards them to a LangGraph orchestrator for AI-powered processing.

## Architecture

```
Jira → Webhook Producer → Kafka (jira-events) → Consumer → LangGraph Orchestrator
```

## Quick Start

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start Kafka (if not running):
   ```bash
   cd ../webhook
   docker-compose up -d
   ```

4. Run consumer:
   ```bash
   poetry run python -m app.main
   ```

## Development

See [docs/README.md](docs/README.md) for detailed documentation.
```

### Step 1.8: Verify Setup

```bash
# Check Poetry installation
poetry check

# Verify dependencies
poetry show

# Run initial test (should pass with no tests)
poetry run pytest
```

**✅ Checkpoint**: Project structure created, dependencies installed, configuration files in place.

---

## Phase 2: Core Consumer Implementation (Day 3-5)

### Milestone: Basic Kafka consumer working and consuming messages

### Step 2.1: Implement Configuration (`app/core/config.py`)

```python
"""Configuration settings for the consumer service"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Kafka Configuration
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "jira-events")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "jira-consumer-group")
    kafka_auto_offset_reset: str = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")
    
    # LangGraph Configuration
    langgraph_api_url: str = os.getenv("LANGGRAPH_API_URL", "")
    langgraph_api_key: str = os.getenv("LANGGRAPH_API_KEY", "")
    
    # Processing Configuration
    batch_size: int = int(os.getenv("BATCH_SIZE", "10"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    retry_backoff_ms: int = int(os.getenv("RETRY_BACKOFF_MS", "1000"))
    
    # Dead Letter Queue
    dlq_topic: str = os.getenv("DLQ_TOPIC", "jira-events-dlq")
    
    # Application Configuration
    app_name: str = "Jira-LangGraph Consumer"
    app_version: str = "1.0.0"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
```

### Step 2.2: Implement Logging (`app/core/logging.py`)

```python
"""Logging configuration"""
import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
```

### Step 2.3: Create Data Models (`app/models/jira_event.py`)

```python
"""Pydantic models for Jira events"""
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    """Jira user model"""
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
    priority: Priority
    status: Status


class Issue(BaseModel):
    """Jira issue model"""
    id: str
    key: str
    fields: IssueFields


class JiraEvent(BaseModel):
    """Complete Jira event model"""
    timestamp: int
    webhookEvent: str
    user: User
    issue: Issue
```

### Step 2.4: Implement Kafka Consumer (`app/consumers/jira_consumer.py`)

```python
"""Kafka consumer for Jira events"""
import json
from typing import Callable, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class JiraEventConsumer:
    """Kafka consumer for Jira events"""
    
    def __init__(self):
        """Initialize Kafka consumer"""
        self.consumer: Optional[KafkaConsumer] = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Kafka"""
        try:
            logger.info(f"Connecting to Kafka at {settings.kafka_bootstrap_servers}")
            self.consumer = KafkaConsumer(
                settings.kafka_topic,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                group_id=settings.kafka_group_id,
                auto_offset_reset=settings.kafka_auto_offset_reset,
                enable_auto_commit=False,  # Manual commit for reliability
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000  # Timeout for graceful shutdown
            )
            logger.info(f"Successfully connected to Kafka topic: {settings.kafka_topic}")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            raise
    
    def consume(self, processor_callback: Callable) -> None:
        """
        Consume messages and process with callback
        
        Args:
            processor_callback: Function to process each message
        """
        if not self.consumer:
            raise RuntimeError("Consumer not initialized")
        
        logger.info("Starting message consumption...")
        
        try:
            for message in self.consumer:
                try:
                    logger.debug(f"Received message from partition {message.partition}, offset {message.offset}")
                    
                    # Process message
                    processor_callback(message.value)
                    
                    # Commit offset after successful processing
                    self.consumer.commit()
                    logger.debug(f"Committed offset {message.offset}")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}", exc_info=True)
                    # Don't commit offset on error - message will be reprocessed
                    
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.close()
    
    def close(self) -> None:
        """Close consumer connection"""
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("Kafka consumer closed successfully")
            except Exception as e:
                logger.error(f"Error closing consumer: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if consumer is connected"""
        return self.consumer is not None
```

### Step 2.5: Create Main Entry Point (`app/main.py`)

```python
"""Main entry point for the consumer service"""
import signal
import sys

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.consumers.jira_consumer import JiraEventConsumer

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Global consumer instance for graceful shutdown
consumer_instance = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if consumer_instance:
        consumer_instance.close()
    sys.exit(0)


def process_message(message: dict) -> None:
    """
    Process a single message
    
    Args:
        message: Deserialized message from Kafka
    """
    logger.info(f"Processing message: {message.get('webhookEvent')} for issue {message.get('issue', {}).get('key')}")
    # TODO: Add transformation and forwarding logic
    logger.debug(f"Message content: {message}")


def main():
    """Main function"""
    global consumer_instance
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Kafka broker: {settings.kafka_bootstrap_servers}")
    logger.info(f"Kafka topic: {settings.kafka_topic}")
    logger.info(f"Consumer group: {settings.kafka_group_id}")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start consumer
        consumer_instance = JiraEventConsumer()
        consumer_instance.consume(process_message)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Step 2.6: Test Basic Consumer

```bash
# Ensure Kafka is running
cd ../webhook
docker-compose up -d

# Start consumer
cd ../jira-consumer
poetry run python -m app.main
```

**Expected Output**:
```
2024-04-28 10:00:00 - app.main - INFO - Starting Jira-LangGraph Consumer v1.0.0
2024-04-28 10:00:00 - app.main - INFO - Kafka broker: localhost:9092
2024-04-28 10:00:00 - app.main - INFO - Kafka topic: jira-events
2024-04-28 10:00:00 - app.consumers.jira_consumer - INFO - Connecting to Kafka...
2024-04-28 10:00:01 - app.consumers.jira_consumer - INFO - Successfully connected to Kafka topic: jira-events
2024-04-28 10:00:01 - app.consumers.jira_consumer - INFO - Starting message consumption...
```

### Step 2.7: Test with Sample Message

In another terminal, send a test message:

```bash
cd ../webhook
curl -X POST http://localhost:8000/webhook/jira \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

**Expected Consumer Output**:
```
2024-04-28 10:01:00 - app.main - INFO - Processing message: jira:issue_created for issue PROJ-123
```

**✅ Checkpoint**: Consumer successfully connects to Kafka and processes messages.

---

## Phase 3: LangGraph Integration (Day 6-8)

### Milestone: Consumer transforms events and forwards to LangGraph

### Step 3.1: Create LangGraph Request Model (`app/models/langgraph_request.py`)

```python
"""Pydantic models for LangGraph requests"""
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LangGraphContext(BaseModel):
    """Context data for LangGraph"""
    summary: str
    description: Optional[str] = None
    priority: str
    status: str
    issue_type: str
    project_key: str
    project_name: str


class LangGraphMetadata(BaseModel):
    """Metadata for LangGraph request"""
    source: str = "jira"
    timestamp: int
    user: str
    issue_id: str


class LangGraphRequest(BaseModel):
    """Complete LangGraph request"""
    event_type: str
    issue_key: str
    context: LangGraphContext
    metadata: LangGraphMetadata
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "jira_issue_created",
                "issue_key": "PROJ-123",
                "context": {
                    "summary": "API returns 500 on login",
                    "description": "Steps to reproduce...",
                    "priority": "High",
                    "status": "To Do",
                    "issue_type": "Bug",
                    "project_key": "PROJ",
                    "project_name": "Project Alpha"
                },
                "metadata": {
                    "source": "jira",
                    "timestamp": 1713782400000,
                    "user": "Charles D",
                    "issue_id": "10001"
                }
            }
        }
```

### Step 3.2: Implement Transformer (`app/transformers/jira_transformer.py`)

```python
"""Transform Jira events to LangGraph format"""
from app.models.jira_event import JiraEvent
from app.models.langgraph_request import (
    LangGraphRequest,
    LangGraphContext,
    LangGraphMetadata
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class JiraEventTransformer:
    """Transform Jira events to LangGraph requests"""
    
    EVENT_TYPE_MAPPING = {
        "jira:issue_created": "jira_issue_created",
        "jira:issue_updated": "jira_issue_updated",
        "jira:issue_deleted": "jira_issue_deleted",
    }
    
    def transform(self, jira_event: JiraEvent) -> LangGraphRequest:
        """
        Transform Jira event to LangGraph request
        
        Args:
            jira_event: Validated Jira event
            
        Returns:
            LangGraph request ready to send
        """
        logger.debug(f"Transforming event: {jira_event.webhookEvent}")
        
        # Map event type
        event_type = self.EVENT_TYPE_MAPPING.get(
            jira_event.webhookEvent,
            "jira_unknown_event"
        )
        
        # Build context
        context = LangGraphContext(
            summary=jira_event.issue.fields.summary,
            description=jira_event.issue.fields.description,
            priority=jira_event.issue.fields.priority.name,
            status=jira_event.issue.fields.status.name,
            issue_type=jira_event.issue.fields.issuetype.name,
            project_key=jira_event.issue.fields.project.key,
            project_name=jira_event.issue.fields.project.name
        )
        
        # Build metadata
        metadata = LangGraphMetadata(
            timestamp=jira_event.timestamp,
            user=jira_event.user.displayName,
            issue_id=jira_event.issue.id
        )
        
        # Create request
        request = LangGraphRequest(
            event_type=event_type,
            issue_key=jira_event.issue.key,
            context=context,
            metadata=metadata
        )
        
        logger.info(f"Transformed {jira_event.webhookEvent} to {event_type} for issue {jira_event.issue.key}")
        return request
```

### Step 3.3: Implement LangGraph Client (`app/clients/langgraph_client.py`)

```python
"""HTTP client for LangGraph API"""
import httpx
from typing import Dict, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.core.config import settings
from app.core.logging import get_logger
from app.models.langgraph_request import LangGraphRequest

logger = get_logger(__name__)


class LangGraphClient:
    """Client for LangGraph API"""
    
    def __init__(self):
        """Initialize LangGraph client"""
        self.base_url = settings.langgraph_api_url
        self.api_key = settings.langgraph_api_key
        
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        logger.info(f"LangGraph client initialized for {self.base_url}")
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def send_event(self, request: LangGraphRequest) -> Dict[str, Any]:
        """
        Send event to LangGraph orchestrator
        
        Args:
            request: LangGraph request to send
            
        Returns:
            Response from LangGraph API
            
        Raises:
            httpx.HTTPError: If request fails
        """
        logger.info(f"Sending event to LangGraph: {request.event_type} for {request.issue_key}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/orchestrate",
                json=request.model_dump()
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully sent event to LangGraph: {request.issue_key}")
            logger.debug(f"LangGraph response: {result}")
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"LangGraph API error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException as e:
            logger.warning(f"LangGraph API timeout: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling LangGraph: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if LangGraph API is reachable
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"LangGraph health check failed: {str(e)}")
            return False
    
    async def close(self) -> None:
        """Close HTTP client"""
        await self.client.aclose()
        logger.info("LangGraph client closed")
```

### Step 3.4: Implement Processor Service (`app/services/processor_service.py`)

```python
"""Main processing service"""
import asyncio
from typing import Dict, Any

from app.models.jira_event import JiraEvent
from app.transformers.jira_transformer import JiraEventTransformer
from app.clients.langgraph_client import LangGraphClient
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProcessorService:
    """Service to process Jira events and forward to LangGraph"""
    
    def __init__(self):
        """Initialize processor service"""
        self.transformer = JiraEventTransformer()
        self.langgraph_client = LangGraphClient()
        logger.info("Processor service initialized")
    
    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a single Jira event
        
        Args:
            event_data: Raw event data from Kafka
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Validate and parse event
            jira_event = JiraEvent(**event_data)
            logger.info(f"Processing event: {jira_event.webhookEvent} for issue {jira_event.issue.key}")
            
            # Transform to LangGraph format
            langgraph_request = self.transformer.transform(jira_event)
            
            # Send to LangGraph
            response = await self.langgraph_client.send_event(langgraph_request)
            
            logger.info(f"Successfully processed event for issue {jira_event.issue.key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process event: {str(e)}", exc_info=True)
            return False
    
    async def close(self) -> None:
        """Cleanup resources"""
        await self.langgraph_client.close()
        logger.info("Processor service closed")
```

### Step 3.5: Update Main Entry Point

Update `app/main.py` to use the processor service:

```python
"""Main entry point for the consumer service"""
import signal
import sys
import asyncio

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.consumers.jira_consumer import JiraEventConsumer
from app.services.processor_service import ProcessorService

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Global instances for graceful shutdown
consumer_instance = None
processor_instance = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if consumer_instance:
        consumer_instance.close()
    if processor_instance:
        asyncio.run(processor_instance.close())
    sys.exit(0)


def process_message(message: dict) -> None:
    """
    Process a single message
    
    Args:
        message: Deserialized message from Kafka
    """
    try:
        # Process event asynchronously
        success = asyncio.run(processor_instance.process_event(message))
        
        if not success:
            logger.error(f"Failed to process message for issue {message.get('issue', {}).get('key')}")
            # TODO: Send to DLQ
            
    except Exception as e:
        logger.error(f"Error in message processing: {str(e)}", exc_info=True)


def main():
    """Main function"""
    global consumer_instance, processor_instance
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Kafka broker: {settings.kafka_bootstrap_servers}")
    logger.info(f"Kafka topic: {settings.kafka_topic}")
    logger.info(f"LangGraph API: {settings.langgraph_api_url}")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize processor service
        processor_instance = ProcessorService()
        
        # Create and start consumer
        consumer_instance = JiraEventConsumer()
        consumer_instance.consume(process_message)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Step 3.6: Test LangGraph Integration

```bash
# Update .env with LangGraph credentials
LANGGRAPH_API_URL=https://your-langgraph-api.com
LANGGRAPH_API_KEY=your-api-key

# Start consumer
poetry run python -m app.main

# In another terminal, send test message
cd ../webhook
curl -X POST http://localhost:8000/webhook/jira \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

**Expected Output**:
```
INFO - Processing event: jira:issue_created for issue PROJ-123
INFO - Transformed jira:issue_created to jira_issue_created for issue PROJ-123
INFO - Sending event to LangGraph: jira_issue_created for PROJ-123
INFO - Successfully sent event to LangGraph: PROJ-123
INFO - Successfully processed event for issue PROJ-123
```

**✅ Checkpoint**: Consumer transforms events and successfully forwards to LangGraph.

---

## Phase 4: Reliability & Error Handling (Day 9-11)

### Milestone: Robust error handling with DLQ and retry logic

### Step 4.1: Implement Dead Letter Queue Producer

Create `app/services/dlq_service.py`:

```python
"""Dead Letter Queue service"""
import json
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DLQService:
    """Service for publishing failed messages to Dead Letter Queue"""
    
    def __init__(self):
        """Initialize DLQ producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info(f"DLQ producer initialized for topic: {settings.dlq_topic}")
        except KafkaError as e:
            logger.error(f"Failed to initialize DLQ producer: {str(e)}")
            raise
    
    def send_to_dlq(self, message: Dict[str, Any], error: str, issue_key: str = None) -> bool:
        """
        Send failed message to DLQ
        
        Args:
            message: Original message that failed
            error: Error description
            issue_key: Optional issue key for partitioning
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            dlq_message = {
                "original_message": message,
                "error": error,
                "timestamp": message.get("timestamp"),
                "issue_key": issue_key or message.get("issue", {}).get("key")
            }
            
            future = self.producer.send(
                settings.dlq_topic,
                value=dlq_message,
                key=issue_key
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            logger.warning(
                f"Message sent to DLQ: {issue_key} "
                f"[partition: {record_metadata.partition}, offset: {record_metadata.offset}]"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close DLQ producer"""
        if self.producer:
            try:
                self.producer.flush()
                self.producer.close()
                logger.info("DLQ producer closed")
            except Exception as e:
                logger.error(f"Error closing DLQ producer: {str(e)}")
```

### Step 4.2: Add Circuit Breaker

Create `app/core/circuit_breaker.py`:

```python
"""Circuit breaker implementation"""
import time
from enum import Enum
from typing import Callable, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        name: str = "circuit_breaker"
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (half-open)
            name: Name for logging
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
        logger.info(f"Circuit breaker '{name}' initialized")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.timeout
        )
    
    def _on_success(self) -> None:
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit breaker '{self.name}' closing after successful test")
            self.state = CircuitState.CLOSED
        
        self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker '{self.name}' opened after "
                f"{self.failure_count} failures"
            )
```

### Step 4.3: Update Processor Service with Error Handling

Update `app/services/processor_service.py`:

```python
"""Main processing service with error handling"""
import asyncio
from typing import Dict, Any

from app.models.jira_event import JiraEvent
from app.transformers.jira_transformer import JiraEventTransformer
from app.clients.langgraph_client import LangGraphClient
from app.services.dlq_service import DLQService
from app.core.circuit_breaker import CircuitBreaker
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProcessorService:
    """Service to process Jira events with error handling"""
    
    def __init__(self):
        """Initialize processor service"""
        self.transformer = JiraEventTransformer()
        self.langgraph_client = LangGraphClient()
        self.dlq_service = DLQService()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            name="langgraph_api"
        )
        logger.info("Processor service initialized with error handling")
    
    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a single Jira event with error handling
        
        Args:
            event_data: Raw event data from Kafka
            
        Returns:
            True if processed successfully, False otherwise
        """
        issue_key = None
        
        try:
            # Validate and parse event
            jira_event = JiraEvent(**event_data)
            issue_key = jira_event.issue.key
            
            logger.info(f"Processing event: {jira_event.webhookEvent} for issue {issue_key}")
            
            # Transform to LangGraph format
            langgraph_request = self.transformer.transform(jira_event)
            
            # Send to LangGraph with circuit breaker
            try:
                response = await self.circuit_breaker.call(
                    self.langgraph_client.send_event,
                    langgraph_request
                )
                
                logger.info(f"Successfully processed event for issue {issue_key}")
                return True
                
            except Exception as e:
                logger.error(f"LangGraph API call failed for {issue_key}: {str(e)}")
                
                # Send to DLQ
                self.dlq_service.send_to_dlq(
                    event_data,
                    f"LangGraph API error: {str(e)}",
                    issue_key
                )
                return False
        
        except Exception as e:
            logger.error(f"Failed to process event: {str(e)}", exc_info=True)
            
            # Send to DLQ
            self.dlq_service.send_to_dlq(
                event_data,
                f"Processing error: {str(e)}",
                issue_key
            )
            return False
    
    async def close(self) -> None:
        """Cleanup resources"""
        await self.langgraph_client.close()
        self.dlq_service.close()
        logger.info("Processor service closed")
```

### Step 4.4: Test Error Handling

```bash
# Test with invalid LangGraph URL to trigger errors
LANGGRAPH_API_URL=http://invalid-url.com

# Start consumer
poetry run python -m app.main

# Send test messages - should go to DLQ
cd ../webhook
for i in {1..10}; do
  curl -X POST http://localhost:8000/webhook/jira \
    -H "Content-Type: application/json" \
    -d @test_payload.json
  sleep 1
done
```

**Expected Behavior**:
- First 5 messages: Retry attempts
- After 5 failures: Circuit breaker opens
- All failed messages: Sent to DLQ topic

**Verify DLQ**:
```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic jira-events-dlq \
  --from-beginning
```

**✅ Checkpoint**: Error handling working with DLQ and circuit breaker.

---

## Phase 5: Observability (Day 12-14)

### Milestone: Metrics, monitoring, and health checks implemented

### Step 5.1: Add Prometheus Metrics

Add dependency:
```bash
poetry add prometheus-client
```

Create `app/core/metrics.py`:

```python
"""Prometheus metrics"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server

from app.core.logging import get_logger

logger = get_logger(__name__)

# Counters
messages_consumed_total = Counter(
    'messages_consumed_total',
    'Total number of messages consumed from Kafka'
)

messages_processed_success = Counter(
    'messages_processed_success',
    'Number of messages processed successfully'
)

messages_failed_total = Counter(
    'messages_failed_total',
    'Number of messages that failed processing',
    ['error_type']
)

messages_sent_to_dlq = Counter(
    'messages_sent_to_dlq',
    'Number of messages sent to dead letter queue'
)

# Histograms
processing_duration_seconds = Histogram(
    'processing_duration_seconds',
    'Time spent processing messages',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

langgraph_api_latency_seconds = Histogram(
    'langgraph_api_latency_seconds',
    'LangGraph API call latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Gauges
consumer_lag = Gauge(
    'consumer_lag',
    'Current consumer lag'
)

circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half_open, 2=open)',
    ['name']
)


def start_metrics_server(port: int = 9090) -> None:
    """Start Prometheus metrics HTTP server"""
    try:
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {str(e)}")
```

### Step 5.2: Add Health Check Endpoint

Create `app/api/health.py`:

```python
"""Health check API"""
from fastapi import FastAPI
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    kafka_connected: bool
    langgraph_reachable: bool
    consumer_lag: int


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # TODO: Implement actual health checks
    return HealthResponse(
        status="healthy",
        kafka_connected=True,
        langgraph_reachable=True,
        consumer_lag=0
    )


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {"status": "ready"}


@app.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {"status": "alive"}
```

### Step 5.3: Update Processor with Metrics

Update `app/services/processor_service.py` to include metrics:

```python
import time
from app.core import metrics

# In process_event method:
async def process_event(self, event_data: Dict[str, Any]) -> bool:
    start_time = time.time()
    metrics.messages_consumed_total.inc()
    
    try:
        # ... existing processing code ...
        
        # Record success
        metrics.messages_processed_success.inc()
        duration = time.time() - start_time
        metrics.processing_duration_seconds.observe(duration)
        
        return True
        
    except Exception as e:
        # Record failure
        metrics.messages_failed_total.labels(error_type=type(e).__name__).inc()
        duration = time.time() - start_time
        metrics.processing_duration_seconds.observe(duration)
        
        return False
```

### Step 5.4: Update Main to Start Metrics Server

Update `app/main.py`:

```python
from app.core.metrics import start_metrics_server

def main():
    # ... existing code ...
    
    # Start metrics server
    start_metrics_server(port=9090)
    
    # ... rest of code ...
```

### Step 5.5: Create Grafana Dashboard Config

Create `docs/grafana-dashboard.json`:

```json
{
  "dashboard": {
    "title": "Jira-LangGraph Consumer",
    "panels": [
      {
        "title": "Messages Processed",
        "targets": [
          {
            "expr": "rate(messages_processed_success[5m])"
          }
        ]
      },
      {
        "title": "Processing Duration",
