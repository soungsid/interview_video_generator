import os
import logging
from pathlib import Path
from elevenlabs import ElevenLabs, VoiceSettings

from .base_audio_provider import BaseAudioProvider

logger = logging.getLogger(__name__)


class ElevenLabsProvider(BaseAudioProvider):
    """ElevenLabs audio provider"""
    
    def __init__(self):
        self.api_key = os.environ.get('ELEVENLABS_API_KEY')
        self.interviewer_voice = os.environ.get('ELEVENLABS_VOICE_INTERVIEWER', 'Brian')  # Expressive male voice
        self.candidate_voice = os.environ.get('ELEVENLABS_VOICE_CANDIDATE', 'Jessica')  # Professional female voice
        
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not configured - ElevenLabs will be disabled")
            self.client = None
        else:
            self.client = ElevenLabs(api_key=self.api_key)
            logger.info("ElevenLabsProvider initialized")
    
    def generate_audio(self, text: str, output_path: Path, voice_id: str) -> bool:
        """Generate audio using ElevenLabs"""
        if not self.client:
            logger.error("ElevenLabs client not initialized")
            return False
        
        if output_path.exists():
            logger.info(f"Audio file already exists: {output_path}")
            return False
        
        try:
            logger.info(f"Generating audio with ElevenLabs: voice={voice_id}, text_length={len(text)}")
            
            # Generate audio
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",  # Supports multiple languages
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.5,
                    use_speaker_boost=True
                )
            )
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio to file
            with open(output_path, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            logger.info(f"ElevenLabs audio generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"ElevenLabs error: {str(e)}")
            return False
    
    def get_default_interviewer_voice(self) -> str:
        return self.interviewer_voice
    
    def get_default_candidate_voice(self) -> str:
        return self.candidate_voice
