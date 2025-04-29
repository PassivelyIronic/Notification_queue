# config/redis_conf.py
import os

redis_config = {
    'host': os.environ.get('REDIS_HOST', 'localhost'),
    'port': int(os.environ.get('REDIS_PORT', '6379'))
}