# AI Learning Projects

A collection of AI and machine learning projects for learning and experimentation.

## 📁 Projects

### 1. Jira Webhook to Kafka POC (`webhook/`)

A production-ready FastAPI service that receives Jira webhook events and publishes them to Apache Kafka.

**Key Features:**
- FastAPI webhook endpoint with Pydantic validation
- Kafka producer with retry logic
- Docker Compose setup for local development
- Comprehensive error handling and logging
- Health check endpoints
- Kafka UI for monitoring

**Quick Start:**
```bash
cd webhook
poetry install
docker-compose up -d
poetry run uvicorn app.main:app --reload
```

**Documentation:** See [webhook/README.md](webhook/README.md) for detailed setup and usage.

---

### 2. Python Scripts

- `app.py` - Main application script
- `ollama.py` - Ollama integration
- `streamlit.py` - Streamlit web interface

## 🛠️ Technology Stack

- **Python 3.12+**
- **FastAPI** - Modern web framework
- **Apache Kafka** - Event streaming platform
- **Docker & Docker Compose** - Containerization
- **Poetry** - Dependency management
- **Pydantic** - Data validation
- **Streamlit** - Web UI framework

## 📚 Documentation

Each project contains its own detailed documentation:
- Setup instructions
- API references
- Architecture diagrams
- Troubleshooting guides

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-learning
   ```

2. **Choose a project**
   ```bash
   cd webhook  # or any other project directory
   ```

3. **Follow the project-specific README**
   Each project has its own setup instructions and requirements.

## 📖 Learning Resources

This repository serves as a hands-on learning environment for:
- Building production-ready APIs
- Event-driven architectures
- Microservices patterns
- Docker containerization
- Python best practices

## 🤝 Contributing

This is a personal learning repository. Feel free to fork and experiment!

## 📝 License

This project is for educational purposes.