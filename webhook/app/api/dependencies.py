"""API dependencies"""
from app.services.kafka_service import KafkaService
from app.services.webhook_service import WebhookService


# Singleton instances
_kafka_service = KafkaService()


def get_kafka_service() -> KafkaService:
    """Get Kafka service instance"""
    return _kafka_service


def get_webhook_service() -> WebhookService:
    """Get webhook service instance"""
    return WebhookService(kafka_service=get_kafka_service())

