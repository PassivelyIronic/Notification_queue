from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import redis
from rq import Queue

from config.redis_conf import redis_config
from config.notification_conf import notification_config

# Connect to Redis
redis_conn = redis.Redis(
    host=redis_config['host'],
    port=redis_config['port']
)

# Access queues
push_queue = Queue(notification_config['channels']['push']['queue_name'], connection=redis_conn)
mail_queue = Queue(notification_config['channels']['mail']['queue_name'], connection=redis_conn)
notification_queue = Queue('notifications', connection=redis_conn)

async def get_metrics_handler(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)")
):
    try:
        # Default to last 24 hours if dates not provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Convert to datetime objects
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Get queue statistics
        queue_stats = {
            'push': {
                'pending': len(push_queue),
                'total_jobs': push_queue.count,
                'failed': len(push_queue.failed_job_registry),
                'completed': len(push_queue.finished_job_registry),
            },
            'mail': {
                'pending': len(mail_queue),
                'total_jobs': mail_queue.count,
                'failed': len(mail_queue.failed_job_registry),
                'completed': len(mail_queue.finished_job_registry),
            },
            'notifications': {
                'pending': len(notification_queue),
                'total_jobs': notification_queue.count,
                'failed': len(notification_queue.failed_job_registry),
                'completed': len(notification_queue.finished_job_registry),
            }
        }
        
        # Format queue stats for output
        metrics = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'queues': queue_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return JSONResponse(
            status_code=200,
            content=metrics
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Error retrieving metrics", "error": str(e)}
        )