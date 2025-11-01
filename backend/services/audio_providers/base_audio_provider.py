from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseAudioProvider(ABC):
    """Base class for audio generation providers"""
    
    @abstractmethod
    def generate_audio(self, text: str, output_path: Path, voice_id: str) -> bool:
        """Generate audio from text
        
        Args:
            text: Text to synthesize
            output_path: Path where audio file will be saved
            voice_id: Voice ID or name to use
        
        Returns:
            True if audio was generated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_default_interviewer_voice(self) -> str:
        """Get default voice for interviewer"""
        pass
    
    @abstractmethod
    def get_default_candidate_voice(self) -> str:
        """Get default voice for candidate"""
        pass
