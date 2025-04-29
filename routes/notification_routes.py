from fastapi import APIRouter, Path
from controllers.notification_controller import (
    create_notification_handler,
    force_send_notification_handler,
    delete_notification_handler,
    notification_status_handler
)
from schemas.notification_schema import NotificationSchema

router = APIRouter()

router.post("/notifications", response_model=dict)(create_notification_handler)
router.put("/notifications/{id}", response_model=dict)(force_send_notification_handler)
router.delete("/notifications/{id}", response_model=dict)(delete_notification_handler)
router.get("/notifications/status/{id}", response_model=dict)(notification_status_handler)