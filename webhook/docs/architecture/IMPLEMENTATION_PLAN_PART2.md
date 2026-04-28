# Jira-LangGraph Consumer - Implementation Plan (Part 2)

## Phase 5: Observability (Continued)

### Step 5.6: Add Structured Logging

Update `app/core/logging.py` to add structured logging:

```python
"""Enhanced logging configuration with structured logging"""
import logging
import sys
import json
from datetime import datetime
from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'issue_key'):
            log_data["issue_key"] = record.issue_key
        if hasattr(record, 'event_type'):
            log_data["event_type"] = record.event_type
        
        return json.dumps(log_data)


def setup_logging() -> None:
    """Configure application logging with structured format"""
    
    # Use structured logging in production
    if settings.log_level == "DEBUG":
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = StructuredFormatter()
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        handlers=[handler]
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
```

**✅ Checkpoint**: Observability features implemented with metrics and structured logging.

---

## Phase 6: Testing & Documentation (Day 15-17)

### Milestone: Comprehensive test coverage and documentation

### Step 6.1: Create Unit Tests

**`tests/unit/test_transformer.py`**:

```python
"""Unit tests for Jira transformer"""
import pytest
from app.transformers.jira_transformer import JiraEventTransformer
from app.models.jira_event import JiraEvent


@pytest.fixture
def sample_jira_event():
    """Sample Jira event for testing"""
    return {
        "timestamp": 1713782400000,
        "webhookEvent": "jira:issue_created",
        "user": {
            "name": "charles",
            "displayName": "Charles D",
            "emailAddress": "charles@example.com"
        },
        "issue": {
            "id": "10001",
            "key": "PROJ-123",
            "fields": {
                "summary": "Test issue",
                "description": "Test description",
                "issuetype": {"id": "1", "name": "Bug"},
                "project": {"id": "10", "key": "PROJ", "name": "Test Project"},
                "priority": {"id": "3", "name": "High"},
                "status": {"id": "1", "name": "To Do"}
            }
        }
    }


def test_transform_issue_created(sample_jira_event):
    """Test transformation of issue created event"""
    transformer = JiraEventTransformer()
    jira_event = JiraEvent(**sample_jira_event)
    
    result = transformer.transform(jira_event)
    
    assert result.event_type == "jira_issue_created"
    assert result.issue_key == "PROJ-123"
    assert result.context.summary == "Test issue"
    assert result.context.priority == "High"
    assert result.metadata.user == "Charles D"


def test_transform_unknown_event(sample_jira_event):
    """Test transformation of unknown event type"""
    sample_jira_event["webhookEvent"] = "jira:unknown_event"
    transformer = JiraEventTransformer()
    jira_event = JiraEvent(**sample_jira_event)
    
    result = transformer.transform(jira_event)
    
    assert result.event_type == "jira_unknown_event"
```

**`tests/unit/test_circuit_breaker.py`**:

```python
"""Unit tests for circuit breaker"""
import pytest
import time
from app.core.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_closed_state():
    """Test circuit breaker in closed state"""
    cb = CircuitBreaker(failure_threshold=3, timeout=1)
    
    def success_func():
        return "success"
    
    result = cb.call(success_func)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_opens_after_failures():
    """Test circuit breaker opens after threshold failures"""
    cb = CircuitBreaker(failure_threshold=3, timeout=1)
    
    def failing_func():
        raise Exception("Test error")
    
    # Trigger failures
    for _ in range(3):
        with pytest.raises(Exception):
            cb.call(failing_func)
    
    assert cb.state == CircuitState.OPEN


def test_circuit_breaker_half_open_after_timeout():
    """Test circuit breaker enters half-open state after timeout"""
    cb = CircuitBreaker(failure_threshold=2, timeout=1)
    
    def failing_func():
        raise Exception("Test error")
    
    # Open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            cb.call(failing_func)
    
    assert cb.state == CircuitState.OPEN
    
    # Wait for timeout
    time.sleep(1.1)
    
    # Next call should attempt (half-open)
    with pytest.raises(Exception):
        cb.call(failing_func)
    
    # Should be back to open after failure in half-open
    assert cb.state == CircuitState.OPEN
```

### Step 6.2: Create Integration Tests

**`tests/integration/test_end_to_end.py`**:

