import os
import logging
from pathlib import Path
from openai import OpenAI

from .base_audio_provider import BaseAudioProvider

logger = logging.getLogger(__name__)


class OpenAITTSProvider(BaseAudioProvider):
    """OpenAI Text-to-Speech provider"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_TTS_API_KEY')
        self.interviewer_voice = os.environ.get('OPENAI_TTS_VOICE_INTERVIEWER', 'onyx')
        self.candidate_voice = os.environ.get('OPENAI_TTS_VOICE_CANDIDATE', 'nova')
        
        if not self.api_key:
            logger.warning("OPENAI_TTS_API_KEY not configured - OpenAI TTS will be disabled")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAITTSProvider initialized")
    
    def generate_audio(self, text: str, output_path: Path, voice_id: str) -> bool:
        """Generate audio using OpenAI TTS"""
        if not self.client:
            logger.error("OpenAI TTS client not initialized")
            return False
        
        if output_path.exists():
            logger.info(f"Audio file already exists: {output_path}")
            return False
        
        try:
            logger.info(f"Generating audio with OpenAI TTS: voice={voice_id}, text_length={len(text)}")
            
            response = self.client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice=voice_id,
                input=text
            )
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            response.stream_to_file(output_path)
            
            logger.info(f"OpenAI TTS audio generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI TTS error: {str(e)}")
            return False
    
    def get_default_interviewer_voice(self) -> str:
        return self.interviewer_voice
    
    def get_default_candidate_voice(self) -> str:
        return self.candidate_voice
