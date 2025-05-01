import os

con_config = {
    'port': int(os.environ.get('APP_PORT', 3100)),
    'database': {
        'url': os.environ.get('MONGODB_URI', 'mongodb://mongo:27017/notification_manager'),
        'options': {
            'connect': True,
            'serverSelectionTimeoutMS': 5000
        }
    },
    'redis': {
        'host': os.environ.get('REDIS_HOST', 'redis'),
        'port': int(os.environ.get('REDIS_PORT', 6379))
    }
}