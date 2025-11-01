import os
import logging
from typing import List, Optional

from clients.ai_providers.provider_factory import AIProviderFactory
from clients.ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class AIClient:
    """Client for interacting with multiple AI providers (DeepSeek, OpenAI, Gemini)"""
    
    def __init__(self, provider_name: Optional[str] = None):
        """Initialize AIClient with specified provider or default from environment
        
        Args:
            provider_name: Name of provider (deepseek, openai, gemini)
                          If None, uses DEFAULT_AI_PROVIDER from environment
        """
        self.provider_name = provider_name or os.environ.get('DEFAULT_AI_PROVIDER', 'deepseek')
        self.provider: BaseAIProvider = AIProviderFactory.create_provider(self.provider_name)
        logger.info(f"AIClient initialized with provider: {self.provider_name}")
    
    def generate_completion(self, messages: List[dict], model: Optional[str] = None, max_tokens: int = 4000) -> str:
        """Generate a completion using the configured AI provider
        
        Args:
            messages: Conversation history
            model: AI model to use (optional, uses provider's default if not specified)
            max_tokens: Maximum tokens in response (default: 4000)
        
        Returns:
            Generated text completion
        """
        return self.provider.generate_completion(messages, model, max_tokens)
    
    def get_default_model(self) -> str:
        """Get the default model for current provider"""
        return self.provider.get_default_model()
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available AI providers based on environment configuration"""
        return AIProviderFactory.get_available_providers()

