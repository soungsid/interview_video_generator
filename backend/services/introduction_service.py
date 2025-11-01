import logging
import random
from typing import List

from clients.ai_providers.base_provider import BaseAIProvider
from entities.persona import Persona, Language
from entities.dialogue import Role

logger = logging.getLogger(__name__)


class IntroductionService:
    """Service for generating engaging introductions as structured dialogues"""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
    
    def generate_engaging_introduction(
        self,
        topic: str,
        interviewer_persona: Persona,
        candidate_persona: Persona,
        language: Language,
        model: str = None,
        max_tokens: int = 4000
    ) -> List[dict]:
        """Generate an engaging introduction as structured dialogues.
        
        Returns a list of 3 dialogue items:
        1. Engaging intro about the topic (YOUTUBER, question_number=0)
        2. Welcome to candidate by name (YOUTUBER, question_number=0)
        3. Candidate's response (CANDIDATE, question_number=0)
        
        Args:
            topic: The interview topic
            interviewer_persona: The interviewer persona
            candidate_persona: The candidate persona
            language: Language for the interview
            model: AI model to use (optional)
            max_tokens: Maximum tokens per response
        
        Returns:
            List of dialogue dictionaries with role, text, and question_number
        """
        lang_code = language.value
        
        # 1. Generate engaging introduction about topic
        intro_text = self._generate_engaging_hook(
            topic, interviewer_persona, lang_code, model, max_tokens
        )
        
        # 2. Generate welcome to candidate
        welcome_text = self._generate_candidate_welcome(
            candidate_persona, interviewer_persona, lang_code, model, max_tokens
        )
        
        # 3. Generate candidate's response
        candidate_response_text = self._generate_candidate_greeting_response(
            candidate_persona, interviewer_persona, lang_code, model, max_tokens
        )
        
        # Return as structured dialogues
        return [
            {
                "role": Role.YOUTUBER,
                "text": intro_text,
                "question_number": 0
            },
            {
                "role": Role.YOUTUBER,
                "text": welcome_text,
                "question_number": 0
            },
            {
                "role": Role.CANDIDATE,
                "text": candidate_response_text,
                "question_number": 0
            }
        ]
    
    def _generate_natural_intro(
        self,
        topic: str,
        interviewer_persona: Persona,
        language: str,
        model: str,
        max_tokens: int
    ) -> str:
        """Generate natural introduction without clichés"""
        personality_desc = ", ".join(interviewer_persona.personality_traits)
        
        system_prompt = f"""You are {interviewer_persona.name}, a professional YouTuber.
Your specialty: {interviewer_persona.specialty or 'general topics'}.
Your personality: {personality_desc}.
Speak in {language} language."""
        
        user_prompt = f"""Create a brief, engaging introduction (2-3 sentences) for a YouTube interview about {topic}.

IMPORTANT RULES:
- DO NOT use clichés like "Welcome to my channel", "Bienvenue sur ma chaîne", "Welcome back"
- Start directly with the topic or an interesting hook
- Be natural and conversational
- Show your personality: {personality_desc}
- Keep it short and engaging

Examples of GOOD intros:
- "Today we're exploring something fascinating: {topic}. I've got an expert here who's going to share some incredible insights."
- "Let's dive into {topic}. This is a topic that's been generating a lot of buzz lately."
- "I'm really excited about today's conversation on {topic}. We're going to uncover some interesting perspectives."

Return ONLY the introduction text."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.ai_provider.generate_completion(messages, model, max_tokens)
    
    def _generate_candidate_welcome(
        self,
        candidate_persona: Persona,
        interviewer_persona: Persona,
        language: str,
        model: str,
        max_tokens: int
    ) -> str:
        """Generate welcome message to candidate by name"""
        personality_desc = ", ".join(interviewer_persona.personality_traits)
        
        if language == 'fr':
            template = f"""Bienvenue {candidate_persona.name}! Comment allez-vous aujourd'hui?"""
        else:
            template = f"""Welcome {candidate_persona.name}! How are you doing today?"""
        
        return template
    
    def _generate_candidate_greeting_response(
        self,
        candidate_persona: Persona,
        interviewer_persona: Persona,
        language: str,
        model: str,
        max_tokens: int
    ) -> str:
        """Generate candidate's response to greeting"""
        personality_desc = ", ".join(candidate_persona.personality_traits)
        
        system_prompt = f"""You are {candidate_persona.name}, about to be interviewed.
Your personality: {personality_desc}.
Speak in {language} language."""
        
        if language == 'fr':
            greeting_question = f"L'interviewer {interviewer_persona.name} vous demande: Comment allez-vous aujourd'hui?"
        else:
            greeting_question = f"The interviewer {interviewer_persona.name} asks you: How are you doing today?"
        
        user_prompt = f"""{greeting_question}

Respond naturally and briefly (1-2 sentences). Show your personality: {personality_desc}.
Be friendly and professional.

Return ONLY your response."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.ai_provider.generate_completion(messages, model, max_tokens)
    
    def _generate_natural_transition(self, language: str) -> str:
        """Generate natural transition expression"""
        if language == 'fr':
            return random.choice(self.TRANSITIONS_FR)
        else:
            return random.choice(self.TRANSITIONS_EN)
