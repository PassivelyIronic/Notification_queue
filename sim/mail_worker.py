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
mail_stats = {
    'sent': 0,
    'failed': 0,
    'pending': 0
}

class MailService:
    def send(self, recipient, content):
        logger.info(f"Sending mail to {recipient}: {content[:30]}...")
        
        # Simulate delivery
        time.sleep(1)
        
        # 50% chance of success
        if random.random() < 0.5:
            mail_stats['sent'] += 1
            logger.info(f"Mail sent successfully to {recipient}")
            return {"success": True}
        else:
            mail_stats['failed'] += 1
            logger.error(f"Failed to send mail to {recipient}")
            raise Exception("Mail delivery failed (simulation)")

mail_service = MailService()

def send_mail(notification):
    try:
        mail_stats['pending'] += 1
        result = mail_service.send(notification['recipient'], notification['content'])
        mail_stats['pending'] -= 1
        return {"success": True, "message": f"Mail sent to {notification['recipient']}"}
    except Exception as e:
        mail_stats['pending'] -= 1
        logger.error(f"Error sending mail: {str(e)}")
        raise

def get_mail_stats():
    return mail_stats

def setup_mail_worker():
    redis_conn = redis.Redis(
        host=redis_config['host'],
        port=redis_config['port']
    )
    
    queue_name = notification_config['channels']['mail']['queue_name']
    with Connection(redis_conn):
        worker = Worker([Queue(queue_name)])
        logger.info("Mail notification worker started")
        worker.work()
    
    return worker

if __name__ == "__main__":
    setup_mail_worker()