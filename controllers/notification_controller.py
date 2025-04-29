from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Dict, Any

from schemas.notification_schema import NotificationSchema
from services.notification_service import (
    create_notification, 
    force_send_notification, 
    remove_notification,
    get_notification_status
)

async def create_notification_handler(notification: NotificationSchema) -> Dict[str, Any]:
    try:
        result = create_notification(notification)
        return JSONResponse(
            status_code=201,
            content={"message": "Wiadomość utworzona i zakolejkowana", "data": result}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Error creating notification", "error": str(e)}
        )

async def force_send_notification_handler(id: str) -> Dict[str, Any]:
    try:
        if not id:
            raise HTTPException(status_code=400, detail="Wymagane id wiadomości")
        
        notification = force_send_notification(id)
        return JSONResponse(
            status_code=201,
            content={"message": "Wysłano wiadomość", "data": notification}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Błąd w trakcie wymuszania wysłania wiadomości", "error": str(e)}
        )

async def delete_notification_handler(id: str) -> Dict[str, Any]:
    try:
        if not id:
            raise HTTPException(status_code=400, detail="Wymagane id wiadomości")
        
        notification = remove_notification(id)
        return JSONResponse(
            status_code=201,
            content={"message": "Wiadomość usunięta pomyślnie", "data": notification}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Błąd w trakcie usuwania wiadomości", "error": str(e)}
        )

async def notification_status_handler(id: str) -> Dict[str, Any]:
    try:
        if not id:
            raise HTTPException(status_code=400, detail="Wymagane id wiadomości")
        
        result = get_notification_status(id)
        return JSONResponse(
            status_code=201,
            content={"message": f"Status wiadomości o id: {result['job_id']}: {result['status']}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Błąd w trakcie pobierania statusu wiadomości", "error": str(e)}
        )