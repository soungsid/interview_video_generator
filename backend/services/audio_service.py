import logging
import os
from pathlib import Path
from typing import List, Optional
from pydub import AudioSegment

from services.audio_providers.audio_provider_factory import AudioProviderFactory
from services.audio_providers.base_audio_provider import BaseAudioProvider

logger = logging.getLogger(__name__)


class AudioService:
    """Service for generating and managing audio files using multiple providers"""
    
    def __init__(self, provider_name: Optional[str] = None):
        """Initialize AudioService with specified provider or default from environment
        
        Args:
            provider_name: Name of audio provider (polly, openai-tts, elevenlabs)
                          If None, uses DEFAULT_AUDIO_PROVIDER from environment
        """
        self.provider_name = provider_name or os.environ.get('DEFAULT_AUDIO_PROVIDER', 'polly')
        self.provider: BaseAudioProvider = AudioProviderFactory.create_provider(self.provider_name)
        
        # Configure audio files directory
        audio_path = os.environ.get('AUDIO_FILES_PATH', './audio_files')
        self.audio_base_path = Path(audio_path).resolve()
        
        # Create directory if it doesn't exist
        self.audio_base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"AudioService initialized with provider: {self.provider_name}")
        logger.info(f"Audio files directory: {self.audio_base_path}")
    
    def generate_audio(self, text: str, output_path: Path, role: str = "interviewer", voice_id: Optional[str] = None) -> bool:
        """
        Generate audio from text using configured provider
        
        Args:
            text: Text to synthesize
            output_path: Path where audio file will be saved
            role: "interviewer" or "candidate" to select appropriate voice
            voice_id: Optional specific voice ID (if None, uses provider's default)
        
        Returns:
            True if audio was generated, False if file already exists or error occurred
        """
        # Get voice ID if not provided
        if voice_id is None:
            if role == "interviewer":
                voice_id = self.provider.get_default_interviewer_voice()
            else:
                voice_id = self.provider.get_default_candidate_voice()
        
        return self.provider.generate_audio(text, output_path, voice_id)
    
    def concatenate_audio_files(self, audio_paths: List[Path], output_path: Path) -> bool:
        """
        Concatenate multiple audio files into one
        
        Args:
            audio_paths: List of paths to audio files to concatenate
            output_path: Path where concatenated audio will be saved
        
        Returns:
            True if concatenation successful, False otherwise
        """
        try:
            logger.info(f"Concatenating {len(audio_paths)} audio files")
            
            # Filter only existing files
            existing_paths = [p for p in audio_paths if p.exists()]
            
            if not existing_paths:
                logger.warning("No audio files to concatenate")
                return False
            
            # Load first audio file
            combined = AudioSegment.from_mp3(existing_paths[0])
            
            # Add small pause between segments (500ms)
            pause = AudioSegment.silent(duration=500)
            
            # Concatenate all audio files with pauses
            for audio_path in existing_paths[1:]:
                combined = combined + pause + AudioSegment.from_mp3(audio_path)
            
            # Save concatenated audio
            output_path.parent.mkdir(parents=True, exist_ok=True)
            combined.export(output_path, format="mp3")
            
            logger.info(f"Concatenated audio saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to concatenate audio files: {str(e)}")
            return False
    
    def get_audio_base_path(self) -> Path:
        """Get base path for audio files"""
        return self.audio_base_path
    
    def get_video_audio_dir(self, video_id: str) -> Path:
        """Get audio directory for a specific video"""
        return self.get_audio_base_path() / video_id
    
    def generate_video_audio_url(self, video_id: str, filename: str) -> str:
        """Generate audio URL for API response"""
        return f"/api/videos/{video_id}/audio/{filename}"

    
    def generate_video_audio_url(self, video_id: str, filename: str) -> str:
        """Generate audio URL for API response"""
        return f"/api/videos/{video_id}/audio/{filename}"
