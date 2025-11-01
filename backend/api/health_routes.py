import logging
from fastapi import APIRouter
from config.dependencies import get_video_service

logger = logging.getLogger(__name__)

# Create a router with the /api prefix
health_router = APIRouter(prefix="/api")


@health_router.get("/")
async def root():
    """API health check"""
    return {
        "message": "InterviewVideoGenerator API",
        "version": "2.0.0",
        "status": "running"
    }


@health_router.get("/health")
async def health_check():
    """General health check"""
    return {
        "status": "healthy",
        "message": "API is running"
    }


@health_router.get("/health/database")
async def check_database():
    """Check MongoDB connection health"""
    try:
        video_service = await get_video_service()
        # Try to ping the database
        await video_service.db.command('ping')
        return {
            "status": "healthy",
            "message": "MongoDB connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
