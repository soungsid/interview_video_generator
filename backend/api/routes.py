import logging
from fastapi import APIRouter, HTTPException
from typing import List

from entities.video import Video, VideoWithDialogues
from entities.requests import GenerateVideoRequest
from config.dependencies import get_script_service, get_video_service

logger = logging.getLogger(__name__)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    """API health check"""
    return {
        "message": "InterviewVideoGenerator API",
        "version": "1.0.0",
        "status": "running"
    }


@api_router.get("/health/database")
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
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@api_router.post("/videos/generate", response_model=VideoWithDialogues)
async def generate_video(request: GenerateVideoRequest):
    """
    Generate a complete interview video script with introduction, dialogues, and conclusion.
    
    - **topic**: The subject of the interview (e.g., "Spring Boot Security", "Microservices")
    - **num_questions**: Number of interview questions (1-20)
    - **model**: Optional AI model to use (defaults to configured model)
    """
    try:
        logger.info(f"Received request to generate video: topic={request.topic}, num_questions={request.num_questions}, model={request.model}")
        
        script_service = get_script_service()
        video_service = await get_video_service()
        
        # Generate script with conversation memory
        script_data = script_service.generate_video_script(
            topic=request.topic,
            num_questions=request.num_questions,
            model=request.model
        )
        
        # Save to database
        video = await video_service.create_video(request.topic, script_data)
        
        # Return complete video with dialogues
        return await video_service.get_video_by_id(video.id)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error generating video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")


@api_router.get("/videos/{video_id}", response_model=VideoWithDialogues)
async def get_video(video_id: str):
    """
    Retrieve a generated video with all its dialogues.
    
    - **video_id**: The unique identifier of the video
    """
    video_service = await get_video_service()
    video = await video_service.get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with id {video_id} not found")
    return video


@api_router.get("/videos", response_model=List[Video])
async def list_videos():
    """
    List all generated videos (without dialogues).
    Returns videos sorted by creation date (newest first).
    """
    video_service = await get_video_service()
    return await video_service.get_all_videos()
