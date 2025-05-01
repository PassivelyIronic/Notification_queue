import redis
from rq import Queue
import logging

from config.redis_conf import redis_config
from config.notification_conf import notification_config
from services.notification_sender import send_notification

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection
redis_conn = redis.Redis(
    host=redis_config['host'],
    port=redis_config['port']
)

# Creating queues
notification_queue = Queue('notifications', connection=redis_conn)
push_queue = Queue(notification_config['channels']['push']['queue_name'], connection=redis_conn)
mail_queue = Queue(notification_config['channels']['mail']['queue_name'], connection=redis_conn)

# Register functions with RQ
push_queue.enqueue_call = push_queue._create_job

# Function to schedule notification
def schedule_notification(notification_data, job_id=None, delay=0, priority=None, retry=None):
    """
    Schedule a notification for sending
    """
    logger.info(f"Scheduling notification for {notification_data['recipient']} via {notification_data['channel']}")
    
    # Set default retry if not specified
    if retry is None:
        retry = 3
    
    job = notification_queue.enqueue(
        send_notification,
        notification_data,
        job_id=job_id,
        result_ttl=86400,  # Results expire after 1 day
        failure_ttl=86400,  # Failed jobs expire after 1 day
        retry=retry,
        job_timeout=300,  # 5 minutes timeout
        priority=priority
    )
    
    logger.info(f"Notification scheduled with job ID: {job.id}")
    return job