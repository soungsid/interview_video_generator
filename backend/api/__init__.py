from .health_routes import health_router
from .video_script_routes import video_script_router
from .audio_routes import audio_router
from .video_routes import video_router

__all__ = [
    "health_router",
    "video_script_router", 
    "audio_router",
    "video_router"
]
