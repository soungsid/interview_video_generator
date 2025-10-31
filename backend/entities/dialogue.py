from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import uuid


class Role(str, Enum):
    """Role in the interview conversation"""
    YOUTUBER = "YOUTUBER"
    CANDIDATE = "CANDIDATE"


class Dialogue(BaseModel):
    """Represents a single dialogue turn in an interview"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Role
    text: str
    question_number: int
    video_id: str


class DialogueResponse(BaseModel):
    """Response model for dialogue (without video_id)"""
    id: str
    role: Role
    text: str
    question_number: int
