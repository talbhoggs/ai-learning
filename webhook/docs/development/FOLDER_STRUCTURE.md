# Webhook Project - Recommended Folder Structure

## Current Structure (Basic POC)

```
webhook/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application & routes
│   ├── models.py                # Pydantic models
│   ├── kafka_producer.py        # Kafka producer logic
│   └── config.py                # Configuration settings
├── docker-compose.yml           # Kafka + Zookeeper setup
├── pyproject.toml               # Poetry dependencies
├── requirements.txt             # Pip dependencies (compatibility)
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── .python-version              # Python version
├── README.md                    # Documentation
└── test_payload.json            # Sample Jira payload
```

## Recommended Structure (Production-Ready)

For a more scalable and maintainable application, consider this structure:

```
webhook/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app initialization & startup/shutdown
│   │
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Shared dependencies (DB, Kafka, etc.)
│   │   └── v1/                  # API version 1
│   │       ├── __init__.py
│   │       ├── endpoints/       # Route handlers
│   │       │   ├── __init__.py
│   │       │   ├── webhooks.py  # Jira webhook endpoints
│   │       │   └── health.py    # Health check endpoints
│   │       └── router.py        # API router aggregation
│   │
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── logging.py           # Logging configuration
│   │   └── security.py          # Security utilities (auth, validation)
│   │
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── jira.py              # Jira webhook models
│   │   ├── kafka.py             # Kafka message models
│   │   └── responses.py         # API response models
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── kafka_service.py     # Kafka operations
│   │   ├── webhook_service.py   # Webhook processing logic
│   │   └── validation_service.py # Additional validation logic
│   │
│   ├── schemas/                 # Request/Response schemas
│   │   ├── __init__.py
│   │   ├── webhook.py           # Webhook schemas
│   │   └── health.py            # Health check schemas
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── retry.py             # Retry logic utilities
│       ├── serializers.py       # Custom serializers
│       └── validators.py        # Custom validators
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_kafka_service.py
│   │   └── test_webhook_service.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_kafka_integration.py
│   └── fixtures/                # Test data
│       ├── __init__.py
│       └── jira_payloads.json
│
├── scripts/                     # Utility scripts
│   ├── setup.sh                 # Setup script
│   ├── start_dev.sh             # Development startup
│   └── kafka_consumer.py        # Kafka consumer for testing
│
├── docs/                        # Additional documentation
│   ├── api.md                   # API documentation
│   ├── architecture.md          # Architecture overview
│   └── deployment.md            # Deployment guide
│
├── docker/                      # Docker configurations
│   ├── Dockerfile               # Application Dockerfile
│   ├── Dockerfile.dev           # Development Dockerfile
│   └── docker-compose.yml       # Moved from root
│
├── .github/                     # GitHub specific
│   └── workflows/
│       ├── ci.yml               # CI pipeline
│       └── deploy.yml           # Deployment pipeline
│
├── pyproject.toml               # Poetry configuration
├── poetry.lock                  # Poetry lock file (generated)
├── requirements.txt             # Pip requirements (for compatibility)
├── .env.example                 # Environment variables template
├── .env                         # Local environment (gitignored)
├── .gitignore                   # Git ignore rules
├── .python-version              # Python version
├── README.md                    # Main documentation
├── CHANGELOG.md                 # Version history
└── LICENSE                      # License file
```

## Detailed Breakdown

### 1. **app/api/** - API Layer
Handles HTTP requests and responses. Separates routing logic from business logic.

**Benefits:**
- Clean separation of concerns
- Easy to version APIs (v1, v2, etc.)
- Simplified testing of endpoints

**Example structure:**
```python
# app/api/v1/endpoints/webhooks.py
from fastapi import APIRouter, Depends
from app.services.webhook_service import WebhookService
from app.models.jira import JiraWebhookPayload

router = APIRouter()

@router.post("/jira")
async def receive_jira_webhook(
    payload: JiraWebhookPayload,
    webhook_service: WebhookService = Depends()
):
    return await webhook_service.process_webhook(payload)
```

### 2. **app/core/** - Core Functionality
Contains application-wide configurations, logging, and security.

**Benefits:**
- Centralized configuration management
- Consistent logging across the application
- Reusable security utilities

### 3. **app/models/** - Data Models
Pydantic models for data validation and serialization.

**Benefits:**
- Type safety
- Automatic validation
- Clear data contracts

### 4. **app/services/** - Business Logic
Contains the core business logic, separated from API handlers.

**Benefits:**
- Reusable business logic
- Easier to test
- Can be used by multiple endpoints or background tasks

**Example:**
```python
# app/services/webhook_service.py
class WebhookService:
    def __init__(self, kafka_service: KafkaService):
        self.kafka_service = kafka_service
    
    async def process_webhook(self, payload: JiraWebhookPayload):
        # Business logic here
        message = self._transform_payload(payload)
        await self.kafka_service.publish(message)
        return {"status": "accepted"}
```

