from pydantic import BaseModel, Field
from typing import Optional


class GenerateVideoRequest(BaseModel):
    """Request to generate a video script"""
    topic: str = Field(..., description="The subject of the interview")
    num_questions: int = Field(
        ge=1, 
        le=20, 
        description="Number of interview questions (1-20)"
    )
    model: Optional[str] = Field(
        default=None, 
        description="AI model to use (optional, defaults to configured model)"
    )
