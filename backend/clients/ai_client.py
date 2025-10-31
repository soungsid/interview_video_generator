import os
import logging
from typing import List, Optional
from openai import OpenAI
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class AIClient:
    """Client for interacting with AI models (DeepSeek, OpenAI, etc.)"""
    
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        self.base_url = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        self.default_model = os.environ.get('DEFAULT_AI_MODEL', 'deepseek-chat')
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        logger.info(f"AIClient initialized with base_url: {self.base_url}, default_model: {self.default_model}")
    
    def generate_completion(self, messages: List[dict], model: Optional[str] = None) -> str:
        """Generate a completion using the AI model with conversation history"""
        try:
            model_to_use = model or self.default_model
            logger.info(f"Generating completion with model: {model_to_use}")
            logger.debug(f"Messages: {messages}")
            
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            logger.info(f"Completion generated successfully: {len(content)} characters")
            return content
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")
