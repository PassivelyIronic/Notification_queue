from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class Notification(Document):
    content = StringField(required=True)
    channel = StringField(required=True, choices=['push', 'mail'])
    recipient = StringField(required=True)
    timezone = StringField(required=True)
    priority = StringField(required=True, choices=['low', 'high'], default='low')
    scheduled_at = DateTimeField(required=True)
    
    meta = {
        'collection': 'notifications',
        'indexes': [
            'recipient',
            'scheduled_at',
            'priority'
        ]
    }