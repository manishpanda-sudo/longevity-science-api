from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging
import time
from datetime import datetime
import os
from models import Base
from dependencies import engine, get_db
from routes import auth, admin, protected, biomarkers

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG level
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        # File handler - writes to file with date
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
        # Console handler - prints to terminal
        logging.StreamHandler()
    ]
)

# Create logger instance
# logger = logging.getLogger(__name__)

# Set SQLAlchemy logging to see database queries
# logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
# logging.getLogger("uvicorn").setLevel(logging.INFO)

# logger.info("=" * 60)
# logger.info("Initializing Longevity Biomarker API")
# logger.info("=" * 60)

# Create all tables
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(title="Longevity Biomarker API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(protected.router)
app.include_router(biomarkers.router)

# Root endpoints
@app.get("/")
def root():
    return {
        "message": "Longevity Biomarker API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):  # ← FIX: Use Depends, not next()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}