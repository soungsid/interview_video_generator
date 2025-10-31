import logging
from typing import List, Optional, Tuple

from clients.ai_client import AIClient
from entities.dialogue import Role
from entities.persona import Persona, Language
from services.interjections import InterjectionService

logger = logging.getLogger(__name__)


class ScriptGenerationService:
    """Service for generating interview video scripts with conversation memory"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.interjection_service = InterjectionService()
    
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
        
        # Generate introduction
        introduction = self._generate_introduction(
            topic, interviewer_persona, lang_code, model, max_tokens
        )
        logger.info("Introduction generated")
        
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
    
    def _generate_introduction(
        self, 
        topic: str, 
        interviewer_persona: Persona, 
        language: str,
        model: Optional[str] = None, 
        max_tokens: int = 4000
    ) -> str:
        """Generate the introduction for the video"""
        personality_desc = ", ".join(interviewer_persona.personality_traits)
        
        system_prompt = f"""You are {interviewer_persona.name}, a professional YouTuber who creates engaging interview content.
Your specialty is {interviewer_persona.specialty or 'general topics'}.
Your personality is: {personality_desc}.
Speak in {language} language."""
        
        user_prompt = f"""Create a brief, engaging introduction (2-3 sentences) for a YouTube video where you'll interview a candidate about {topic}.
Welcome viewers and introduce the topic naturally.
Show your personality: {personality_desc}.
Return ONLY the introduction text."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.ai_client.generate_completion(messages, model, max_tokens)
    
    def _generate_dialogues(self, topic: str, num_questions: int, model: Optional[str] = None, max_tokens: int = 4000) -> List[dict]:
        """
        Generate interview dialogues with conversation memory.
        Both agents remember the entire conversation.
        """
        dialogues = []
        
        # Initialize conversation memory for both agents
        conversation_history = [
            {
                "role": "system",
                "content": f"""You are simulating a YouTube technical interview about {topic}.

You will alternate between two personas:
1. YOUTUBER: A friendly interviewer who asks progressively challenging questions
2. CANDIDATE: A knowledgeable professional answering the questions with detailed, comprehensive explanations

Important rules:
- Maintain conversation memory: reference previous questions/answers when relevant
- Make questions progressively more difficult
- CANDIDATE should provide detailed, thorough explanations (4-6 sentences minimum)
- Make it feel like a natural conversation, not isolated Q&A
- The candidate should acknowledge and build upon previous topics when appropriate
- The YouTuber may follow up based on previous answers
- Include practical examples and code snippets when relevant"""
            }
        ]
        
        logger.info("="*80)
        logger.info(f"CONVERSATION START: {topic}")
        logger.info("="*80)
        
        for i in range(1, num_questions + 1):
            # Generate YouTuber's question
            conversation_history.append({
                "role": "user",
                "content": f"As the YOUTUBER, ask question #{i} about {topic}. {'This is the first question.' if i == 1 else 'Build on the previous conversation.'} Return ONLY the question text, no labels or formatting."
            })
            
            question_text = self.ai_client.generate_completion(conversation_history, model, max_tokens)
            
            # Log the question
            logger.info(f"\n[Question {i}] YOUTUBER: {question_text}")
            
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
            
            # Generate Candidate's answer
            conversation_history.append({
                "role": "user",
                "content": f"As the CANDIDATE, provide a detailed, comprehensive answer to the question. Reference previous discussion if relevant. Give a thorough explanation with practical examples (4-6 sentences minimum). Return ONLY the answer text, no labels or formatting."
            })
            
            answer_text = self.ai_client.generate_completion(conversation_history, model, max_tokens)
            
            # Log the answer
            logger.info(f"[Answer {i}] CANDIDATE: {answer_text}")
            
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
    
    def _generate_conclusion(self, topic: str, dialogues: List[dict], model: Optional[str] = None, max_tokens: int = 4000) -> str:
        """Generate a conclusion that references the interview"""
        messages = [
            {
                "role": "system",
                "content": "You are a professional YouTuber concluding a technical interview video."
            },
            {
                "role": "user",
                "content": f"Create a brief, engaging conclusion (2-3 sentences) for a YouTube video about {topic}. Thank viewers, encourage engagement (likes, subscribes), and tease future content. Keep it friendly and professional."
            }
        ]
        
        return self.ai_client.generate_completion(messages, model, max_tokens)
