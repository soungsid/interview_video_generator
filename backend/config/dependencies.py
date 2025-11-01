from clients.ai_providers.provider_factory import AIProviderFactory
from clients.ai_providers.base_provider import BaseAIProvider
from services.script_generation_service import ScriptGenerationService
from services.video_service import VideoService
from services.seo_service import SEOService
from services.audio_service import AudioService
from config.database import get_database

# Singleton instances
_ai_provider = None
_script_service = None
_seo_service = None
_audio_service = None


def get_ai_provider() -> BaseAIProvider:
    """Get or create AI Provider singleton"""
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = AIProviderFactory.create_provider()
    return _ai_provider


def get_script_service() -> ScriptGenerationService:
    """Get or create ScriptGenerationService singleton"""
    global _script_service
    if _script_service is None:
        ai_provider = get_ai_provider()
        _script_service = ScriptGenerationService(ai_provider)
    return _script_service


def get_seo_service() -> SEOService:
    """Get or create SEOService singleton"""
    global _seo_service
    if _seo_service is None:
        ai_provider = get_ai_provider()
        _seo_service = SEOService(ai_provider)
    return _seo_service


def get_audio_service() -> AudioService:
    """Get or create AudioService singleton"""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service


async def get_video_service() -> VideoService:
    """Get VideoService instance"""
    db = get_database()
    return VideoService(db)

