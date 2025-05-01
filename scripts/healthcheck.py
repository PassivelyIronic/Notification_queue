#!/usr/bin/env python3
import socket
import time
import sys
import redis
import os
import requests
from pymongo import MongoClient

def check_mongo():
    try:
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://mongo:27017/notification_manager') 
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
        client.server_info()
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

def check_redis():
    try:
        redis_host = os.environ.get('REDIS_HOST', 'redis')
        redis_port = int(os.environ.get('REDIS_PORT', '6379'))
        r = redis.Redis(host=redis_host, port=redis_port)
        r.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False

def check_api():
    try:
        response = requests.get('http://localhost:3100')
        return response.status_code < 500
    except:
        return False

if __name__ == "__main__":
    if check_mongo() and check_redis():
        sys.exit(0)
    else:
        sys.exit(1)