```python
"""Integration tests for end-to-end flow"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.processor_service import ProcessorService


@pytest.fixture
def sample_kafka_message():
    """Sample Kafka message"""
    return {
        "timestamp": 1713782400000,
        "webhookEvent": "jira:issue_created",
        "user": {
            "name": "charles",
            "displayName": "Charles D"
        },
        "issue": {
            "id": "10001",
            "key": "PROJ-123",
            "fields": {
                "summary": "Test issue",
                "description": "Test description",
                "issuetype": {"id": "1", "name": "Bug"},
                "project": {"id": "10", "key": "PROJ", "name": "Test Project"},
                "priority": {"id": "3", "name": "High"},
                "status": {"id": "1", "name": "To Do"}
            }
        }
    }


@pytest.mark.asyncio
async def test_successful_processing(sample_kafka_message):
    """Test successful message processing"""
    processor = ProcessorService()
    
    # Mock LangGraph client
    with patch.object(
        processor.langgraph_client,
        'send_event',
        new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = {"status": "success"}
        
        result = await processor.process_event(sample_kafka_message)
        
        assert result is True
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_failed_processing_sends_to_dlq(sample_kafka_message):
    """Test failed processing sends message to DLQ"""
    processor = ProcessorService()
    
    # Mock LangGraph client to fail
    with patch.object(
        processor.langgraph_client,
        'send_event',
        new_callable=AsyncMock
    ) as mock_send:
        mock_send.side_effect = Exception("API Error")
        
        # Mock DLQ service
        with patch.object(processor.dlq_service, 'send_to_dlq') as mock_dlq:
            mock_dlq.return_value = True
            
            result = await processor.process_event(sample_kafka_message)
            
            assert result is False
            mock_dlq.assert_called_once()
```

### Step 6.3: Create Test Configuration

**`tests/conftest.py`**:

```python
"""Pytest configuration and fixtures"""
import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"
    os.environ["KAFKA_TOPIC"] = "test-jira-events"
    os.environ["LANGGRAPH_API_URL"] = "http://test-api.com"
    os.environ["LANGGRAPH_API_KEY"] = "test-key"
    os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture
def mock_kafka_consumer(mocker):
    """Mock Kafka consumer"""
    return mocker.patch('app.consumers.jira_consumer.KafkaConsumer')


@pytest.fixture
def mock_langgraph_client(mocker):
    """Mock LangGraph client"""
    return mocker.patch('app.clients.langgraph_client.LangGraphClient')
```

### Step 6.4: Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_transformer.py -v

# Run integration tests only
poetry run pytest tests/integration/ -v
```

### Step 6.5: Create Comprehensive Documentation

**`README.md`** (Complete version):

```markdown
# Jira-LangGraph Consumer

A robust Kafka consumer service that processes Jira webhook events and forwards them to a LangGraph orchestrator for AI-powered processing.

## Features

- ✅ Kafka consumer with consumer group management
- ✅ Event transformation from Jira to LangGraph format
- ✅ Retry logic with exponential backoff
- ✅ Circuit breaker for external API calls
- ✅ Dead Letter Queue for failed messages
- ✅ Prometheus metrics for monitoring
- ✅ Structured logging
- ✅ Health check endpoints
- ✅ Docker support

## Architecture

```
Jira → Webhook Producer → Kafka (jira-events) → Consumer → LangGraph Orchestrator
                                                     ↓
                                              Dead Letter Queue
```

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry
- Docker & Docker Compose
- Running Kafka cluster

### Installation

1. Clone and navigate to project:
   ```bash
   cd ~/dev/java/ai-learning/jira-consumer
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Start the consumer:
   ```bash
   poetry run python -m app.main
   ```

## Configuration

Environment variables (`.env`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | Yes | `localhost:9092` | Kafka broker address |
| `KAFKA_TOPIC` | Yes | `jira-events` | Topic to consume from |
| `KAFKA_GROUP_ID` | Yes | `jira-consumer-group` | Consumer group ID |
| `LANGGRAPH_API_URL` | Yes | - | LangGraph API endpoint |
| `LANGGRAPH_API_KEY` | Yes | - | LangGraph API key |
| `BATCH_SIZE` | No | `10` | Processing batch size |
| `MAX_RETRIES` | No | `3` | Max retry attempts |
| `DLQ_TOPIC` | No | `jira-events-dlq` | Dead letter queue topic |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Monitoring

### Metrics

Prometheus metrics available at `http://localhost:9090/metrics`:

- `messages_consumed_total` - Total messages consumed
- `messages_processed_success` - Successfully processed messages
- `messages_failed_total` - Failed messages
- `processing_duration_seconds` - Processing time histogram
- `langgraph_api_latency_seconds` - API call latency
- `consumer_lag` - Current consumer lag

### Health Checks

- `GET /health` - Overall health status
- `GET /ready` - Readiness check (Kubernetes)
- `GET /live` - Liveness check (Kubernetes)

## Error Handling

### Retry Strategy

- Automatic retry with exponential backoff
- Max 3 retry attempts per message
- Configurable backoff timing

### Circuit Breaker

- Opens after 5 consecutive failures
- Timeout: 60 seconds
- Prevents cascading failures

### Dead Letter Queue

Failed messages are sent to DLQ with:
- Original message
- Error description
- Timestamp
- Issue key

