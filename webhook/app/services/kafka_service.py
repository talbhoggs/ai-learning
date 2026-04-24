"""Kafka service with connection handling and retry logic"""
import json
import time
from typing import Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class KafkaService:
    """Kafka service with connection management"""
    
    _instance: Optional['KafkaService'] = None
    _producer: Optional[KafkaProducer] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Kafka producer with retry logic"""
        if self._producer is None:
            self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Kafka broker with retry logic"""
        max_retries = settings.kafka_max_retries
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to connect to Kafka at {settings.kafka_bootstrap_servers}")
                self._producer = KafkaProducer(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    retries=settings.kafka_max_retries,
                    retry_backoff_ms=settings.kafka_retry_backoff_ms,
                    request_timeout_ms=settings.kafka_request_timeout_ms,
                    acks='all',  # Wait for all replicas to acknowledge
                    compression_type='gzip',  # Compress messages
                )
                logger.info("Successfully connected to Kafka")
                return
            except NoBrokersAvailable as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = settings.kafka_retry_backoff_ms * (2 ** retry_count) / 1000
                    logger.warning(
                        f"Kafka connection failed (attempt {retry_count}/{max_retries}). "
                        f"Retrying in {wait_time}s... Error: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to connect to Kafka after {max_retries} attempts")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to Kafka: {str(e)}")
                raise
    
    def publish(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """
        Publish message to Kafka topic
        
        Args:
            topic: Kafka topic name
            message: Message payload as dictionary
            key: Optional message key for partitioning
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if self._producer is None:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            # Send message asynchronously
            future = self._producer.send(topic, value=message, key=key)
            
            # Wait for message to be sent (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Message sent successfully to topic '{topic}' "
                f"[partition: {record_metadata.partition}, offset: {record_metadata.offset}]"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to Kafka: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close Kafka producer connection"""
        if self._producer:
            try:
                self._producer.flush()  # Ensure all messages are sent
                self._producer.close()
                logger.info("Kafka producer closed successfully")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {str(e)}")
            finally:
                self._producer = None
    
    def is_connected(self) -> bool:
        """Check if Kafka producer is connected"""
        return self._producer is not None
    
    def reconnect(self) -> None:
        """Reconnect to Kafka broker"""
        logger.info("Attempting to reconnect to Kafka")
        self.close()
        self._connect()

