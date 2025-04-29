import requests
import json
from datetime import datetime, timedelta

API_URL = 'http://localhost:3100/api/v1/notifications'

push_notification = {
    "content": "Testowe powiadomienie push",
    "channel": "push",
    "recipient": "user123",
    "timezone": "Europe/Warsaw",
    "priority": "high",
    "scheduled_at": (datetime.now() + timedelta(minutes=1)).isoformat()
}

mail_notification = {
    "content": "Testowe powiadomienie mail",
    "channel": "mail",
    "recipient": "user@example.com",
    "timezone": "Europe/Warsaw",
    "priority": "low",
    "scheduled_at": (datetime.now() + timedelta(minutes=2)).isoformat()
}

def send_notification(notification):
    try:
        response = requests.post(API_URL, json=notification)
        response.raise_for_status()
        print('Notification created:', response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response:
            print('Error creating notification:', e.response.json())
        else:
            print('Error creating notification:', str(e))
        return None

def run_test():
    push_result = send_notification(push_notification)
    mail_result = send_notification(mail_notification)
    
    # Opcjonalnie: sprawdzenie statusu po utworzeniu
    if push_result and 'data' in push_result:
        job_id = push_result['data'].get('job_id')
        if job_id:
            try:
                status_response = requests.get(f"{API_URL}/status/{job_id}")
                print(f"Status of push notification: {status_response.json()}")
            except Exception as e:
                print(f"Error checking status: {str(e)}")

if __name__ == "__main__":
    run_test()