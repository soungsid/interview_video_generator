import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from config.dependencies import get_video_service

logger = logging.getLogger(__name__)

# Create a router for audio generation
audio_router = APIRouter(prefix="/api")


@audio_router.post("/audio/{video_id}/generate")
async def generate_audio(
    video_id: str
):
    """
    Generate audio files for a video and concatenate them.
    
    - Generates audio for introduction, all dialogues, and conclusion
    - Skips generation if audio file already exists (saves budget)
    - Concatenates all audio files in order
    - Analyzes dialogues to handle code snippets appropriately
    
    - **video_id**: The unique identifier of the video
    """
    try:
        from services.audio_service import AudioService
        from services.dialogue_analyzer_service import DialogueAnalyzerService
        
        logger.info(f"Received request to generate audio for video: {video_id}")
        
        video_service = await get_video_service()
        audio_service = AudioService()
        dialogue_analyzer = DialogueAnalyzerService()
        
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
            "failed": 0,
            "code_analyzed": 0
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
            
            # Analyze dialogue for code content
            dialogue_text = dialogue.text
            analysis_result = await dialogue_analyzer.analyze_and_enrich_dialogue(dialogue_text)
            
            if analysis_result["contains_code"]:
                stats["code_analyzed"] += 1
                dialogue_text = analysis_result["processed_text"]
                logger.info(f"Code detected in dialogue {filename}. Using processed text for audio.")
            
            if audio_service.generate_audio(dialogue_text, audio_path, role):
                stats["generated"] += 1
            elif audio_path.exists():
                stats["skipped"] += 1
            else:
                stats["failed"] += 1
            
            audio_files.append(audio_path)
        
        # Generate audio for conclusion
        conclusion_path = audio_dir / "99_conclusion.mp3"
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
            "final_audio_url": f"/api/audio/{video_id}/final_complete.mp3" if concatenation_success else None
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to generate audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")


@audio_router.get("/audio/{video_id}/{filename}")
async def get_audio(
    video_id: str, 
    filename: str
):
    """
    Retrieve audio file for a video.
    
    - **video_id**: The unique identifier of the video
    - **filename**: The audio filename (e.g., "final_complete.mp3", "01_youtuber.mp3")
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
