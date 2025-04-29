import redis
from rq import Queue, Worker, Connection
from rq.job import Job
import random

from config.redis_conf import redis_config
from config.notification_conf import notification_config

# Połączenie Redis
redis_conn = redis.Redis(
    host=redis_config['host'],
    port=redis_config['port']
)

# Tworzenie kolejek
notification_queue = Queue('notifications', connection=redis_conn)
push_queue = Queue(notification_config['channels']['push']['queue_name'], connection=redis_conn)
mail_queue = Queue(notification_config['channels']['mail']['queue_name'], connection=redis_conn)

# Funkcja do przetwarzania powiadomień
def process_notification(notification_data):
    # Symulacja losowego błędu (50% szansy)
    if random.random() < 0.5:
        raise Exception('Wysyłka zakończona niepowodzeniem (50% szans :P)')
    
    # Przekierowanie do odpowiedniej kolejki w zależności od kanału
    if notification_data['channel'] == 'push':
        push_queue.enqueue('send_push', notification_data)
    elif notification_data['channel'] == 'mail':
        mail_queue.enqueue('send_mail', notification_data)
    
    return {"success": True}