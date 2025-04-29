import time
from config.redis_conf import redis_config
from config.notification_conf import notification_config
import redis
from rq import Queue, Worker, Connection

class MailService:
    async def send(self, recipient, content):
        print(f"Sending mail to {recipient}: {content}")
        
        # Symulacja wysyłki
        time.sleep(1)
        return {"success": True}

mail_service = MailService()

def send_mail(notification):
    mail_service.send(notification['recipient'], notification['content'])
    return {"success": True, "message": f"Mail sent to {notification['recipient']}"}

def setup_mail_worker():
    redis_conn = redis.Redis(
        host=redis_config['host'],
        port=redis_config['port']
    )
    
    queue_name = notification_config['channels']['mail']['queue_name']
    with Connection(redis_conn):
        worker = Worker([Queue(queue_name)])
        print("Mail notification worker started")
        worker.work()
    
    return worker

if __name__ == "__main__":
    setup_mail_worker()