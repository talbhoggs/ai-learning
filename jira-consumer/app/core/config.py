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

# Made with Bob
