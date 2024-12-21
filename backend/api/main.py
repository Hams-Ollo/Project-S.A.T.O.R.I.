#-------------------------------------------------------------------------------------#
# main.py - FastAPI Backend Entry Point
#-------------------------------------------------------------------------------------#

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
import time
from typing import Callable
import sys
import signal
from contextlib import asynccontextmanager

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from core.logging.logger import create_logger
from core.websocket.manager import manager
from api.routes.websocket import router as websocket_router
from api.routes.voice import router as voice_router

# Initialize logger
logger = create_logger(
    name="satori.api",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_dir="logs"
)

# Load environment variables
load_dotenv()
logger.info("🔧 Loading environment variables")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    try:
        # Startup
        logger.info("🚀 Starting S.A.T.O.R.I. AI backend server")
        
        # Log environment details
        env_details = {
            "Environment": os.getenv("ENVIRONMENT", "development"),
            "API Version": os.getenv("API_VERSION", "0.1.0"),
            "Debug Mode": os.getenv("DEBUG", "False"),
            "Host": os.getenv("API_HOST", "0.0.0.0"),
            "Port": os.getenv("API_PORT", 8000)
        }
        
        for key, value in env_details.items():
            logger.info(f"📌 {key}: {value}")
        
        logger.info("✨ Server is ready to accept connections")
        yield
        
        # Shutdown
        logger.info("🔄 Initiating graceful shutdown")
        await manager.shutdown()
        logger.info("👋 S.A.T.O.R.I. AI backend server shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Error during server lifecycle: {str(e)}")
        raise

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="S.A.T.O.R.I. AI",
    description="System for Agentic Tasks, Orchestration, and Real-time Intelligence",
    version="0.1.0",
    lifespan=lifespan
)

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}")
    logger.info("Initiating graceful shutdown...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handle termination

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Log incoming requests and their processing time"""
    start_time = time.time()
    
    # Log request details
    logger.debug(f"📥 Incoming {request.method} request to {request.url.path}")
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"✨ {request.method} {request.url.path} completed in {process_time:.2f}ms "
            f"(Status: {response.status_code})"
        )
        return response
    except Exception as e:
        logger.error(
            f"❌ Error processing {request.method} {request.url.path}: {str(e)}",
            exc_info=True
        )
        raise

# Configure CORS
logger.info("🔒 Configuring CORS settings")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket routes
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])

# Include Voice routes
app.include_router(voice_router, prefix="/voice", tags=["voice"])

@app.get("/")
async def root():
    """Root endpoint returning API status"""
    logger.debug("📡 Processing root endpoint request")
    return {
        "message": "Welcome to S.A.T.O.R.I. AI",
        "status": "operational",
        "version": "0.1.0",
        "websocket_enabled": True
    }

if __name__ == "__main__":
    logger.info(f"🌟 Starting server on {os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', 8000)}")
    
    try:
        # Configure uvicorn logging to use our logger
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
        
        uvicorn.run(
            "main:app",
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", 8000)),
            reload=True,
            log_level="info",
            log_config=log_config
        )
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise
    finally:
        logger.info("Server shutdown complete") 