"""
RabbitMQ Connection Manager - Singleton Pattern
Handles connection lifecycle with auto-reconnect and connection pooling
"""
import os
import time
import logging
from typing import Optional
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """Singleton RabbitMQ connection manager"""
    
    _instance: Optional['RabbitMQConnection'] = None
    _connection: Optional[BlockingConnection] = None
    _channel: Optional[BlockingChannel] = None
    _is_connecting: bool = False
    _reconnect_attempts: int = 0
    MAX_RECONNECT_ATTEMPTS: int = 10
    RECONNECT_DELAY: int = 5  # seconds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RabbitMQConnection, cls).__new__(cls)
        return cls._instance

    def connect(self) -> None:
        """Connect to RabbitMQ"""
        if self._connection and self._channel and self._connection.is_open:
            logger.info("[SUCCESS] RabbitMQ already connected")
            return

        if self._is_connecting:
            logger.info("[INFO] RabbitMQ connection in progress...")
            return

        self._is_connecting = True

        try:
            rabbit_url = os.getenv("RABBITMQ_URL")
            if not rabbit_url:
                logger.warning("[WARNING] RABBITMQ_URL not set, skipping RabbitMQ connection")
                self._is_connecting = False
                return

            logger.info("[INFO] Connecting to RabbitMQ...")
            
            # Parse CloudAMQP URL
            parameters = pika.URLParameters(rabbit_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            parameters.socket_timeout = 5  # Add timeout to prevent hanging
            
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            self._reconnect_attempts = 0
            self._is_connecting = False
            logger.info("[SUCCESS] RabbitMQ connected successfully")
        
        except Exception as error:
            self._is_connecting = False
            logger.warning(f"[WARNING] Failed to connect to RabbitMQ (will continue without it): {error}")
            # Don't reconnect on first failure during startup
            return

    def _reconnect(self) -> None:
        """Reconnect with exponential backoff"""
        if self._reconnect_attempts >= self.MAX_RECONNECT_ATTEMPTS:
            logger.error(
                f"[ERROR] Max reconnection attempts ({self.MAX_RECONNECT_ATTEMPTS}) reached. Giving up."
            )
            raise ConnectionError("Failed to connect to RabbitMQ after maximum attempts")

        self._reconnect_attempts += 1
        delay = self.RECONNECT_DELAY * (2 ** (self._reconnect_attempts - 1))
        
        logger.info(
            f"[INFO] Reconnecting to RabbitMQ (attempt {self._reconnect_attempts}/{self.MAX_RECONNECT_ATTEMPTS}) in {delay}s..."
        )

        time.sleep(delay)
        self.connect()

    def get_channel(self) -> Optional[BlockingChannel]:
        """Get active channel"""
        if not self._channel or not self._connection or not self._connection.is_open:
            logger.warning("[WARNING] RabbitMQ channel is not available")
            return None
        return self._channel

    def get_connection(self) -> BlockingConnection:
        """Get active connection"""
        if not self._connection or not self._connection.is_open:
            raise ConnectionError("RabbitMQ connection is not available. Call connect() first.")
        return self._connection

    def is_connected(self) -> bool:
        """Check if connected"""
        return (
            self._connection is not None 
            and self._channel is not None 
            and self._connection.is_open
        )

    def close(self) -> None:
        """Close connection gracefully"""
        try:
            if self._channel and self._channel.is_open:
                self._channel.close()
                self._channel = None
            if self._connection and self._connection.is_open:
                self._connection.close()
                self._connection = None
            logger.info("[SUCCESS] RabbitMQ connection closed gracefully")
        except Exception as error:
            logger.error(f"[ERROR] Error closing RabbitMQ connection: {error}")


# Singleton instance getter
def get_rabbitmq() -> RabbitMQConnection:
    """Get RabbitMQ connection instance"""
    return RabbitMQConnection()


# Initialize RabbitMQ connection
def init_rabbitmq() -> None:
    """Initialize RabbitMQ connection (synchronous)"""
    rabbitmq = get_rabbitmq()
    rabbitmq.connect()
