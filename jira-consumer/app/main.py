"""Main entry point for the consumer service"""
import signal
import sys

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.consumers.jira_consumer import JiraEventConsumer
from app.models.jira_event import JiraEvent

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Global consumer instance for graceful shutdown
consumer_instance = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if consumer_instance:
        consumer_instance.close()
    sys.exit(0)


def process_message(message: dict) -> None:
    """
    Process a single message from Kafka
    
    Args:
        message: Deserialized message from Kafka
    """
    try:
        # Validate and parse Jira event
        jira_event = JiraEvent(**message)
        
        logger.info(
            f"Processing event: {jira_event.webhookEvent} | "
            f"Issue: {jira_event.issue.key} | "
            f"Summary: {jira_event.issue.fields.summary}"
        )

        logger.info(jira_event.json())

       
        logger.debug(f"Event timestamp: {jira_event.timestamp}")
        logger.debug(f"Project: {jira_event.issue.fields.project.name}")
        logger.debug(f"Status: {jira_event.issue.fields.status.name}")
        logger.debug(f"Priority: {jira_event.issue.fields.priority.name}")
        
        if jira_event.comment:
            logger.info(f"Comment by {jira_event.comment.author.displayName}: {jira_event.comment.body[:50]}...")
        
        # TODO: Phase 3 - Transform and forward to LangGraph
        logger.info(f"✓ Successfully processed {jira_event.issue.key}")
        
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}", exc_info=True)
        # TODO: Phase 4 - Send to Dead Letter Queue
        raise


def main():
    """Main function"""
    global consumer_instance
    
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)
    logger.info(f"Kafka Configuration:")
    logger.info(f"  Broker: {settings.kafka_bootstrap_servers}")
    logger.info(f"  Topic: {settings.kafka_topic}")
    logger.info(f"  Consumer Group: {settings.kafka_group_id}")
    logger.info(f"  Auto Offset Reset: {settings.kafka_auto_offset_reset}")
    logger.info(f"LangGraph Configuration:")
    logger.info(f"  API URL: {settings.langgraph_api_url}")
    logger.info(f"  API Key: {'*' * 10 if settings.langgraph_api_key else 'NOT SET'}")
    logger.info(f"Processing Configuration:")
    logger.info(f"  Batch Size: {settings.batch_size}")
    logger.info(f"  Max Retries: {settings.max_retries}")
    logger.info(f"  DLQ Topic: {settings.dlq_topic}")
    logger.info(f"  Log Level: {settings.log_level}")
    logger.info("=" * 60)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start consumer
        logger.info("Initializing Kafka consumer...")
        consumer_instance = JiraEventConsumer()
        
        logger.info("✓ Consumer ready! Waiting for messages...")
        logger.info("  (Press Ctrl+C to stop)")
        logger.info("=" * 60)
        
        # Start consuming messages
        consumer_instance.consume(process_message)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("=" * 60)
        logger.info("Consumer stopped")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
