import os
import logging
from typing import Optional

from .base_provider import BaseAIProvider
from .deepseek_provider import DeepSeekProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """Factory for creating AI providers"""
    
    @staticmethod
    def create_provider(provider_name: Optional[str] = None) -> BaseAIProvider:
        """Create an AI provider based on name or environment configuration
        
        Args:
            provider_name: Name of provider (deepseek, openai, gemini)
                          If None, uses DEFAULT_AI_PROVIDER from environment
        
        Returns:
            Configured AI provider instance
        """
        # Get provider name from environment if not specified
        if provider_name is None:
            provider_name = os.environ.get('DEFAULT_AI_PROVIDER', 'deepseek')
        
        provider_name = provider_name.lower()
        
        logger.info(f"Creating AI provider: {provider_name}")
        
        if provider_name == 'deepseek':
            return DeepSeekProvider()
        elif provider_name == 'openai':
            return OpenAIProvider()
        elif provider_name == 'gemini':
            return GeminiProvider()
        else:
            logger.warning(f"Unknown provider '{provider_name}', falling back to DeepSeek")
            return DeepSeekProvider()
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available providers based on environment configuration"""
        providers = []
        
        if os.environ.get('DEEPSEEK_API_KEY'):
            providers.append('deepseek')
        if os.environ.get('OPENAI_API_KEY'):
            providers.append('openai')
        if os.environ.get('GEMINI_API_KEY'):
            providers.append('gemini')
        
        return providers
