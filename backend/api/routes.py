import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path

from entities.video import Video, VideoWithDialogues
from entities.requests import GenerateVideoRequest
from entities.persona import Language
from config.dependencies import get_script_service, get_video_service, get_database, get_ai_client
from services.persona_service import PersonaService
from motor.motor_asyncio import AsyncIOMotorDatabase
from clients.ai_client import AIClient

logger = logging.getLogger(__name__)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


def get_persona_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
    ai_client: AIClient = Depends(get_ai_client)
) -> PersonaService:
    """Dependency to get PersonaService instance"""
    return PersonaService(db, ai_client)


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
    - **max_tokens**: Maximum tokens per response (500-8000, default: 4000 for more detailed answers)
    """
    try:
        logger.info(f"Received request to generate video: topic={request.topic}, num_questions={request.num_questions}, model={request.model}, max_tokens={request.max_tokens}")
        
        script_service = get_script_service()
        video_service = await get_video_service()
        
        # Generate script with conversation memory
        script_data = script_service.generate_video_script(
            topic=request.topic,
            num_questions=request.num_questions,
            model=request.model,
            max_tokens=request.max_tokens
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


@api_router.post("/videos/{video_id}/generate-audio")
async def generate_video_audio(video_id: str):
    """
    Generate audio files for a video and concatenate them.
    
    - Generates audio for introduction, all dialogues, and conclusion
    - Skips generation if audio file already exists (saves budget)
    - Concatenates all audio files in order
    """
    try:
        from services.audio_service import AudioService
        
        logger.info(f"Received request to generate audio for video: {video_id}")
        
        video_service = await get_video_service()
        audio_service = AudioService()
        
        # Get video with dialogues
        video = await video_service.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail=f"Video with id {video_id} not found")
        
        # Create audio directory for this video
        audio_dir = audio_service.get_video_audio_dir(video_id)
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        audio_files = []
        stats = {
            "generated": 0,
            "skipped": 0,
            "failed": 0
        }
        
        # Generate audio for introduction
        intro_path = audio_dir / "00_introduction.mp3"
        if audio_service.generate_audio(video.introduction, intro_path, "interviewer"):
            stats["generated"] += 1
        elif intro_path.exists():
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
        audio_files.append(intro_path)
        
        # Generate audio for each dialogue
        for dialogue in video.dialogues:
            role = "interviewer" if dialogue.role == "YOUTUBER" else "candidate"
            filename = f"{dialogue.question_number:02d}_{dialogue.role.lower()}.mp3"
            audio_path = audio_dir / filename
            
            if audio_service.generate_audio(dialogue.text, audio_path, role):
                stats["generated"] += 1
            elif audio_path.exists():
                stats["skipped"] += 1
            else:
                stats["failed"] += 1
            
            audio_files.append(audio_path)
        
        # Generate audio for conclusion
        conclusion_path = audio_dir / f"{len(video.dialogues)+1:02d}_conclusion.mp3"
        if audio_service.generate_audio(video.conclusion, conclusion_path, "interviewer"):
            stats["generated"] += 1
        elif conclusion_path.exists():
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
        audio_files.append(conclusion_path)
        
        # Concatenate all audio files
        final_audio_path = audio_dir / "final_complete.mp3"
        concatenation_success = audio_service.concatenate_audio_files(audio_files, final_audio_path)
        
        # Update video with audio URLs
        await video_service.update_video_audio_urls(video_id, audio_service)
        
        logger.info(f"Audio generation completed for video {video_id}: {stats}")
        
        return {
            "status": "success",
            "message": "Audio generation completed",
            "video_id": video_id,
            "stats": stats,
            "concatenation_success": concatenation_success,
            "final_audio_url": f"/api/videos/{video_id}/audio/final_complete.mp3" if concatenation_success else None
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to generate audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")


@api_router.get("/videos/{video_id}/audio/{filename}")
async def get_video_audio(video_id: str, filename: str):
    """
    Retrieve audio file for a video
    """
    try:
        from services.audio_service import AudioService
        audio_service = AudioService()
        
        audio_path = audio_service.get_video_audio_dir(video_id) / filename
        
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=filename
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to retrieve audio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audio file")
