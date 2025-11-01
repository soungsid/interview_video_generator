from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
from typing import Optional

from entities.persona import Language


class GenerationRequest(BaseModel):
    """Represents a video generation request stored in database"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    num_questions: int
    language: Language
    model: Optional[str] = None
    max_tokens: int = 4000
    interviewer_persona_id: Optional[str] = None
    candidate_persona_id: Optional[str] = None
    video_id: Optional[str] = None  # Link to generated video
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
