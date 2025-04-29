notification_config = {
    'channels': {
        'push': {
            'queue_name': 'push-notifications',
            'concurrency': 10,
            'rate_limiter': {
                'max': 100,
                'duration': 1000
            }
        },
        'mail': {
            'queue_name': 'mail-notifications',
            'concurrency': 5,
            'rate_limiter': {
                'max': 50,
                'duration': 1000
            }
        }
    }
}

ALLOWED_HOURS = {
    'start': 8,
    'end': 22
}