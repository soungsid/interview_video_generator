import os
import logging
from typing import Optional

from .base_audio_provider import BaseAudioProvider
from .polly_audio_provider import PollyAudioProvider
from .openai_tts_provider import OpenAITTSProvider
from .elevenlabs_provider import ElevenLabsProvider

logger = logging.getLogger(__name__)


class AudioProviderFactory:
    """Factory for creating audio providers"""
    
    @staticmethod
    def create_provider(provider_name: Optional[str] = None) -> BaseAudioProvider:
        """Create an audio provider based on name or environment configuration
        
        Args:
            provider_name: Name of provider (polly, openai-tts, elevenlabs)
                          If None, uses DEFAULT_AUDIO_PROVIDER from environment
        
        Returns:
            Configured audio provider instance
        """
        # Get provider name from environment if not specified
        if provider_name is None:
            provider_name = os.environ.get('DEFAULT_AUDIO_PROVIDER', 'polly')
        
        provider_name = provider_name.lower()
        
        logger.info(f"Creating audio provider: {provider_name}")
        
        if provider_name == 'polly':
            return PollyAudioProvider()
        elif provider_name in ['openai-tts', 'openai_tts']:
            return OpenAITTSProvider()
        elif provider_name == 'elevenlabs':
            return ElevenLabsProvider()
        else:
            logger.warning(f"Unknown audio provider '{provider_name}', falling back to Polly")
            return PollyAudioProvider()
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available audio providers based on environment configuration"""
        providers = []
        
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            providers.append('polly')
        if os.environ.get('OPENAI_TTS_API_KEY'):
            providers.append('openai-tts')
        if os.environ.get('ELEVENLABS_API_KEY'):
            providers.append('elevenlabs')
        
        return providers
