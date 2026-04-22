"""Configuration settings for the application"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Kafka Configuration
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "jira-events")
    
    # Kafka Producer Configuration
    kafka_max_retries: int = int(os.getenv("KAFKA_MAX_RETRIES", "3"))
    kafka_retry_backoff_ms: int = int(os.getenv("KAFKA_RETRY_BACKOFF_MS", "1000"))
    kafka_request_timeout_ms: int = int(os.getenv("KAFKA_REQUEST_TIMEOUT_MS", "30000"))
    
    # Application Configuration
    app_name: str = "Jira Webhook to Kafka"
    app_version: str = "1.0.0"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Made with Bob
