from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from entities.persona import (
    PersonaResponse, PersonaCreate, PersonaUpdate,
    PersonaType, Language
)
from services.persona_service import PersonaService
from config.dependencies import get_database, get_ai_provider
from motor.motor_asyncio import AsyncIOMotorDatabase
from clients.ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personas", tags=["personas"])


def get_persona_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
    ai_provider: BaseAIProvider = Depends(get_ai_provider)
) -> PersonaService:
    """Dependency to get PersonaService instance"""
    return PersonaService(db, ai_provider)


@router.post("", response_model=PersonaResponse, status_code=201)
async def create_persona(
    persona_data: PersonaCreate,
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Create a new persona
    
    - **name**: Name of the persona
    - **type**: INTERVIEWER or CANDIDATE
    - **specialty**: Specialty for interviewers (e.g., "Python", "Finance")
    - **voice_id**: Amazon Polly Neural voice ID
    - **language**: Language code (en or fr)
    - **personality_traits**: List of personality traits
    - **description**: Description of the persona
    """
    try:
        persona = await persona_service.create_persona(persona_data)
        return PersonaResponse(**persona.model_dump())
    except Exception as e:
        logger.error(f"Error creating persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[PersonaResponse])
async def get_all_personas(
    active_only: bool = True,
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Get all personas
    
    - **active_only**: If True, only return active personas
    """
    try:
        personas = await persona_service.get_all_personas(active_only=active_only)
        return [PersonaResponse(**p.model_dump()) for p in personas]
    except Exception as e:
        logger.error(f"Error fetching personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/type/{persona_type}", response_model=List[PersonaResponse])
async def get_personas_by_type(
    persona_type: PersonaType,
    active_only: bool = True,
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Get personas by type (INTERVIEWER or CANDIDATE)
    
    - **persona_type**: Type of personas to retrieve
    - **active_only**: If True, only return active personas
    """
    try:
        personas = await persona_service.get_personas_by_type(persona_type, active_only)
        return [PersonaResponse(**p.model_dump()) for p in personas]
    except Exception as e:
        logger.error(f"Error fetching personas by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Get a specific persona by ID
    
    - **persona_id**: ID of the persona to retrieve
    """
    persona = await persona_service.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return PersonaResponse(**persona.model_dump())


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: str,
    update_data: PersonaUpdate,
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Update a persona
    
    - **persona_id**: ID of the persona to update
    - Only provided fields will be updated
    """
    persona = await persona_service.update_persona(persona_id, update_data)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return PersonaResponse(**persona.model_dump())


@router.delete("/{persona_id}", status_code=204)
async def delete_persona(
    persona_id: str,
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Delete a persona (soft delete)
    
    - **persona_id**: ID of the persona to delete
    """
    success = await persona_service.delete_persona(persona_id)
    if not success:
        raise HTTPException(status_code=404, detail="Persona not found")
    return None


@router.post("/initialize-defaults", response_model=List[PersonaResponse])
async def initialize_default_personas(
    persona_service: PersonaService = Depends(get_persona_service)
):
    """
    Initialize default personas if none exist
    
    Creates 10 diverse personas with different specialties, voices, and personalities
    """
    try:
        personas = await persona_service.initialize_default_personas()
        return [PersonaResponse(**p.model_dump()) for p in personas]
    except Exception as e:
        logger.error(f"Error initializing default personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
