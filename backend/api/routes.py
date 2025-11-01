import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path

from entities.video import Video, VideoWithDialogues
from entities.requests import GenerateVideoRequest
from entities.generation_request import GenerationRequest
from entities.persona import Language
from config.dependencies import (
    get_script_service, get_video_service, get_database, 
    get_ai_provider, get_seo_service
)
from services.persona_service import PersonaService
from motor.motor_asyncio import AsyncIOMotorDatabase
from clients.ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


def get_persona_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
    ai_provider: BaseAIProvider = Depends(get_ai_provider)
) -> PersonaService:
    """Dependency to get PersonaService instance"""
    return PersonaService(db, ai_provider)


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
async def generate_video(
    request: GenerateVideoRequest,
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Generate a complete interview video script with introduction, dialogues, and conclusion.
    Automatically selects appropriate personas based on the topic and language.
    
    - **topic**: The subject of the interview (e.g., "Spring Boot Security", "Microservices")
    - **num_questions**: Number of interview questions (1-20)
    - **language**: Language for the interview (en or fr, default: en)
    - **model**: Optional AI model to use (defaults to configured model)
    - **max_tokens**: Maximum tokens per response (500-8000, default: 4000 for more detailed answers)
    """
    try:
        logger.info(f"Received request to generate video: topic={request.topic}, num_questions={request.num_questions}, language={request.language}, model={request.model}, max_tokens={request.max_tokens}")
        
        script_service = get_script_service()
        video_service = await get_video_service()
        seo_service = get_seo_service()
        db = get_database()
        
        # Select appropriate personas based on topic and language
        try:
            interviewer_persona, candidate_persona = await persona_service.select_personas_for_topic(
                topic=request.topic,
                language=request.language,
                model=request.model
            )
            logger.info(f"Selected personas: Interviewer={interviewer_persona.name}, Candidate={candidate_persona.name}")
        except ValueError as e:
            # If no personas available, initialize defaults first
            logger.warning(f"Persona selection failed: {e}. Initializing default personas...")
            await persona_service.initialize_default_personas()
            # Try again
            interviewer_persona, candidate_persona = await persona_service.select_personas_for_topic(
                topic=request.topic,
                language=request.language,
                model=request.model
            )
        
        # Generate SEO-friendly title
        seo_title = seo_service.generate_seo_title(
            topic=request.topic,
            language=request.language,
            num_questions=request.num_questions,
            model=request.model
        )
        logger.info(f"Generated SEO title: {seo_title}")
        
        # Generate script with conversation memory and personas
        script_data = script_service.generate_video_script(
            topic=request.topic,
            num_questions=request.num_questions,
            interviewer_persona=interviewer_persona,
            candidate_persona=candidate_persona,
            language=request.language,
            model=request.model,
            max_tokens=request.max_tokens
        )
        
        # Use SEO title instead of plain topic
        script_data['seo_title'] = seo_title
        
        # Save video to database with SEO title and additional fields
        video = await video_service.create_video(
            topic=request.topic,
            script_data=script_data,
            num_questions=request.num_questions,
            language=request.language
        )
        
        # Save generation request to database
        generation_request = GenerationRequest(
            topic=request.topic,
            num_questions=request.num_questions,
            language=request.language,
            model=request.model,
            max_tokens=request.max_tokens,
            interviewer_persona_id=interviewer_persona.id,
            candidate_persona_id=candidate_persona.id,
            video_id=video.id
        )
        await db["generation_requests"].insert_one(generation_request.model_dump())
        logger.info(f"Generation request saved with ID: {generation_request.id}")
        
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
        
        # Generate audio for introduction (legacy - only if video has introduction field)
        if video.introduction:
            intro_path = audio_dir / "00_introduction.mp3"
            if audio_service.generate_audio(video.introduction, intro_path, "interviewer"):
                stats["generated"] += 1
            elif intro_path.exists():
                stats["skipped"] += 1
            else:
                stats["failed"] += 1
            audio_files.append(intro_path)
        
        # Generate audio for each dialogue (including intro dialogues with question_number=0)
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
        conclusion_path = audio_dir / f"99_conclusion.mp3"
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
