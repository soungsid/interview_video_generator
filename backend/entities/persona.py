from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import List, Optional
import uuid


class PersonaType(str, Enum):
    """Type of persona in the interview"""
    INTERVIEWER = "INTERVIEWER"
    CANDIDATE = "CANDIDATE"


class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    FRENCH = "fr"


class Persona(BaseModel):
    """Represents a persona (interviewer or candidate) with voice and personality"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: PersonaType
    specialty: Optional[str] = None  # For interviewers: "Python", "Java Spring Boot", etc.
    voice_id: str  # Amazon Polly Neural voice ID
    language: Language
    personality_traits: List[str] = Field(default_factory=list)  # ["encouraging", "professional", etc.]
    description: str = ""
    is_active: bool = True


class PersonaResponse(BaseModel):
    """Response model for persona"""
    id: str
    name: str
    type: PersonaType
    specialty: Optional[str] = None
    voice_id: str
    language: Language
    personality_traits: List[str]
    description: str
    is_active: bool


class PersonaCreate(BaseModel):
    """Request model for creating a persona"""
    name: str
    type: PersonaType
    specialty: Optional[str] = None
    voice_id: str
    language: Language
    personality_traits: List[str] = Field(default_factory=list)
    description: str = ""
    is_active: bool = True


class PersonaUpdate(BaseModel):
    """Request model for updating a persona"""
    name: Optional[str] = None
    specialty: Optional[str] = None
    voice_id: Optional[str] = None
    language: Optional[Language] = None
    personality_traits: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
