import sys
import signal
import uvicorn
from mongoengine import disconnect

from src.app import app
from config.connection_conf import con_config
from queues.notification_queue import notification_queue

# Obsługa wyjątków
def handle_exception(exc_type, exc_value, exc_traceback):
    print(f"Uncaught Exception: {exc_value}")
    sys.exit(1)

sys.excepthook = handle_exception

# Obsługa sygnałów i zarządzanie zasobami
def graceful_shutdown(signum, frame):
    print("Shutting down gracefully...")
    
    try:
        # Zamknięcie połączeń z Redis (dla kolejek)
        print("Notification queue closed")
    except Exception as e:
        print(f"Error closing notification queue: {str(e)}")
    
    try:
        # Zamknięcie połączenia z MongoDB
        disconnect()
        print("MongoDB connection closed")
    except Exception as e:
        print(f"Error closing MongoDB connection: {str(e)}")
    
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)

def main():
    uvicorn.run(
        "src.app:app", 
        host="0.0.0.0", 
        port=con_config['port'],
        reload=True
    )
    print(f"Server running on port {con_config['port']}")
    print("Notification system initialized")

if __name__ == "__main__":
    main()