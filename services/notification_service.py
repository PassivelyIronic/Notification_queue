# services/notification_service.py
import time
import pytz
import logging
from datetime import datetime
from typing import Dict, Any

from schemas.notification_schema import NotificationSchema
from queues.notification_queue import notification_queue, schedule_notification
from models.notification_model import Notification
from config.notification_conf import ALLOWED_HOURS
from maps.notification_status_map import status_map

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_notification(data: NotificationSchema) -> Dict[str, Any]:
    try:
        # Validate timezone
        try:
            pytz.timezone(data.timezone)
        except Exception:
            raise ValueError(f"Invalid timezone: {data.timezone}")
        
        # Convert time from local to UTC
        local_tz = pytz.timezone(data.timezone)
        utc_tz = pytz.UTC
        
        # If scheduled_at is a string, convert to datetime
        if isinstance(data.scheduled_at, str):
            data.scheduled_at = datetime.fromisoformat(data.scheduled_at)
        
        # Add timezone info if it doesn't exist
        if data.scheduled_at.tzinfo is None:
            local_datetime = local_tz.localize(data.scheduled_at)
        else:
            local_datetime = data.scheduled_at
        
        # Convert to UTC
        utc_datetime = local_datetime.astimezone(utc_tz)
        
        # Check if time is in the future
        current_time = time.time()
        scheduled_time = utc_datetime.timestamp()
        
        if scheduled_time <= current_time:
            raise ValueError("Scheduled time must be in the future")
        
        # Check if delivery time is within allowed hours
        local_hour = local_datetime.hour
        
        if local_hour < ALLOWED_HOURS['start'] or local_hour >= ALLOWED_HOURS['end']:
            # Adjust time to allowed hours
            next_day = local_datetime.replace(hour=ALLOWED_HOURS['start'], minute=0, second=0, microsecond=0)
            adjusted_datetime = next_day.astimezone(utc_tz)
            
            logger.info(f"Adjusted delivery time due to quiet hours to {adjusted_datetime.isoformat()}")
            data.scheduled_at = adjusted_datetime
        else:
            data.scheduled_at = utc_datetime
        
        # Set notification priority
        notification_priority = 1 if data.priority == 'high' else 2
        
        # Calculate delay
        delay = int((data.scheduled_at.timestamp() - current_time) * 1000)  # delay in ms
        
        # Generate job_id
        job_id = f"{data.channel}-{data.recipient}-{data.scheduled_at.isoformat()}"
        
        # Save notification to database
        notification = Notification(
            content=data.content,
            channel=data.channel,
            recipient=data.recipient,
            timezone=data.timezone,
            priority=data.priority,
            scheduled_at=data.scheduled_at
        )
        notification.save()
        
        # Schedule notification
        notification_data = data.dict()
        job = schedule_notification(
            notification_data,
            job_id=job_id,
            delay=delay,
            priority=notification_priority,
            retry=3
        )
        
        return {
            "message": f"Created notification with ID: {job_id}",
            "job_id": job_id,
            "data": data.dict()
        }
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise

def force_send_notification(job_id: str) -> Dict[str, Any]:
    # Get job from queue
    job = notification_queue.fetch_job(job_id)
    
    if not job:
        raise ValueError(f"Notification with job_id: {job_id} not found")
    
    # Get notification data from job args
    notification_data = job.args[0] if job.args else None
    
    if not notification_data:
        raise ValueError(f"Invalid job data for job_id: {job_id}")
    
    # Remove old job
    notification_queue.remove(job_id)
    
    # Add new job with zero delay
    new_job = schedule_notification(
        notification_data,
        job_id=job_id,
        delay=0,
        retry=3
    )
    
    return {
        "message": "Forced immediate delivery",
        "job_id": job_id,
        "data": notification_data
    }

def remove_notification(job_id: str) -> Dict[str, Any]:
    job = notification_queue.fetch_job(job_id)
    
    if job:
        notification_queue.remove(job_id)
        return {"message": "Notification removed", "job_id": job_id}
    else:
        return {"message": "Notification not found with provided job_id", "job_id": job_id}

def get_notification_status(job_id: str) -> Dict[str, Any]:
    job = notification_queue.fetch_job(job_id)
    
    if not job:
        raise ValueError(f"Notification with job_id: {job_id} not found")
    
    state = job.get_status()
    status = status_map.get(state, state)
    
    return {
        "job_id": job_id,
        "status": status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None
    }