# services/notification_sender.py
import random
from queues.notification_queue import push_queue, mail_queue

def send_notification(notification_data):
    """
    Funkcja odpowiedzialna za wysyłanie powiadomień
    """
    # Symulacja losowego błędu (50% szansy)
    if random.random() < 0.5:
        raise Exception('Wysyłka zakończona niepowodzeniem (50% szans :P)')
    
    # Przekierowanie do odpowiedniej kolejki w zależności od kanału
    if notification_data['channel'] == 'push':
        push_queue.enqueue('send_push', notification_data)
    elif notification_data['channel'] == 'mail':
        mail_queue.enqueue('send_mail', notification_data)
    
    return {"success": True}