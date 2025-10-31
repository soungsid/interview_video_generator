from clients.ai_client import AIClient
from services.script_generation_service import ScriptGenerationService
from services.video_service import VideoService
from config.database import get_database

# Singleton instances
_ai_client = None
_script_service = None


def get_ai_client() -> AIClient:
    """Get or create AIClient singleton"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


def get_script_service() -> ScriptGenerationService:
    """Get or create ScriptGenerationService singleton"""
    global _script_service
    if _script_service is None:
        ai_client = get_ai_client()
        _script_service = ScriptGenerationService(ai_client)
    return _script_service


async def get_video_service() -> VideoService:
    """Get VideoService instance"""
    db = get_database()
    return VideoService(db)
