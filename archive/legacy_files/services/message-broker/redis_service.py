#!/usr/bin/env python3
"""
Advanced Redis Message Broker Service
Enhanced inter-service communication with error handling, retry logic, and message persistence.
"""

import json
import logging
import signal
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Message structure for inter-service communication"""

    id: str
    source_service: str
    target_service: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    ttl: int = 3600  # 1 hour default TTL
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ServiceHealth:
    """Service health status"""

    service_name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    last_heartbeat: datetime
    response_time: float
    error_count: int = 0
    message_count: int = 0


class AdvancedRedisMessageBroker:
    """
    Advanced Redis-based message broker with enhanced features:
    - Reliable message delivery with retry logic
    - Service health monitoring
    - Message persistence and recovery
    - Priority-based message routing
    - Dead letter queue handling
    - Circuit breaker pattern
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        service_name: str = "message-broker",
        max_workers: int = 10,
    ):

        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.service_name = service_name
        self.max_workers = max_workers

        # Redis connection
        self.redis_client = None
        self.redis_pubsub = None

        # Service state
        self.is_running = False
        self.health_check_interval = 30  # seconds
        self.message_handlers: Dict[str, Callable] = {}
        self.health_monitors: Dict[str, ServiceHealth] = {}

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.health_thread = None
        self.message_thread = None

        # Circuit breaker state
        self.circuit_breaker_state = "closed"  # closed, open, half-open
        self.failure_threshold = 5
        self.failure_count = 0
        self.recovery_timeout = 60  # seconds
        self.last_failure_time = None

        # Message queues
        self.queues = {
            "high_priority": "queue:high_priority",
            "normal": "queue:normal",
            "low_priority": "queue:low_priority",
            "dead_letter": "queue:dead_letter",
            "health": "queue:health",
        }

        # Initialize Redis connection
        self._connect_redis()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _connect_redis(self) -> None:
        """Establish Redis connection with retry logic"""
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                self.redis_client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )

                # Test connection
                self.redis_client.ping()
                logger.info(
                    f"✅ Redis connection established to {self.redis_host}:{self.redis_port}"
                )
                return

            except (ConnectionError, TimeoutError, RedisError) as e:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(
                        f"Failed to connect to Redis after {max_retries} attempts"
                    )
                    raise

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)

    def start(self) -> None:
        """Start the message broker service"""
        if self.is_running:
            logger.warning("Message broker is already running")
            return

        logger.info("🚀 Starting Advanced Redis Message Broker...")
        self.is_running = True

        # Start health monitoring thread
        self.health_thread = threading.Thread(
            target=self._health_monitor_loop, daemon=True
        )
        self.health_thread.start()

        # Start message processing thread
        self.message_thread = threading.Thread(
            target=self._message_processing_loop, daemon=True
        )
        self.message_thread.start()

        logger.info("✅ Advanced Redis Message Broker started successfully")

    def stop(self) -> None:
        """Stop the message broker service gracefully"""
        if not self.is_running:
            return

        logger.info("🛑 Stopping Advanced Redis Message Broker...")
        self.is_running = False

        # Wait for threads to complete
        if self.health_thread and self.health_thread.is_alive():
            self.health_thread.join(timeout=5)

        if self.message_thread and self.message_thread.is_alive():
            self.message_thread.join(timeout=5)

        # Shutdown executor
        self.executor.shutdown(wait=True)

        # Close Redis connections
        if self.redis_pubsub:
            self.redis_pubsub.close()

        if self.redis_client:
            self.redis_client.close()

        logger.info("✅ Advanced Redis Message Broker stopped")

    def send_message(
        self,
        target_service: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: int = 0,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send a message to a target service with enhanced features
        """
        try:
            # Create message
            message = Message(
                id=str(uuid.uuid4()),
                source_service=self.service_name,
                target_service=target_service,
                message_type=message_type,
                payload=payload,
                timestamp=datetime.utcnow(),
                priority=priority,
                correlation_id=correlation_id,
                metadata=metadata or {},
            )

            # Determine queue based on priority
            if priority >= 8:
                queue_name = self.queues["high_priority"]
            elif priority >= 4:
                queue_name = self.queues["normal"]
            else:
                queue_name = self.queues["low_priority"]

            # Serialize message
            message_data = {
                **asdict(message),
                "timestamp": message.timestamp.isoformat(),
            }

            # Send to Redis queue
            self.redis_client.lpush(queue_name, json.dumps(message_data))

            # Publish to service-specific channel for real-time delivery
            channel = f"service:{target_service}"
            self.redis_client.publish(channel, json.dumps(message_data))

            logger.info(
                f"📤 Message sent: {message.id} -> {target_service} ({message_type})"
            )
            return message.id

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self._handle_circuit_breaker_failure()
            raise

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a message handler for a specific message type"""
        self.message_handlers[message_type] = handler
        logger.info(f"📝 Registered handler for message type: {message_type}")

    def _message_processing_loop(self) -> None:
        """Main message processing loop"""
        logger.info("🔄 Starting message processing loop...")

        while self.is_running:
            try:
                # Process messages from all queues (high priority first)
                for queue_name in [
                    self.queues["high_priority"],
                    self.queues["normal"],
                    self.queues["low_priority"],
                ]:

                    # Get message with timeout
                    result = self.redis_client.brpop(queue_name, timeout=1)
                    if result:
                        _, message_data = result
                        self._process_message(json.loads(message_data))

                # Small delay to prevent busy waiting
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")
                time.sleep(1)

    def _process_message(self, message_data: Dict[str, Any]) -> None:
        """Process a single message"""
        try:
            # Deserialize message
            message = Message(
                id=message_data["id"],
                source_service=message_data["source_service"],
                target_service=message_data["target_service"],
                message_type=message_data["message_type"],
                payload=message_data["payload"],
                timestamp=datetime.fromisoformat(message_data["timestamp"]),
                priority=message_data.get("priority", 0),
                retry_count=message_data.get("retry_count", 0),
                max_retries=message_data.get("max_retries", 3),
                correlation_id=message_data.get("correlation_id"),
                metadata=message_data.get("metadata", {}),
            )

            # Check if message is for this service
            if message.target_service != self.service_name:
                return

            # Check message TTL
            if datetime.utcnow() - message.timestamp > timedelta(seconds=message.ttl):
                logger.warning(
                    f"Message {message.id} expired, moving to dead letter queue"
                )
                self._move_to_dead_letter(message)
                return

            # Process message
            handler = self.message_handlers.get(message.message_type)
            if handler:
                # Submit to thread pool for async processing
                future = self.executor.submit(self._execute_handler, handler, message)
                future.add_done_callback(
                    lambda f: self._handle_handler_result(f, message)
                )
            else:
                logger.warning(
                    f"No handler registered for message type: {message.message_type}"
                )

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _execute_handler(self, handler: Callable, message: Message) -> Any:
        """Execute message handler in thread pool"""
        try:
            return handler(message)
        except Exception as e:
            logger.error(f"Handler execution failed: {e}")
            raise

    def _handle_handler_result(self, future, message: Message) -> None:
        """Handle the result of message handler execution"""
        try:
            result = future.result()
            logger.info(f"✅ Message {message.id} processed successfully")

            # Send acknowledgment if correlation_id exists
            if message.correlation_id:
                self.send_message(
                    target_service=message.source_service,
                    message_type="ack",
                    payload={"status": "success", "message_id": message.id},
                    correlation_id=message.correlation_id,
                )

        except Exception as e:
            logger.error(f"❌ Message {message.id} processing failed: {e}")

            # Handle retry logic
            if message.retry_count < message.max_retries:
                message.retry_count += 1
                logger.info(
                    f"🔄 Retrying message {message.id} (attempt {message.retry_count})"
                )

                # Exponential backoff
                delay = min(2**message.retry_count, 60)  # Max 60 seconds
                time.sleep(delay)

                # Re-queue message
                self._requeue_message(message)
            else:
                logger.error(
                    f"💀 Message {message.id} exceeded max retries, moving to dead letter queue"
                )
                self._move_to_dead_letter(message)

    def _requeue_message(self, message: Message) -> None:
        """Re-queue a message for retry"""
        try:
            message_data = {
                **asdict(message),
                "timestamp": message.timestamp.isoformat(),
            }

            # Determine queue based on priority
            if message.priority >= 8:
                queue_name = self.queues["high_priority"]
            elif message.priority >= 4:
                queue_name = self.queues["normal"]
            else:
                queue_name = self.queues["low_priority"]

            self.redis_client.lpush(queue_name, json.dumps(message_data))

        except Exception as e:
            logger.error(f"Failed to requeue message: {e}")

    def _move_to_dead_letter(self, message: Message) -> None:
        """Move a message to the dead letter queue"""
        try:
            message_data = {
                **asdict(message),
                "timestamp": message.timestamp.isoformat(),
                "dead_letter_reason": "max_retries_exceeded",
            }

            self.redis_client.lpush(
                self.queues["dead_letter"], json.dumps(message_data)
            )

        except Exception as e:
            logger.error(f"Failed to move message to dead letter queue: {e}")

    def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""
        logger.info("💓 Starting health monitoring loop...")

        while self.is_running:
            try:
                self._update_service_health()
                time.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(5)

    def _update_service_health(self) -> None:
        """Update service health status"""
        try:
            # Check Redis connection
            start_time = time.time()
            self.redis_client.ping()
            response_time = time.time() - start_time

            # Update health status
            health = ServiceHealth(
                service_name=self.service_name,
                status="healthy" if response_time < 1.0 else "degraded",
                last_heartbeat=datetime.utcnow(),
                response_time=response_time,
                message_count=len(self.message_handlers),
            )

            # Store health status
            health_data = {
                **asdict(health),
                "last_heartbeat": health.last_heartbeat.isoformat(),
            }

            self.redis_client.hset(
                "service:health", self.service_name, json.dumps(health_data)
            )

            # Publish health update
            self.redis_client.publish("health:updates", json.dumps(health_data))

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._handle_circuit_breaker_failure()

    def _handle_circuit_breaker_failure(self) -> None:
        """Handle circuit breaker failure logic"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.circuit_breaker_state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health status of a specific service"""
        try:
            health_data = self.redis_client.hget("service:health", service_name)
            if health_data:
                data = json.loads(health_data)
                return ServiceHealth(
                    service_name=data["service_name"],
                    status=data["status"],
                    last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]),
                    response_time=data["response_time"],
                    error_count=data.get("error_count", 0),
                    message_count=data.get("message_count", 0),
                )
        except Exception as e:
            logger.error(f"Failed to get service health: {e}")

        return None

    def get_all_service_health(self) -> List[ServiceHealth]:
        """Get health status of all services"""
        try:
            health_data = self.redis_client.hgetall("service:health")
            services = []

            for service_name, data in health_data.items():
                try:
                    data_dict = json.loads(data)
                    services.append(
                        ServiceHealth(
                            service_name=data_dict["service_name"],
                            status=data_dict["status"],
                            last_heartbeat=datetime.fromisoformat(
                                data_dict["last_heartbeat"]
                            ),
                            response_time=data_dict["response_time"],
                            error_count=data_dict.get("error_count", 0),
                            message_count=data_dict.get("message_count", 0),
                        )
                    )
                except Exception as e:
                    logger.error(f"Failed to parse health data for {service_name}: {e}")

            return services

        except Exception as e:
            logger.error(f"Failed to get all service health: {e}")
            return []

    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        try:
            stats = {}
            for queue_name, queue_key in self.queues.items():
                stats[queue_name] = self.redis_client.llen(queue_key)
            return stats
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Create message broker instance
    broker = AdvancedRedisMessageBroker(
        redis_host="localhost", redis_port=6379, service_name="test-service"
    )

    # Register message handlers
    def handle_test_message(message: Message):
        logger.info(f"Processing test message: {message.payload}")
        return {"status": "processed", "message_id": message.id}

    broker.register_handler("test", handle_test_message)

    # Start the broker
    broker.start()

    try:
        # Send a test message
        message_id = broker.send_message(
            target_service="test-service",
            message_type="test",
            payload={"data": "Hello, World!"},
            priority=5,
        )

        logger.info(f"Sent test message: {message_id}")

        # Keep running for a while
        time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        broker.stop()
