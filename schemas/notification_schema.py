from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class NotificationSchema(BaseModel):
    content: str
    channel: Literal['push', 'mail']
    recipient: str
    timezone: str
    priority: Literal['low', 'high'] = 'low'
    scheduled_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }