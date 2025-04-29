import time
from config.redis_conf import redis_config
from config.notification_conf import notification_config
import redis
from rq import Queue, Worker, Connection

class PushService:
    async def send(self, recipient, content):
        print(f"Sending push notification to {recipient}: {content}")
        
        # Symulacja wysyłki
        time.sleep(0.5)
        return {"success": True}

push_service = PushService()

def send_push(notification):
    push_service.send(notification['recipient'], notification['content'])
    return {"success": True, "message": f"Push notification sent to {notification['recipient']}"}

def setup_push_worker():
    redis_conn = redis.Redis(
        host=redis_config['host'],
        port=redis_config['port']
    )
    
    queue_name = notification_config['channels']['push']['queue_name']
    with Connection(redis_conn):
        worker = Worker([Queue(queue_name)])
        print("Push notification worker started")
        worker.work()
    
    return worker

if __name__ == "__main__":
    setup_push_worker()