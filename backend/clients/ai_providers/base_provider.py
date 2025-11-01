from abc import ABC, abstractmethod
from typing import List, Optional


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    def generate_completion(self, messages: List[dict], model: Optional[str] = None, max_tokens: int = 4000) -> str:
        """Generate a completion using the AI model
        
        Args:
            messages: Conversation history
            model: AI model to use (optional)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model for this provider"""
        pass
