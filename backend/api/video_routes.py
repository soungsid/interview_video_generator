import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from entities.requests import GenerateVideoRequest
from config.dependencies import get_video_service

logger = logging.getLogger(__name__)

# Create a router for video generation
video_router = APIRouter(prefix="/api")


@video_router.post("/video/{video_id}/generate")
async def generate_video(
    video_id: str
):
    """
    Generate complete video with visual elements from script and audio.
    
    This endpoint creates a full video with:
    - Animated background
    - Avatars of YouTuber and candidate (positioned in upper section)
    - Dynamic content zone (diagrams, images, code snippets, etc.)
    
    - **video_id**: The unique identifier of the video (must have audio already generated)
    """
    try:
        from services.video_generation_service import VideoGenerationService
        from services.audio_service import AudioService
        
        logger.info(f"Received request to generate video for: {video_id}")
        
        video_service = await get_video_service()
        audio_service = AudioService()
        video_generator = VideoGenerationService()
        
        # Get video with dialogues
        video = await video_service.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail=f"Video with id {video_id} not found")
        
        # Check if audio exists
        audio_dir = audio_service.get_video_audio_dir(video_id)
        final_audio_path = audio_dir / "final_complete.mp3"
        
        if not final_audio_path.exists():
            raise HTTPException(
                status_code=400, 
                detail="Audio not found. Please generate audio first using /api/audio/{video_id}/generate"
            )
        
        # Generate video
        await video_generator.generate_video(
            video=video,
            audio_path=final_audio_path,
            video_id=video_id
        )
        
        # Update video record with video URL
        await video_service.update_video_url(video_id, f"/api/video/{video_id}/file")
        
        logger.info(f"Video generation completed for video {video_id}")
        
        return {
            "status": "success",
            "message": "Video generation completed",
            "video_id": video_id,
            "video_url": f"/api/video/{video_id}/file"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to generate video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")


@video_router.get("/video/{video_id}/file")
async def get_video_file(
    video_id: str
):
    """
    Retrieve the generated video file.
    
    - **video_id**: The unique identifier of the video
    """
    try:
        from services.video_generation_service import VideoGenerationService
        
        video_generator = VideoGenerationService()
        video_path = video_generator.get_video_path(video_id)
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=f"interview_{video_id}.mp4"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to retrieve video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve video file")