## Development

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Specific tests
poetry run pytest tests/unit/test_transformer.py -v
```

### Code Quality

```bash
# Format code
poetry run black app/

# Lint
poetry run flake8 app/

# Type checking
poetry run mypy app/
```

## Deployment

### Docker

```bash
# Build image
docker build -t jira-consumer:latest .

# Run container
docker run -d \
  --name jira-consumer \
  --env-file .env \
  jira-consumer:latest
```

### Docker Compose

```bash
docker-compose up -d
```

## Troubleshooting

### Consumer not receiving messages

1. Check Kafka connection:
   ```bash
   docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
   ```

2. Verify consumer group:
   ```bash
   docker exec -it kafka kafka-consumer-groups \
     --bootstrap-server localhost:9092 \
     --describe --group jira-consumer-group
   ```

### Messages going to DLQ

1. Check DLQ messages:
   ```bash
   docker exec -it kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic jira-events-dlq \
     --from-beginning
   ```

2. Review error logs for root cause

### Circuit breaker open

- Wait for timeout (60 seconds)
- Check LangGraph API health
- Review API credentials

## Documentation

- [Architecture Plan](docs/CONSUMER_ARCHITECTURE_PLAN.md)
- [Implementation Guide](docs/IMPLEMENTATION_PLAN.md)
- [API Documentation](docs/API.md)

## License

This is a POC project.
```

**✅ Checkpoint**: Comprehensive tests and documentation completed.

---

## Phase 7: Production Deployment (Day 18-20)

### Milestone: Production-ready deployment with Docker and monitoring

### Step 7.1: Create Dockerfile

**`Dockerfile`**:

```dockerfile
# Multi-stage build for smaller image
FROM python:3.12-slim as builder

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Final stage
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 consumer && \
    mkdir -p /app && \
    chown -R consumer:consumer /app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=consumer:consumer app/ ./app/

# Switch to non-root user
USER consumer

# Expose metrics port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python", "-m", "app.main"]
```

### Step 7.2: Create Docker Compose

**`docker-compose.yml`**:

```yaml
version: '3.8'

services:
  jira-consumer:
    build: .
    container_name: jira-consumer
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - KAFKA_TOPIC=jira-events
      - KAFKA_GROUP_ID=jira-consumer-group
      - LANGGRAPH_API_URL=${LANGGRAPH_API_URL}
      - LANGGRAPH_API_KEY=${LANGGRAPH_API_KEY}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    depends_on:
      - kafka
    networks:
      - kafka-network
    restart: unless-stopped
    ports:
      - "9090:9090"  # Metrics
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  kafka-network:
    external: true
```

### Step 7.3: Create Kubernetes Manifests

**`k8s/deployment.yaml`**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jira-consumer
  labels:
    app: jira-consumer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jira-consumer
  template:
    metadata:
      labels:
        app: jira-consumer
    spec:
      containers:
      - name: consumer
        image: jira-consumer:latest
        ports:
        - containerPort: 9090
          name: metrics
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka-service:9092"
        - name: KAFKA_TOPIC
          value: "jira-events"
        - name: KAFKA_GROUP_ID
          value: "jira-consumer-group"
        - name: LANGGRAPH_API_URL
          valueFrom:
            secretKeyRef:
              name: langgraph-credentials
              key: api-url
        - name: LANGGRAPH_API_KEY
          valueFrom:
            secretKeyRef:
              name: langgraph-credentials
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: jira-consumer-metrics
spec:
  selector:
    app: jira-consumer
  ports:
  - port: 9090
    targetPort: 9090
    name: metrics
```

### Step 7.4: Create CI/CD Pipeline

**`.github/workflows/ci.yml`**:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: poetry install
    
    - name: Run tests
      run: poetry run pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
  
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: poetry install
    
    - name: Run Black
      run: poetry run black --check app/
    
    - name: Run Flake8
      run: poetry run flake8 app/
    
    - name: Run MyPy
      run: poetry run mypy app/
  
  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t jira-consumer:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker push jira-consumer:${{ github.sha }}
```

### Step 7.5: Create Deployment Checklist

**`docs/DEPLOYMENT_CHECKLIST.md`**:

```markdown
# Deployment Checklist

## Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Environment variables configured
- [ ] LangGraph API credentials verified
- [ ] Kafka cluster accessible
- [ ] Monitoring dashboards created
- [ ] Alerting rules configured

## Deployment Steps

### 1. Build and Test

```bash
# Build Docker image
docker build -t jira-consumer:v1.0.0 .

# Run tests in container
docker run jira-consumer:v1.0.0 pytest
```

### 2. Deploy to Staging

```bash
# Deploy to staging
kubectl apply -f k8s/staging/ -n staging

