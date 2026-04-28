# Jira Consumer

Kafka consumer service that processes Jira webhook events and forwards them to a LangGraph orchestrator for AI-powered processing.

## Architecture

```
Jira → Webhook Producer → Kafka (jira-events) → Consumer → LangGraph Orchestrator
```

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

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry (or pip)
- Docker & Docker Compose
- Running Kafka cluster

### Installation

1. Clone and navigate to project:
   ```bash
   cd jira-consumer
   ```

2. Install dependencies:
   
   **Using Poetry:**
   ```bash
   poetry install
   ```
   
   **Using pip:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Start the consumer:
   
   **Using Poetry:**
   ```bash
   poetry run python -m app.main
   ```
   
   **Using pip:**
   ```bash
   python -m app.main
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

## Project Structure

```
jira-consumer/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── consumers/
│   │   └── jira_consumer.py       # Kafka consumer
│   ├── transformers/
│   │   └── jira_transformer.py    # Event transformation
│   ├── clients/
│   │   └── langgraph_client.py    # LangGraph API client
│   ├── models/
│   │   ├── jira_event.py          # Input models
│   │   └── langgraph_request.py   # Output models
│   ├── services/
│   │   ├── processor_service.py   # Main processing
│   │   └── dlq_service.py         # Dead Letter Queue
│   └── core/
│       ├── config.py               # Configuration
│       ├── logging.py              # Logging setup
│       ├── metrics.py              # Prometheus metrics
│       └── circuit_breaker.py     # Circuit breaker
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Development Status

**Phase 1: Project Setup** ✅ COMPLETE
- [x] Project structure created
- [x] Configuration files set up
- [x] Core modules initialized
- [x] Basic entry point working

**Phase 2: Core Consumer** 🚧 IN PROGRESS
- [ ] Kafka consumer implementation
- [ ] Message consumption logic
- [ ] Basic error handling

**Phase 3: LangGraph Integration** 📋 PLANNED
- [ ] Event transformation
- [ ] LangGraph client
- [ ] End-to-end flow

**Phase 4: Reliability** 📋 PLANNED
- [ ] Retry logic
- [ ] Circuit breaker
- [ ] Dead Letter Queue

**Phase 5: Observability** 📋 PLANNED
- [ ] Prometheus metrics
- [ ] Structured logging
- [ ] Health checks

**Phase 6: Testing** 📋 PLANNED
- [ ] Unit tests
- [ ] Integration tests
- [ ] Coverage reporting

**Phase 7: Production** 📋 PLANNED
- [ ] Docker setup
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline

## Development

### Running Tests

```bash
# Using Poetry
poetry run pytest

# Using pip
pytest
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

### Consumer not starting

1. Check Python version: `python --version` (should be 3.12+)
2. Verify dependencies installed: `poetry install` or `pip install -r requirements.txt`
3. Check .env file exists and has correct values

### Cannot connect to Kafka

1. Verify Kafka is running:
   ```bash
   docker ps | grep kafka
   ```

2. Check Kafka logs:
   ```bash
   docker logs kafka
   ```

3. Test Kafka connection:
   ```bash
   docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
   ```

## Documentation

- [Architecture Plan](../webhook/docs/architecture/CONSUMER_ARCHITECTURE_PLAN.md)
- [Implementation Guide](../webhook/docs/architecture/IMPLEMENTATION_PLAN.md)
- [Quick Start Guide](../webhook/docs/architecture/QUICK_START_GUIDE.md)

## License

This is a POC project.

## Support

For issues or questions:
1. Check the implementation plan documentation
2. Review logs for error messages
3. Verify environment configuration
4. Test Kafka and LangGraph connectivity separately