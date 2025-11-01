import logging
from typing import List, Optional, Tuple

from clients.ai_providers.base_provider import BaseAIProvider
from entities.dialogue import Role
from entities.persona import Persona, Language
from services.interjections import InterjectionService
from services.introduction_service import IntroductionService

logger = logging.getLogger(__name__)


class ScriptGenerationService:
    """Service for generating interview video scripts with conversation memory"""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
        self.interjection_service = InterjectionService()
        self.introduction_service = IntroductionService(ai_provider)
    
    def generate_video_script(
        self, 
        topic: str, 
        num_questions: int, 
        interviewer_persona: Persona,
        candidate_persona: Persona,
        language: Language = Language.ENGLISH,
        model: Optional[str] = None, 
        max_tokens: int = 4000
    ) -> dict:
        """
        Generate a complete video script with introduction, dialogues, and conclusion.
        Maintains conversation memory throughout the generation process.
        
        Args:
            topic: The interview topic
            num_questions: Number of questions to generate
            interviewer_persona: The interviewer persona
            candidate_persona: The candidate persona
            language: Language for the interview
            model: AI model to use (optional)
            max_tokens: Maximum tokens per response (default: 4000)
        
        Returns:
            Dictionary with introduction, dialogues, conclusion, and personas
        """
        logger.info(f"Starting video script generation for topic: {topic}, questions: {num_questions}")
        logger.info(f"Interviewer: {interviewer_persona.name} ({interviewer_persona.specialty})")
        logger.info(f"Candidate: {candidate_persona.name}")
        logger.info(f"Language: {language}, max_tokens: {max_tokens}")
        
        lang_code = language.value
        
        # Generate engaging introduction with greeting exchange
        intro, welcome, candidate_response, transition = self.introduction_service.generate_engaging_introduction(
            topic, interviewer_persona, candidate_persona, language, model, max_tokens
        )
        logger.info("Engaging introduction generated")
        
        # Combine introduction parts
        introduction = f"{intro}\n\n{welcome}\n\n{candidate_response}\n\n{transition}"
        
        # Generate dialogues with conversation memory
        dialogues = self._generate_dialogues(
            topic, num_questions, interviewer_persona, candidate_persona, 
            lang_code, model, max_tokens
        )
        logger.info(f"Generated {len(dialogues)} dialogues")
        
        # Generate conclusion
        conclusion = self._generate_conclusion(
            topic, dialogues, interviewer_persona, lang_code, model, max_tokens
        )
        logger.info("Conclusion generated")
        
        return {
            "introduction": introduction,
            "dialogues": dialogues,
            "conclusion": conclusion,
            "interviewer_persona": interviewer_persona,
            "candidate_persona": candidate_persona
        }
    
    def _generate_dialogues(
        self, 
        topic: str, 
        num_questions: int, 
        interviewer_persona: Persona,
        candidate_persona: Persona,
        language: str,
        model: Optional[str] = None, 
        max_tokens: int = 4000
    ) -> List[dict]:
        """
        Generate interview dialogues with conversation memory and natural interjections.
        Both agents remember the entire conversation.
        """
        dialogues = []
        
        interviewer_personality = ", ".join(interviewer_persona.personality_traits)
        candidate_personality = ", ".join(candidate_persona.personality_traits)
        
        # Initialize conversation memory for both agents
        conversation_history = [
            {
                "role": "system",
                "content": f"""You are simulating a YouTube interview about {topic} in {language} language.

You will alternate between two personas:

1. INTERVIEWER ({interviewer_persona.name}):
   - Specialty: {interviewer_persona.specialty or 'General'}
   - Personality: {interviewer_personality}
   - Role: Asks progressively challenging questions
   - Occasionally reacts to answers with brief comments (praise, humor, acknowledgment)
   - Makes the conversation feel natural and human-like

2. CANDIDATE ({candidate_persona.name}):
   - Personality: {candidate_personality}
   - Role: Provides detailed, comprehensive answers
   - Often starts responses with natural interjections like "Ok," "Well," "That's a good question," etc.
   - References previous discussion when relevant

Important rules for realistic dialogue:
- Maintain conversation memory: reference previous questions/answers when relevant
- Make questions progressively more difficult
- CANDIDATE should provide detailed explanations (4-6 sentences minimum)
- INTERVIEWER may add brief reactions between questions (not always, about 40% of the time)
- CANDIDATE often uses conversational starters (about 70% of the time)
- Make it feel like a natural conversation between two humans, not a mechanical Q&A
- Include practical examples and code snippets when relevant
- Show personality in the dialogue"""
            }
        ]
        
        logger.info("="*80)
        logger.info(f"CONVERSATION START: {topic}")
        logger.info(f"Interviewer: {interviewer_persona.name}, Candidate: {candidate_persona.name}")
        logger.info("="*80)
        
        for i in range(1, num_questions + 1):
            # Add interviewer reaction to previous answer (sometimes)
            if i > 1:
                reaction = self.interjection_service.get_interviewer_reaction(language)
                if reaction:
                    # Add reaction to the last dialogue (which was candidate's answer)
                    if dialogues and dialogues[-1]["role"] == Role.CANDIDATE:
                        conversation_history.append({
                            "role": "user",
                            "content": f"As {interviewer_persona.name} (the INTERVIEWER), react briefly to the candidate's answer. Use this reaction: '{reaction}' and optionally add a short comment. Return ONLY the reaction text (keep it very short, 1-2 sentences max)."
                        })
                        
                        reaction_text = self.ai_client.generate_completion(conversation_history, model, max_tokens)
                        
                        logger.info(f"[Reaction] {interviewer_persona.name}: {reaction_text}")
                        
                        # Add reaction to dialogues as a separate turn
                        dialogues.append({
                            "role": Role.YOUTUBER,
                            "text": reaction_text,
                            "question_number": i - 1  # Associate with previous question
                        })
                        
                        conversation_history.append({
                            "role": "assistant",
                            "content": reaction_text
                        })
            
            # Generate interviewer's question
            conversation_history.append({
                "role": "user",
                "content": f"""As {interviewer_persona.name} (the INTERVIEWER), ask question #{i} about {topic}.
{'This is the first question - start the interview naturally.' if i == 1 else 'Build on the previous conversation and ask a follow-up or related question.'}
Show your personality: {interviewer_personality}.
Return ONLY the question text, no labels or formatting."""
            })
            
            question_text = self.ai_client.generate_completion(conversation_history, model, max_tokens)
            
            # Log the question
            logger.info(f"\n[Question {i}] {interviewer_persona.name}: {question_text}")
            
            # Add question to dialogues
            dialogues.append({
                "role": Role.YOUTUBER,
                "text": question_text,
                "question_number": i
            })
            
            # Add the question to conversation memory
            conversation_history.append({
                "role": "assistant",
                "content": question_text
            })
            
            # Generate candidate's answer with interjection
            interjection = self.interjection_service.get_candidate_interjection(language)
            
            conversation_history.append({
                "role": "user",
                "content": f"""As {candidate_persona.name} (the CANDIDATE), provide a detailed, comprehensive answer to the question.
{'Start with this natural interjection: "' + interjection + '" ' if interjection else ''}
Reference previous discussion if relevant.
Give a thorough explanation with practical examples (4-6 sentences minimum).
Show your personality: {candidate_personality}.
Return ONLY the answer text, no labels or formatting."""
            })
            
            answer_text = self.ai_client.generate_completion(conversation_history, model, max_tokens)
            
            # Make sure interjection is included
            if interjection and not any(answer_text.startswith(inter.strip()) for inter in [interjection] + 
                                       InterjectionService.CANDIDATE_INTERJECTIONS_EN + 
                                       InterjectionService.CANDIDATE_INTERJECTIONS_FR):
                answer_text = self.interjection_service.add_interjection_to_text(answer_text, interjection)
            
            # Log the answer
            logger.info(f"[Answer {i}] {candidate_persona.name}: {answer_text}")
            
            # Add answer to dialogues
            dialogues.append({
                "role": Role.CANDIDATE,
                "text": answer_text,
                "question_number": i
            })
            
            # Add the answer to conversation memory
            conversation_history.append({
                "role": "assistant",
                "content": answer_text
            })
        
        logger.info("="*80)
        logger.info("CONVERSATION END")
        logger.info("="*80)
        
        return dialogues
    
    def _generate_conclusion(
        self, 
        topic: str, 
        dialogues: List[dict], 
        interviewer_persona: Persona,
        language: str,
        model: Optional[str] = None, 
        max_tokens: int = 4000
    ) -> str:
        """Generate a conclusion that references the interview"""
        personality_desc = ", ".join(interviewer_persona.personality_traits)
        
        system_prompt = f"""You are {interviewer_persona.name}, concluding your YouTube interview video.
Your personality is: {personality_desc}.
Speak in {language} language."""
        
        user_prompt = f"""Create a brief, engaging conclusion (2-3 sentences) for your YouTube video about {topic}.
Thank viewers, encourage engagement (likes, subscribes), and tease future content.
Show your personality: {personality_desc}.
Keep it friendly and natural.
Return ONLY the conclusion text."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.ai_client.generate_completion(messages, model, max_tokens)