# Verify deployment
kubectl get pods -n staging
kubectl logs -f deployment/jira-consumer -n staging
```

### 3. Smoke Tests

- [ ] Consumer connects to Kafka
- [ ] Messages are processed
- [ ] LangGraph API receives events
- [ ] Metrics are exposed
- [ ] Health checks pass

### 4. Deploy to Production

```bash
# Deploy to production
kubectl apply -f k8s/production/ -n production

# Monitor rollout
kubectl rollout status deployment/jira-consumer -n production
```

### 5. Post-Deployment Verification

- [ ] Check consumer lag
- [ ] Verify message processing rate
- [ ] Monitor error rates
- [ ] Check DLQ for failures
- [ ] Verify LangGraph integration

## Rollback Plan

```bash
# Rollback to previous version
kubectl rollout undo deployment/jira-consumer -n production

# Verify rollback
kubectl rollout status deployment/jira-consumer -n production
```

## Monitoring

- [ ] Grafana dashboards accessible
- [ ] Prometheus scraping metrics
- [ ] Alerts configured
- [ ] Log aggregation working

## Documentation

- [ ] Runbook updated
- [ ] Architecture diagrams current
- [ ] API documentation published
- [ ] Team notified
```

**✅ Checkpoint**: Production deployment ready with Docker, Kubernetes, and CI/CD.

---

## Summary & Next Steps

### What We've Built

A production-ready Kafka consumer service with:

1. **Core Functionality**
   - Kafka consumer with consumer group management
   - Event transformation (Jira → LangGraph)
   - LangGraph API integration

2. **Reliability**
   - Retry logic with exponential backoff
   - Circuit breaker pattern
   - Dead Letter Queue for failures
   - Graceful shutdown handling

3. **Observability**
   - Prometheus metrics
   - Structured logging
   - Health check endpoints
   - Consumer lag monitoring

4. **Testing**
   - Unit tests for transformers
   - Integration tests for end-to-end flow
   - Test coverage reporting

5. **Deployment**
   - Docker containerization
   - Kubernetes manifests
   - CI/CD pipeline
   - Deployment automation

### Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Setup | 2 days | Project structure, dependencies |
| Phase 2: Core Consumer | 3 days | Basic Kafka consumer working |
| Phase 3: LangGraph Integration | 3 days | Event transformation and forwarding |
| Phase 4: Reliability | 3 days | Error handling, DLQ, circuit breaker |
| Phase 5: Observability | 3 days | Metrics, logging, monitoring |
| Phase 6: Testing | 3 days | Unit and integration tests |
| Phase 7: Deployment | 3 days | Docker, K8s, CI/CD |
| **Total** | **20 days** | Production-ready service |

### Quick Start Commands

```bash
# 1. Create project
cd ~/dev/java/ai-learning
mkdir jira-consumer && cd jira-consumer

# 2. Initialize
poetry init
poetry add kafka-python pydantic httpx tenacity prometheus-client

# 3. Create structure
mkdir -p app/{consumers,transformers,clients,models,services,core}
mkdir -p tests/{unit,integration}

# 4. Configure
cp .env.example .env
# Edit .env with your settings

# 5. Run
poetry run python -m app.main
```

### Key Files to Create First

1. `app/core/config.py` - Configuration
2. `app/core/logging.py` - Logging setup
3. `app/models/jira_event.py` - Data models
4. `app/consumers/jira_consumer.py` - Kafka consumer
5. `app/main.py` - Entry point

### Testing Strategy

```bash
# Unit tests - Fast, isolated
poetry run pytest tests/unit/ -v

# Integration tests - Slower, requires Kafka
poetry run pytest tests/integration/ -v

# Coverage report
poetry run pytest --cov=app --cov-report=html
```

### Monitoring Checklist

- [ ] Prometheus scraping metrics at `:9090/metrics`
- [ ] Grafana dashboard imported
- [ ] Alerts configured for:
  - High error rate
  - Consumer lag > threshold
  - Circuit breaker open
  - DLQ messages accumulating

### Production Readiness Checklist

- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] Documentation complete
- [ ] Security review done
- [ ] Performance testing completed
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations

### Support & Maintenance

**Daily**:
- Monitor consumer lag
- Check error rates
- Review DLQ messages

**Weekly**:
- Review metrics trends
- Update dependencies
- Check for security updates

**Monthly**:
- Performance optimization
- Capacity planning
- Documentation updates

### Resources

- [Kafka Consumer Best Practices](https://kafka.apache.org/documentation/#consumerconfigs)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

## Conclusion

This implementation plan provides a complete roadmap for building a production-ready Kafka consumer service. Follow the phases sequentially, validate each checkpoint, and you'll have a robust, scalable service that reliably processes Jira events and forwards them to your LangGraph orchestrator.

**Ready to start? Begin with Phase 1: Project Setup!**