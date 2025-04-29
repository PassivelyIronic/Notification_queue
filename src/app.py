from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect
import uvicorn

from config.connection_conf import con_config
from routes.notification_routes import router as notification_router

class App:
    def __init__(self):
        self.app = FastAPI(title="Notification Queue Service")
        self.configure_middleware()
        self.configure_routes()
        self.connect_to_database()
    
    def configure_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def configure_routes(self):
        self.app.include_router(notification_router, prefix="/api/v1")
    
    def connect_to_database(self):
        try:
            connect(
                host=con_config['database']['url'],
                **con_config['database']['options']
            )
            print("Connected to MongoDB")
        except Exception as e:
            print(f"MongoDB connection error: {str(e)}")
            import sys
            sys.exit(1)

app_instance = App()
app = app_instance.app