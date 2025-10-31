from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime, timezone
import uuid

from .dialogue import DialogueResponse


class Video(BaseModel):
    """Represents a complete interview video script"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    topic: str
    introduction: str
    conclusion: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VideoWithDialogues(BaseModel):
    """Complete video with all dialogues"""
    id: str
    title: str
    topic: str
    introduction: str
    conclusion: str
    created_at: datetime
    dialogues: List[DialogueResponse]
