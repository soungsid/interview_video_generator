import logging
from typing import List, Optional, Dict, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from entities.persona import (
    Persona, PersonaResponse, PersonaCreate, PersonaUpdate,
    PersonaType, Language
)
from clients.ai_client import AIClient

logger = logging.getLogger(__name__)


class PersonaService:
    """Service for managing personas (interviewers and candidates)"""
    
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None):
        self.db = db
        self.personas_collection = db["personas"]
        self.ai_client = ai_client
    
    async def create_persona(self, persona_data: PersonaCreate) -> Persona:
        """Create a new persona"""
        persona = Persona(**persona_data.model_dump())
        await self.personas_collection.insert_one(persona.model_dump())
        logger.info(f"Created persona: {persona.name} ({persona.type})")
        return persona
    
    async def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get a persona by ID"""
        persona_dict = await self.personas_collection.find_one({"id": persona_id})
        if persona_dict:
            return Persona(**persona_dict)
        return None
    
    async def get_all_personas(self, active_only: bool = True) -> List[Persona]:
        """Get all personas"""
        query = {"is_active": True} if active_only else {}
        personas = []
        async for persona_dict in self.personas_collection.find(query):
            personas.append(Persona(**persona_dict))
        return personas
    
    async def get_personas_by_type(self, persona_type: PersonaType, active_only: bool = True) -> List[Persona]:
        """Get personas by type"""
        query = {"type": persona_type}
        if active_only:
            query["is_active"] = True
        
        personas = []
        async for persona_dict in self.personas_collection.find(query):
            personas.append(Persona(**persona_dict))
        return personas
    
    async def update_persona(self, persona_id: str, update_data: PersonaUpdate) -> Optional[Persona]:
        """Update a persona"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            return await self.get_persona(persona_id)
        
        result = await self.personas_collection.update_one(
            {"id": persona_id},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated persona: {persona_id}")
            return await self.get_persona(persona_id)
        return None
    
    async def delete_persona(self, persona_id: str) -> bool:
        """Delete a persona (soft delete by setting is_active to False)"""
        result = await self.personas_collection.update_one(
            {"id": persona_id},
            {"$set": {"is_active": False}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Deleted persona: {persona_id}")
            return True
        return False
    
    async def select_personas_for_topic(
        self, 
        topic: str, 
        language: Language = Language.ENGLISH,
        model: Optional[str] = None
    ) -> Tuple[Persona, Persona]:
        """
        Automatically select appropriate interviewer and candidate personas for a topic
        using AI to analyze the topic and match with available personas
        
        Args:
            topic: The interview topic
            language: Preferred language
            model: AI model to use for selection
        
        Returns:
            Tuple of (interviewer_persona, candidate_persona)
        """
        # Get all active personas
        all_personas = await self.get_all_personas(active_only=True)
        
        # Filter by language
        language_personas = [p for p in all_personas if p.language == language]
        
        if not language_personas:
            # Fallback to any language if no personas in requested language
            logger.warning(f"No personas found for language {language}, using all available")
            language_personas = all_personas
        
        # Separate by type
        interviewers = [p for p in language_personas if p.type == PersonaType.INTERVIEWER]
        candidates = [p for p in language_personas if p.type == PersonaType.CANDIDATE]
        
        if not interviewers or not candidates:
            raise ValueError("Not enough personas available. Need at least one interviewer and one candidate.")
        
        # Use AI to select the best interviewer
        if self.ai_client and len(interviewers) > 1:
            interviewer = await self._ai_select_interviewer(topic, interviewers, model)
        else:
            # Fallback: select first available
            interviewer = interviewers[0]
        
        # Select a candidate (can be generic)
        # For candidates, we can just pick one randomly or the first one
        candidate = candidates[0]
        
        logger.info(f"Selected personas - Interviewer: {interviewer.name} ({interviewer.specialty}), Candidate: {candidate.name}")
        return interviewer, candidate
    
    async def _ai_select_interviewer(
        self, 
        topic: str, 
        interviewers: List[Persona],
        model: Optional[str] = None
    ) -> Persona:
        """
        Use AI to select the most appropriate interviewer for the topic
        """
        # Build a description of available interviewers
        interviewer_descriptions = []
        for i, interviewer in enumerate(interviewers):
            desc = f"{i+1}. {interviewer.name} - Specialty: {interviewer.specialty or 'General'}, Personality: {', '.join(interviewer.personality_traits)}"
            interviewer_descriptions.append(desc)
        
        prompt = f"""Given the interview topic: "{topic}"

Select the most appropriate interviewer from this list:
{chr(10).join(interviewer_descriptions)}

Respond with ONLY the number (1, 2, 3, etc.) of the best interviewer for this topic."""
        
        messages = [
            {"role": "system", "content": "You are an expert at matching interview topics with appropriate interviewers based on their specialties."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.ai_client.generate_completion(messages, model, max_tokens=10)
            # Extract number from response
            import re
            match = re.search(r'\d+', response)
            if match:
                index = int(match.group()) - 1
                if 0 <= index < len(interviewers):
                    return interviewers[index]
        except Exception as e:
            logger.warning(f"AI selection failed: {e}. Using first interviewer.")
        
        # Fallback to first interviewer
        return interviewers[0]
    
    async def initialize_default_personas(self) -> List[Persona]:
        """
        Initialize default personas if none exist
        Creates 10 diverse personas with different specialties, voices, and personalities
        """
        existing_count = await self.personas_collection.count_documents({})
        if existing_count > 0:
            logger.info(f"Personas already exist ({existing_count}), skipping initialization")
            return []
        
        logger.info("Initializing default personas...")
        
        default_personas = [
            # Tech Interviewers
            PersonaCreate(
                name="Sarah",
                type=PersonaType.INTERVIEWER,
                specialty="Python",
                voice_id="Ruth",
                language=Language.ENGLISH,
                personality_traits=["encouraging", "patient", "detail-oriented"],
                description="A Python expert who loves teaching and encouraging candidates. Specializes in backend development and data science."
            ),
            PersonaCreate(
                name="Marcus",
                type=PersonaType.INTERVIEWER,
                specialty="Java Spring Boot",
                voice_id="Kevin",
                language=Language.ENGLISH,
                personality_traits=["professional", "serious", "thorough"],
                description="A seasoned Java architect with deep Spring Boot expertise. Very professional and detail-focused."
            ),
            PersonaCreate(
                name="Alex",
                type=PersonaType.INTERVIEWER,
                specialty="JavaScript React",
                voice_id="Justin",
                language=Language.ENGLISH,
                personality_traits=["dynamic", "modern", "enthusiastic"],
                description="A frontend specialist passionate about modern JavaScript and React. Energetic and up-to-date with latest trends."
            ),
            PersonaCreate(
                name="Emma",
                type=PersonaType.INTERVIEWER,
                specialty="DevOps",
                voice_id="Ivy",
                language=Language.ENGLISH,
                personality_traits=["practical", "direct", "solution-oriented"],
                description="A DevOps engineer focused on practical solutions and real-world scenarios. Direct and efficient communication style."
            ),
            
            # Business Interviewers
            PersonaCreate(
                name="David",
                type=PersonaType.INTERVIEWER,
                specialty="Finance",
                voice_id="Stephen",
                language=Language.ENGLISH,
                personality_traits=["analytical", "precise", "methodical"],
                description="A finance expert with strong analytical skills. Precise and methodical in his approach."
            ),
            PersonaCreate(
                name="Sophie",
                type=PersonaType.INTERVIEWER,
                specialty="Marketing",
                voice_id="Salli",
                language=Language.ENGLISH,
                personality_traits=["creative", "enthusiastic", "persuasive"],
                description="A marketing professional with creative flair. Enthusiastic and persuasive communication style."
            ),
            PersonaCreate(
                name="Jean",
                type=PersonaType.INTERVIEWER,
                specialty="Droit",
                voice_id="Remy",
                language=Language.FRENCH,
                personality_traits=["précis", "méthodique", "rigoureux"],
                description="Un expert en droit des affaires. Très précis et méthodique dans ses questions."
            ),
            
            # Generic Candidates
            PersonaCreate(
                name="Lisa",
                type=PersonaType.CANDIDATE,
                specialty=None,
                voice_id="Lea",
                language=Language.FRENCH,
                personality_traits=["confiante", "articulée", "adaptable"],
                description="Une candidate polyvalente avec une bonne capacité d'adaptation."
            ),
            PersonaCreate(
                name="Mike",
                type=PersonaType.CANDIDATE,
                specialty="Tech",
                voice_id="Kevin",
                language=Language.ENGLISH,
                personality_traits=["curious", "analytical", "eager-to-learn"],
                description="A tech-savvy candidate with strong problem-solving skills and eagerness to learn."
            ),
            PersonaCreate(
                name="Claire",
                type=PersonaType.CANDIDATE,
                specialty="Business",
                voice_id="Ruth",
                language=Language.ENGLISH,
                personality_traits=["adaptable", "confident", "strategic"],
                description="A business professional with strategic thinking and excellent communication skills."
            ),
        ]
        
        created_personas = []
        for persona_data in default_personas:
            persona = await self.create_persona(persona_data)
            created_personas.append(persona)
        
        logger.info(f"Created {len(created_personas)} default personas")
        return created_personas
