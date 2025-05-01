import time
import logging
import random
from config.redis_conf import redis_config
from config.notification_conf import notification_config
import redis
from rq import Queue, Worker, Connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stats counters
push_stats = {
    'sent': 0,
    'failed': 0,
    'pending': 0
}

class PushService:
    def send(self, recipient, content):
        logger.info(f"Sending push notification to {recipient}: {content[:30]}...")
        
        # Simulate delivery
        time.sleep(0.5)
        
        # 50% chance of success
        if random.random() < 0.5:
            push_stats['sent'] += 1
            logger.info(f"Push notification sent successfully to {recipient}")
            return {"success": True}
        else:
            push_stats['failed'] += 1
            logger.error(f"Failed to send push notification to {recipient}")
            raise Exception("Push notification delivery failed (simulation)")

push_service = PushService()

def send_push(notification):
    try:
        push_stats['pending'] += 1
        result = push_service.send(notification['recipient'], notification['content'])
        push_stats['pending'] -= 1
        return {"success": True, "message": f"Push notification sent to {notification['recipient']}"}
    except Exception as e:
        push_stats['pending'] -= 1
        logger.error(f"Error sending push notification: {str(e)}")
        raise

def get_push_stats():
    return push_stats

def setup_push_worker():
    redis_conn = redis.Redis(
        host=redis_config['host'],
        port=redis_config['port']
    )
    
    queue_name = notification_config['channels']['push']['queue_name']
    with Connection(redis_conn):
        worker = Worker([Queue(queue_name)])
        logger.info("Push notification worker started")
        worker.work()
    
    return worker

if __name__ == "__main__":
    setup_push_worker()