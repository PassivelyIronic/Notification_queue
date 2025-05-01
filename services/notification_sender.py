# services/notification_sender.py
import random
import logging
from rq import get_current_job

logger = logging.getLogger(__name__)

def send_notification(notification_data):
    """
    Function responsible for sending notifications.
    This is the main entry point for the notification job.
    """
    job = get_current_job()
    logger.info(f"Processing notification job {job.id}")
    
    # Get notification details
    recipient = notification_data.get('recipient')
    content = notification_data.get('content')
    channel = notification_data.get('channel')
    
    # Simulate random failure (50% chance)
    if random.random() < 0.5:
        logger.warning(f"Sending failed for {channel} notification to {recipient}")
        raise Exception('Delivery failed (50% chance simulation)')
    
    # Log successful notification
    logger.info(f"Successfully sent {channel} notification to {recipient}: {content[:30]}...")
    
    return {
        "success": True,
        "job_id": job.id,
        "recipient": recipient,
        "channel": channel
    }