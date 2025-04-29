import time
import pytz
from datetime import datetime
from typing import Dict, Any
from schemas.notification_schema import NotificationSchema
from queues.notification_queue import notification_queue
from config.notification_conf import ALLOWED_HOURS
from maps.notification_status_map import status_map
import time
import pytz
from datetime import datetime
from typing import Dict, Any
from rq.job import Job

def create_notification(data: NotificationSchema) -> Dict[str, Any]:
    try:
        # Sprawdzenie poprawności strefy czasowej
        pytz.timezone(data.timezone)
    except Exception:
        raise ValueError(f"Błędna strefa czasowa: {data.timezone}")
    
    # Konwersja czasu z lokalnego na UTC
    local_tz = pytz.timezone(data.timezone)
    utc_tz = pytz.UTC
    
    # Zamiana na datetime w strefie lokalnej
    if isinstance(data.scheduled_at, str):
        data.scheduled_at = datetime.fromisoformat(data.scheduled_at)
    
    # Dodanie informacji o strefie czasowej jeśli jej nie ma
    if data.scheduled_at.tzinfo is None:
        local_datetime = local_tz.localize(data.scheduled_at)
    else:
        local_datetime = data.scheduled_at
    
    # Konwersja do UTC
    utc_datetime = local_datetime.astimezone(utc_tz)
    
    # Sprawdzenie czy czas jest w przyszłości
    current_time = time.time()
    scheduled_time = utc_datetime.timestamp()
    
    if scheduled_time <= current_time:
        raise ValueError("Czas wysyłki musi być w przyszłości")
    
    # Sprawdzenie czy czas wysyłki mieści się w dozwolonych godzinach
    local_hour = local_datetime.hour
    
    if local_hour < ALLOWED_HOURS['start'] or local_hour >= ALLOWED_HOURS['end']:
        # Dostosowanie czasu do dozwolonych godzin
        next_day = local_datetime.replace(hour=ALLOWED_HOURS['start'], minute=0, second=0, microsecond=0)
        adjusted_datetime = next_day.astimezone(utc_tz)
        
        print(f"Zmieniono czas wysyłki z względu na ciszę nocną {adjusted_datetime.isoformat()}")
        data.scheduled_at = adjusted_datetime
    else:
        data.scheduled_at = utc_datetime
    
    # Ustalenie priorytetu powiadomienia
    notification_priority = 1 if data.priority == 'high' else 2
    
    # Obliczenie opóźnienia
    delay = int((data.scheduled_at.timestamp() - current_time) * 1000)  # delay in ms
    
    # Generowanie job_id
    job_id = f"{data.channel}-{data.recipient}-{data.scheduled_at.isoformat()}"
    
    # Dodanie zadania do kolejki
    notification_queue.enqueue(
        'send_notification',
        data.dict(),
        job_id=job_id,
        delay=delay,
        retry=3,
        priority=notification_priority
    )
    
    return {
        "message": f"Utworzono/wysłano wiadomość o id: {job_id}",
        "data": data.dict()
    }

def force_send_notification(job_id: str) -> Dict[str, Any]:
    # Pobranie zadania z kolejki
    job = notification_queue.fetch_job(job_id)
    
    if not job:
        raise ValueError(f"Nie znaleziono wiadomości o job_id: {job_id}")
    
    notification_data = job.kwargs.get('args', [{}])[0]
    
    # Usuń stare zadanie
    notification_queue.remove(job_id)
    
    # Dodaj nowe zadanie z opóźnieniem 0
    notification_queue.enqueue(
        'send_notification',
        notification_data,
        job_id=job_id,
        delay=0,
        retry=3
    )
    
    return {
        "message": "Wymuszono wysłanie wiadomości",
        "data": notification_data
    }

def remove_notification(job_id: str) -> Dict[str, Any]:
    job = notification_queue.fetch_job(job_id)
    
    if job:
        notification_queue.remove(job_id)
        return {"message": "Usunięto wiadomość", "job_id": job_id}
    else:
        return {"message": "Nie znaleziono wiadomości o podanym job_id", "job_id": job_id}

def get_notification_status(job_id: str) -> Dict[str, Any]:
    job = notification_queue.fetch_job(job_id)
    
    if not job:
        raise ValueError(f"Nie znaleziono powiadomienia o job_id: {job_id}")
    
    state = job.get_status()
    status = status_map.get(state, state)
    
    return {
        "job_id": job_id,
        "status": status
    }