import os

redis_config = {
    'host': os.environ.get('REDIS_HOST', 'redis'),
    'port': int(os.environ.get('REDIS_PORT', '6379'))
}