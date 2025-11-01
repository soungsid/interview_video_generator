from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from .dialogue import DialogueResponse
from .persona import Language


class Video(BaseModel):
    """Represents a complete interview video script"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    topic: str
    num_questions: int = 3  # Number of questions in the interview
    language: Language = Language.ENGLISH  # Language of the interview
    # Legacy fields - kept for backward compatibility with old videos
    introduction: Optional[str] = None
    introduction_audio_url: Optional[str] = None
    conclusion: str
    conclusion_audio_url: str = ""
    final_audio_url: str = ""  # URL to the concatenated full audio
    video_url: str = ""  # URL to the generated video file
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VideoWithDialogues(BaseModel):
    """Complete video with all dialogues"""
    id: str
    title: str
    topic: str
    num_questions: int
    language: Language
    # Legacy fields - kept for backward compatibility with old videos
    introduction: Optional[str] = None
    introduction_audio_url: Optional[str] = None
    conclusion: str
    conclusion_audio_url: str = ""
    final_audio_url: str = ""
    created_at: datetime
    dialogues: List[DialogueResponse]
