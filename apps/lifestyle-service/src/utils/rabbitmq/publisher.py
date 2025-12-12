"""
Event Publisher for RabbitMQ
Handles publishing habit events to appropriate exchanges with routing keys
"""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from .connection import get_rabbitmq
from .config import RABBITMQ_CONFIG
import logging

logger = logging.getLogger(__name__)


class EventPublisher:
    """Event Publisher for Habit Events"""

    def _publish_event(
        self,
        event: Dict[str, Any],
        exchange: str,
        routing_key: str
    ) -> None:
        """
        Publish an event to RabbitMQ
        
        Args:
            event: The event dictionary to publish
            exchange: The exchange name
            routing_key: The routing key for the event
        """
        try:
            rabbitmq = get_rabbitmq()
            channel = rabbitmq.get_channel()

            if not channel:
                logger.error("❌ RabbitMQ channel not available")
                raise Exception("RabbitMQ channel not available")

            message = json.dumps(event)
            
            # Publish with persistence (durable message)
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message,
                properties={
                    'delivery_mode': 2,  # Persistent message
                    'content_type': 'application/json',
                    'content_encoding': 'utf-8',
                    'timestamp': int(datetime.now().timestamp()),
                    'message_id': event['eventId'],
                }
            )

            logger.info(f"📤 Published event: {event['eventType']} to {exchange}/{routing_key}")
        except Exception as error:
            logger.error(f"❌ Failed to publish event: {error}")
            raise

    def publish_habit_created(
        self,
        user_id: str,
        habit_id: str,
        habit_type: str,
        name: str,
        frequency: str,
        target_value: Optional[int] = None,
        target_unit: Optional[str] = None
    ) -> None:
        """Publish HABIT_CREATED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'HABIT_CREATED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'habitType': habit_type,
            'name': name,
            'frequency': frequency,
            'targetValue': target_value,
            'targetUnit': target_unit,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_CREATED']
        )

    def publish_habit_logged(
        self,
        user_id: str,
        habit_id: str,
        log_id: str,
        habit_type: str,
        logged_at: datetime,
        data: Dict[str, Any]
    ) -> None:
        """Publish HABIT_LOGGED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'HABIT_LOGGED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'logId': log_id,
            'habitType': habit_type,
            'loggedAt': logged_at.isoformat() if isinstance(logged_at, datetime) else logged_at,
            'data': data,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_LOGGED']
        )

    def publish_food_logged(
        self,
        user_id: str,
        habit_id: str,
        log_id: str,
        meal_type: str,
        satisfaction: int,
        emotional_state: Optional[str],
        macros: Optional[Dict[str, float]],
        logged_at: datetime
    ) -> None:
        """Publish FOOD_LOGGED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'FOOD_LOGGED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'logId': log_id,
            'mealType': meal_type,
            'satisfaction': satisfaction,
            'emotionalState': emotional_state,
            'macros': macros,
            'loggedAt': logged_at.isoformat() if isinstance(logged_at, datetime) else logged_at,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_LOGGED']
        )

    def publish_exercise_logged(
        self,
        user_id: str,
        habit_id: str,
        log_id: str,
        activity_type: str,
        duration: int,
        rpe: int,
        post_energy: Optional[str],
        logged_at: datetime
    ) -> None:
        """Publish EXERCISE_LOGGED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'EXERCISE_LOGGED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'logId': log_id,
            'activityType': activity_type,
            'duration': duration,
            'rpe': rpe,
            'postEnergy': post_energy,
            'loggedAt': logged_at.isoformat() if isinstance(logged_at, datetime) else logged_at,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_LOGGED']
        )

    def publish_sleep_logged(
        self,
        user_id: str,
        habit_id: str,
        log_id: str,
        bedtime: datetime,
        wake_time: datetime,
        duration: int,
        quality: int,
        interruptions: int,
        logged_at: datetime
    ) -> None:
        """Publish SLEEP_LOGGED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'SLEEP_LOGGED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'logId': log_id,
            'bedtime': bedtime.isoformat() if isinstance(bedtime, datetime) else bedtime,
            'wakeTime': wake_time.isoformat() if isinstance(wake_time, datetime) else wake_time,
            'duration': duration,
            'quality': quality,
            'interruptions': interruptions,
            'loggedAt': logged_at.isoformat() if isinstance(logged_at, datetime) else logged_at,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_LOGGED']
        )

    def publish_study_logged(
        self,
        user_id: str,
        habit_id: str,
        log_id: str,
        task_id: Optional[str],
        duration: int,
        flow_state: bool,
        stickiness_percentage: int,
        logged_at: datetime
    ) -> None:
        """Publish STUDY_LOGGED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'STUDY_LOGGED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'logId': log_id,
            'taskId': task_id,
            'duration': duration,
            'flowState': flow_state,
            'stickinessPercentage': stickiness_percentage,
            'loggedAt': logged_at.isoformat() if isinstance(logged_at, datetime) else logged_at,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_LOGGED']
        )

    def publish_water_logged(
        self,
        user_id: str,
        habit_id: str,
        log_id: str,
        amount: int,
        urine_color: int,
        caffeine: bool,
        cognitive_fog: bool,
        logged_at: datetime
    ) -> None:
        """Publish WATER_LOGGED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'WATER_LOGGED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'logId': log_id,
            'amount': amount,
            'urineColor': urine_color,
            'caffeine': caffeine,
            'cognitiveFog': cognitive_fog,
            'loggedAt': logged_at.isoformat() if isinstance(logged_at, datetime) else logged_at,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_LOGGED']
        )

    def publish_streak_achieved(
        self,
        user_id: str,
        habit_id: str,
        habit_type: str,
        streak_days: int,
        milestone: bool
    ) -> None:
        """Publish STREAK_ACHIEVED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'STREAK_ACHIEVED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'habitType': habit_type,
            'streakDays': streak_days,
            'milestone': milestone,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_STREAK_ACHIEVED']
        )

    def publish_streak_broken(
        self,
        user_id: str,
        habit_id: str,
        habit_type: str,
        previous_streak: int,
        days_missed: int
    ) -> None:
        """Publish STREAK_BROKEN event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'STREAK_BROKEN',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'habitType': habit_type,
            'previousStreak': previous_streak,
            'daysMissed': days_missed,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_STREAK_BROKEN']
        )

    def publish_milestone_reached(
        self,
        user_id: str,
        habit_id: str,
        habit_type: str,
        milestone_type: str,
        value: int,
        description: str
    ) -> None:
        """Publish MILESTONE_REACHED event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventType': 'MILESTONE_REACHED',
            'timestamp': datetime.utcnow().isoformat(),
            'userId': user_id,
            'habitId': habit_id,
            'habitType': habit_type,
            'milestoneType': milestone_type,
            'value': value,
            'description': description,
            'metadata': {}
        }

        self._publish_event(
            event,
            RABBITMQ_CONFIG['EXCHANGES']['HABITS'],
            RABBITMQ_CONFIG['ROUTING_KEYS']['HABIT_MILESTONE']
        )


# Singleton instance
_publisher_instance = None


def get_event_publisher() -> EventPublisher:
    """Get the singleton EventPublisher instance"""
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = EventPublisher()
    return _publisher_instance
