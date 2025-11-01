import os
import logging
from typing import List, Optional
import google.generativeai as genai
from fastapi import HTTPException

from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.default_model = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        logger.info(f"GeminiProvider initialized with model: {self.default_model}")
    
    def generate_completion(self, messages: List[dict], model: Optional[str] = None, max_tokens: int = 4000) -> str:
        """Generate a completion using Gemini"""
        try:
            model_to_use = model or self.default_model
            logger.info(f"Gemini generating completion with model: {model_to_use}")
            
            # Convert OpenAI format to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Create Gemini model
            gemini_model = genai.GenerativeModel(model_to_use)
            
            # Generate content
            response = gemini_model.generate_content(
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=max_tokens,
                )
            )
            
            content = response.text
            logger.info(f"Gemini completion generated: {len(content)} characters")
            return content
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")
    
    def _convert_messages_to_gemini_format(self, messages: List[dict]) -> str:
        """Convert OpenAI message format to Gemini format"""
        # For Gemini, we concatenate system and user messages into a single prompt
        formatted_parts = []
        
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'system':
                formatted_parts.append(f"System Instructions: {content}")
            elif role == 'user':
                formatted_parts.append(f"User: {content}")
            elif role == 'assistant':
                formatted_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(formatted_parts)
    
    def get_default_model(self) -> str:
        return self.default_model
