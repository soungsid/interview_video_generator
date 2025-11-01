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
    
    def _generate_engaging_hook(
        self,
        topic: str,
        interviewer_persona: Persona,
        language: str,
        model: str,
        max_tokens: int
    ) -> str:
        """Generate an engaging hook/introduction that captures attention"""
        personality_desc = ", ".join(interviewer_persona.personality_traits)
        
        system_prompt = f"""You are {interviewer_persona.name}, a professional YouTuber creating engaging content.
Your specialty: {interviewer_persona.specialty or 'general topics'}.
Your personality: {personality_desc}.
Speak in {language} language."""
        
        if language == 'fr':
            user_prompt = f"""Créez une introduction captivante (2-3 phrases) pour une interview YouTube sur {topic}.

RÈGLES IMPORTANTES:
- N'utilisez PAS de clichés comme "Bienvenue sur ma chaîne", "Bonjour à tous", "Aujourd'hui on va parler de"
- Commencez par une question intrigante ou un fait surprenant qui crée du suspense
- Soyez professionnel et engageant
- Montrez votre personnalité: {personality_desc}
- Gardez ça court mais percutant

Exemples d'EXCELLENTES intros (à adapter au sujet):
- "Vous êtes-vous déjà demandé comment [aspect fascinant du {topic}]? Ce n'est pas de la magie — c'est [explication courte]. Aujourd'hui, nous allons découvrir ce qui se cache vraiment derrière."
- "La plupart des développeurs utilisent [outil/concept lié à {topic}] tous les jours — mais combien comprennent vraiment comment ça fonctionne en coulisses? La réponse pourrait vous surprendre."
- "Imaginez pouvoir [bénéfice lié à {topic}] en quelques lignes de code. C'est exactement ce que nous allons explorer aujourd'hui."

IMPORTANT: NE PAS mentionner le candidat dans cette partie. Retournez UNIQUEMENT le texte d'introduction."""
        else:
            user_prompt = f"""Create a captivating introduction (2-3 sentences) for a YouTube interview about {topic}.

IMPORTANT RULES:
- DO NOT use clichés like "Welcome to my channel", "Hi everyone", "Today we're going to talk about"
- Start with an intriguing question or surprising fact that creates suspense
- Be professional and engaging
- Show your personality: {personality_desc}
- Keep it short but impactful

Examples of EXCELLENT intros (adapt to your topic):
- "Have you ever wondered how [fascinating aspect of {topic}]? That's not magic — it's [short explanation]. Today, we'll uncover what's really happening behind the scenes."
- "Most developers use [tool/concept related to {topic}] every day — but how many actually understand how it works under the hood? The answer might surprise you."
- "Imagine being able to [benefit related to {topic}] with just a few lines of code. That's exactly what we're exploring today."

IMPORTANT: DO NOT mention the candidate in this part. Return ONLY the introduction text."""
        
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
        """Generate welcome message to candidate by name and brief introduction"""
        personality_desc = ", ".join(interviewer_persona.personality_traits)
        
        system_prompt = f"""You are {interviewer_persona.name}, welcoming your guest to the interview.
Your personality: {personality_desc}.
Speak in {language} language."""
        
        if language == 'fr':
            user_prompt = f"""Accueillez votre invité {candidate_persona.name} de manière naturelle et professionnelle.

Présentez brièvement qui il/elle est (sans entrer dans trop de détails) et demandez-lui comment il/elle va.

Format suggéré:
"Avec moi aujourd'hui, [Candidate Name], [brève présentation]. Bienvenue [Candidate Name]! Comment allez-vous?"

Soyez naturel et montrez votre personnalité: {personality_desc}.
Gardez ça court (2-3 phrases maximum).

Retournez UNIQUEMENT le texte de bienvenue."""
        else:
            user_prompt = f"""Welcome your guest {candidate_persona.name} in a natural and professional way.

Briefly introduce who they are (without going into too much detail) and ask how they're doing.

Suggested format:
"Joining me today is [Candidate Name], [brief introduction]. Welcome [Candidate Name]! How are you doing today?"

Be natural and show your personality: {personality_desc}.
Keep it short (2-3 sentences maximum).

Return ONLY the welcome text."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.ai_provider.generate_completion(messages, model, max_tokens)
    
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
