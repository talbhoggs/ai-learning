# Jira-LangGraph Consumer - Quick Start Guide

## 🚀 Get Started in 15 Minutes

This guide will help you set up and run the Kafka consumer service quickly.

---

## Prerequisites Checklist

Before starting, ensure you have:

- ✅ Python 3.12 or higher installed
- ✅ Poetry installed (`curl -sSL https://install.python-poetry.org | python3 -`)
- ✅ Docker and Docker Compose running
- ✅ Kafka cluster accessible (from webhook project)
- ✅ LangGraph API URL and credentials

---

## Step 1: Create Project (5 minutes)

```bash
# Navigate to workspace
cd ~/dev/java/ai-learning

# Create project directory
mkdir jira-consumer
cd jira-consumer

# Initialize Git
git init
git branch -M main

# Create directory structure
mkdir -p app/{consumers,transformers,clients,models,services,core}
mkdir -p tests/{unit,integration}
mkdir -p docs

# Create __init__.py files
touch app/__init__.py
touch app/{consumers,transformers,clients,models,services,core}/__init__.py
touch tests/__init__.py
touch tests/{unit,integration}/__init__.py
```

---

## Step 2: Initialize Poetry (2 minutes)

```bash
# Initialize Poetry project
poetry init --name jira-consumer \
           --description "Kafka consumer for Jira events to LangGraph" \
           --python "^3.12" \
           --no-interaction

# Add dependencies
poetry add kafka-python pydantic pydantic-settings httpx tenacity python-dotenv prometheus-client

# Add dev dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov black flake8 mypy
```

---

## Step 3: Configure Environment (2 minutes)

Create `.env` file:

```bash
cat > .env << 'EOF'
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
EOF
```

**Important**: Update `LANGGRAPH_API_URL` and `LANGGRAPH_API_KEY` with your actual credentials!

---

## Step 4: Create Core Files (3 minutes)

### Configuration (`app/core/config.py`)

```python
"""Configuration settings"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "jira-events")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "jira-consumer-group")
    langgraph_api_url: str = os.getenv("LANGGRAPH_API_URL", "")
    langgraph_api_key: str = os.getenv("LANGGRAPH_API_KEY", "")
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    dlq_topic: str = os.getenv("DLQ_TOPIC", "jira-events-dlq")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Logging (`app/core/logging.py`)

```python
"""Logging configuration"""
import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

### Main Entry Point (`app/main.py`)

```python
"""Main entry point"""
import signal
import sys
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

def signal_handler(signum, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

def main():
    logger.info(f"Starting Jira-LangGraph Consumer")
    logger.info(f"Kafka: {settings.kafka_bootstrap_servers}")
    logger.info(f"Topic: {settings.kafka_topic}")
    logger.info(f"LangGraph: {settings.langgraph_api_url}")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Consumer ready! (Press Ctrl+C to stop)")
    
    # TODO: Add consumer logic
    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
```

---

## Step 5: Test Basic Setup (1 minute)

```bash
# Verify Kafka is running
cd ../webhook
docker-compose ps

# If not running, start it
docker-compose up -d

# Return to consumer project
cd ../jira-consumer

# Run the consumer
poetry run python -m app.main
```

**Expected Output**:
```
2024-04-28 10:00:00 - app.main - INFO - Starting Jira-LangGraph Consumer
2024-04-28 10:00:00 - app.main - INFO - Kafka: localhost:9092
2024-04-28 10:00:00 - app.main - INFO - Topic: jira-events
2024-04-28 10:00:00 - app.main - INFO - LangGraph: https://your-langgraph-api.com
2024-04-28 10:00:00 - app.main - INFO - Consumer ready! (Press Ctrl+C to stop)
```

Press `Ctrl+C` to stop.

---

## Step 6: Add Full Implementation (2 minutes)

Now that the basic setup works, you have two options:

### Option A: Copy Full Implementation

Download the complete implementation files from the detailed plan:
- See [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) for Phase 2-7
- Copy all code files as specified

### Option B: Implement Incrementally

Follow the phase-by-phase implementation:
1. **Phase 2**: Core Kafka consumer
2. **Phase 3**: LangGraph integration
3. **Phase 4**: Error handling & DLQ
4. **Phase 5**: Observability
5. **Phase 6**: Testing
6. **Phase 7**: Production deployment

---

## Verification Checklist

After setup, verify:

- [ ] Consumer starts without errors
- [ ] Kafka connection successful
- [ ] Environment variables loaded correctly
- [ ] Logs are readable and informative
- [ ] Can stop gracefully with Ctrl+C

---

## Next Steps

### For Development

1. **Implement Kafka Consumer** (Phase 2)
   - Create `app/consumers/jira_consumer.py`
   - Add message consumption logic
   - Test with sample messages

2. **Add LangGraph Integration** (Phase 3)
   - Create `app/clients/langgraph_client.py`
   - Implement event transformation
   - Test end-to-end flow

3. **Add Error Handling** (Phase 4)
   - Implement retry logic
   - Add circuit breaker
   - Set up Dead Letter Queue

### For Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=app

# Specific test
poetry run pytest tests/unit/test_transformer.py -v
```

### For Production

```bash
# Build Docker image
docker build -t jira-consumer:latest .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f jira-consumer
```

---

## Common Issues & Solutions

### Issue: "No module named 'kafka'"

**Solution**:
```bash
poetry install
poetry run python -m app.main
```

### Issue: "Cannot connect to Kafka"

**Solution**:
```bash
# Check Kafka is running
cd ../webhook
docker-compose ps

# Check Kafka logs
docker-compose logs kafka
```

### Issue: "LangGraph API authentication failed"

**Solution**:
- Verify `LANGGRAPH_API_KEY` in `.env`
- Test API manually: `curl -H "Authorization: Bearer YOUR_KEY" https://your-api.com/health`

### Issue: "Consumer lag increasing"

**Solution**:
- Scale up consumer instances
- Increase `BATCH_SIZE`
- Check LangGraph API performance

---

## Useful Commands

```bash
# Development
poetry run python -m app.main              # Run consumer
poetry run pytest                          # Run tests
poetry run black app/                      # Format code
poetry run flake8 app/                     # Lint code

# Docker
docker build -t jira-consumer .            # Build image
docker-compose up -d                       # Start services
docker-compose logs -f jira-consumer       # View logs
docker-compose down                        # Stop services

# Kafka
# List topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Consume messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic jira-events \
  --from-beginning

# Check consumer group
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group jira-consumer-group
```

---

## Project Structure Reference

```
jira-consumer/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entry point ✅
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
│       ├── config.py               # Configuration ✅
│       ├── logging.py              # Logging ✅
│       ├── metrics.py              # Prometheus metrics
│       └── circuit_breaker.py     # Circuit breaker
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── .env                            # Environment config ✅
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml                  # Poetry config ✅
└── README.md
```

✅ = Created in this quick start

---

## Resources

- **Detailed Implementation**: [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md)
- **Architecture Overview**: [`CONSUMER_ARCHITECTURE_PLAN.md`](CONSUMER_ARCHITECTURE_PLAN.md)
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/

---

## Support

For issues or questions:
1. Check the detailed implementation plan
2. Review logs for error messages
3. Verify environment configuration
4. Test Kafka and LangGraph connectivity separately

---

**🎉 Congratulations!** You've completed the quick start setup. Your consumer is ready for development!

**Next**: Follow the detailed implementation plan to add full functionality.