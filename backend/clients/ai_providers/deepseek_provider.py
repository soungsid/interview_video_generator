import os
import logging
from typing import List, Optional
from openai import OpenAI
from fastapi import HTTPException

from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek AI provider"""
    
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        self.base_url = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        self.default_model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        logger.info(f"DeepSeekProvider initialized with model: {self.default_model}")
    
    def generate_completion(self, messages: List[dict], model: Optional[str] = None, max_tokens: int = 4000) -> str:
        """Generate a completion using DeepSeek"""
        try:
            model_to_use = model or self.default_model
            logger.info(f"DeepSeek generating completion with model: {model_to_use}")
            
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"DeepSeek completion generated: {len(content)} characters")
            return content
        except Exception as e:
            logger.error(f"DeepSeek error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"DeepSeek error: {str(e)}")
    
    def get_default_model(self) -> str:
        return self.default_model
