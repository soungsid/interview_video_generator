import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from entities.video import Video, VideoWithDialogues
from entities.requests import GenerateVideoRequest
from entities.generation_request import GenerationRequest
from config.dependencies import (
    get_script_service, get_video_service, get_database, 
    get_ai_provider, get_seo_service
)
from services.persona_service import PersonaService
from motor.motor_asyncio import AsyncIOMotorDatabase
from clients.ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

# Create a router for video script generation
video_script_router = APIRouter(prefix="/api")


def get_persona_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
    ai_provider: BaseAIProvider = Depends(get_ai_provider)
) -> PersonaService:
    """Dependency to get PersonaService instance"""
    return PersonaService(db, ai_provider)


@video_script_router.post("/video-script", response_model=VideoWithDialogues)
async def generate_video_script(
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
        logger.info(f"Received request to generate video script: topic={request.topic}, num_questions={request.num_questions}, language={request.language}, model={request.model}, max_tokens={request.max_tokens}")
        
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
        logger.error(f"Unexpected error generating video script: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate video script: {str(e)}")


@video_script_router.get("/videos/{video_id}", response_model=VideoWithDialogues)
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


@video_script_router.get("/videos", response_model=List[Video])
async def list_videos():
    """
    List all generated videos (without dialogues).
    Returns videos sorted by creation date (newest first).
    """
    video_service = await get_video_service()
    return await video_service.get_all_videos()
