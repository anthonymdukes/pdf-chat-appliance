"""
Advanced Message Broker Service Package
Enhanced inter-service communication with Redis backend.
"""

from .redis_service import AdvancedRedisMessageBroker, Message, ServiceHealth

__version__ = "2.4.0"
__author__ = "PDF Chat Appliance Team"

__all__ = ["AdvancedRedisMessageBroker", "Message", "ServiceHealth"]
