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
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                # No consumer_timeout_ms - run indefinitely until interrupted
            )
            logger.info(f"Successfully connected to Kafka topic: {settings.kafka_topic}")
            logger.info(f"Consumer group: {settings.kafka_group_id}")
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
        logger.info("=" * 60)
        
        try:
            for message in self.consumer:
                try:
                    logger.debug(
                        f"Received message from partition {message.partition}, "
                        f"offset {message.offset}"
                    )
                    
                    # Process message
                    processor_callback(message.value)
                    
                    # Commit offset after successful processing
                    self.consumer.commit()
                    logger.debug(f"Committed offset {message.offset}")
                    
                except Exception as e:
                    logger.error(
                        f"Error processing message at offset {message.offset}: {str(e)}",
                        exc_info=True
                    )
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

# Made with Bob
