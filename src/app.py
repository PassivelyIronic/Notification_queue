from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect
import uvicorn
import logging

from config.connection_conf import con_config
from routes.notification_routes import router as notification_router
from routes.metrics_routes import router as metrics_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class App:
    def __init__(self):
        self.app = FastAPI(
            title="Notification Queue Service",
            description="Service for scheduling and delivering notifications",
            version="1.0.0"
        )
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
        self.app.include_router(metrics_router, prefix="/api/v1")
        
        @self.app.get("/")
        async def root():
            return {"message": "Notification Queue Service", "status": "running"}
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}
    
    def connect_to_database(self):
        try:
            connect(
                host=con_config['database']['url'],
                **con_config['database']['options']
            )
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            import sys
            sys.exit(1)

app_instance = App()
app = app_instance.app