### 5. **app/schemas/** - Request/Response Schemas
Defines the shape of API requests and responses.

**Benefits:**
- Clear API contracts
- Automatic OpenAPI documentation
- Validation at API boundary

### 6. **app/utils/** - Utility Functions
Reusable helper functions and utilities.

**Benefits:**
- DRY (Don't Repeat Yourself)
- Easy to test
- Shared across the application

### 7. **tests/** - Test Suite
Comprehensive test coverage with unit and integration tests.

**Structure:**
- `unit/` - Fast, isolated tests
- `integration/` - Tests with external dependencies
- `fixtures/` - Test data and fixtures

### 8. **scripts/** - Utility Scripts
Helper scripts for development and operations.

**Examples:**
- Database migrations
- Data seeding
- Kafka consumer for testing
- Deployment scripts

### 9. **docs/** - Documentation
Additional documentation beyond README.

**Includes:**
- API documentation
- Architecture diagrams
- Deployment guides
- Troubleshooting guides

### 10. **docker/** - Docker Configuration
All Docker-related files in one place.

**Benefits:**
- Clean root directory
- Easy to manage multiple Dockerfiles
- Separate dev and prod configurations

## Migration Path from Current to Recommended

### Phase 1: Reorganize Existing Code
```bash
# Create new directories
mkdir -p app/api/v1/endpoints
mkdir -p app/core
mkdir -p app/services
mkdir -p app/schemas
mkdir -p tests/unit tests/integration

# Move and refactor files
# main.py -> Split into app/main.py and app/api/v1/endpoints/webhooks.py
# models.py -> app/models/jira.py
# kafka_producer.py -> app/services/kafka_service.py
# config.py -> app/core/config.py
```

### Phase 2: Add Testing Infrastructure
```bash
# Create test files
touch tests/conftest.py
touch tests/unit/test_webhook_service.py
touch tests/integration/test_api.py
```

### Phase 3: Add Documentation
```bash
mkdir docs
touch docs/api.md docs/architecture.md
```

### Phase 4: Enhance with Scripts and CI/CD
```bash
mkdir scripts .github/workflows
touch scripts/start_dev.sh
touch .github/workflows/ci.yml
```

## Best Practices

### 1. **Separation of Concerns**
- Keep API handlers thin
- Put business logic in services
- Use models for data validation

### 2. **Dependency Injection**
- Use FastAPI's dependency injection
- Makes testing easier
- Promotes loose coupling

### 3. **Configuration Management**
- Use environment variables
- Separate dev/staging/prod configs
- Never commit secrets

### 4. **Error Handling**
- Create custom exception classes
- Use FastAPI exception handlers
- Log errors appropriately

### 5. **Testing**
- Write tests alongside code
- Aim for high coverage
- Use fixtures for test data

### 6. **Documentation**
- Keep README up to date
- Document API endpoints
- Add inline comments for complex logic

### 7. **Version Control**
- Use meaningful commit messages
- Create feature branches
- Use pull requests for code review

## Example: Refactored Webhook Endpoint

### Current (main.py)
```python
@app.post("/webhook/jira")
async def jira_webhook(payload: JiraWebhookPayload):
    # All logic in one place
    if not kafka_producer.is_connected():
        kafka_producer.reconnect()
    
    message = payload.model_dump()
    success = kafka_producer.send_message(
        topic=settings.kafka_topic,
        message=message,
        key=payload.issue.key
    )
    
    if not success:
        raise HTTPException(status_code=500)
    
    return {"status": "accepted"}
```

### Recommended (Separated)
```python
# app/api/v1/endpoints/webhooks.py
@router.post("/jira")
async def jira_webhook(
    payload: JiraWebhookPayload,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    result = await webhook_service.process_jira_webhook(payload)
    return result

# app/services/webhook_service.py
class WebhookService:
    def __init__(self, kafka_service: KafkaService):
        self.kafka_service = kafka_service
    
    async def process_jira_webhook(
        self, 
        payload: JiraWebhookPayload
    ) -> WebhookResponse:
        logger.info(f"Processing webhook: {payload.webhookEvent}")
        
        # Transform payload
        message = self._transform_to_kafka_message(payload)
        
        # Publish to Kafka
        await self.kafka_service.publish(
            topic="jira-events",
            message=message,
            key=payload.issue.key
        )
        
        return WebhookResponse(
            status="accepted",
            issue_key=payload.issue.key,
            webhook_event=payload.webhookEvent
        )
```

## Conclusion

The recommended structure provides:
- ✅ Better organization and maintainability
- ✅ Easier testing and debugging
- ✅ Scalability for future features
- ✅ Clear separation of concerns
- ✅ Professional project structure

Start with the current simple structure for POC, then gradually migrate to the recommended structure as the project grows.