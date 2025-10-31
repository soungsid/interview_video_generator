import logging
from typing import List, Optional

from clients.ai_client import AIClient
from entities.dialogue import Role

logger = logging.getLogger(__name__)


class ScriptGenerationService:
    """Service for generating interview video scripts with conversation memory"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    def generate_video_script(self, topic: str, num_questions: int, model: Optional[str] = None) -> dict:
        """
        Generate a complete video script with introduction, dialogues, and conclusion.
        Maintains conversation memory throughout the generation process.
        """
        logger.info(f"Starting video script generation for topic: {topic}, questions: {num_questions}")
        
        # Generate introduction
        introduction = self._generate_introduction(topic, model)
        logger.info("Introduction generated")
        
        # Generate dialogues with conversation memory
        dialogues = self._generate_dialogues(topic, num_questions, model)
        logger.info(f"Generated {len(dialogues)} dialogues")
        
        # Generate conclusion
        conclusion = self._generate_conclusion(topic, dialogues, model)
        logger.info("Conclusion generated")
        
        return {
            "introduction": introduction,
            "dialogues": dialogues,
            "conclusion": conclusion
        }
    
    def _generate_introduction(self, topic: str, model: Optional[str] = None) -> str:
        """Generate the introduction for the video"""
        messages = [
            {
                "role": "system",
                "content": "You are a professional YouTuber who creates engaging technical interview content. Your style is friendly, clear, and professional."
            },
            {
                "role": "user",
                "content": f"Create a brief, engaging introduction (2-3 sentences) for a YouTube video where you'll interview a candidate about {topic}. Welcome viewers and introduce the topic naturally."
            }
        ]
        
        return self.ai_client.generate_completion(messages, model)
    
    def _generate_dialogues(self, topic: str, num_questions: int, model: Optional[str] = None) -> List[dict]:
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
2. CANDIDATE: A knowledgeable professional answering the questions

Important rules:
- Maintain conversation memory: reference previous questions/answers when relevant
- Make questions progressively more difficult
- Keep responses clear and concise (2-4 sentences)
- Make it feel like a natural conversation, not isolated Q&A
- The candidate should acknowledge and build upon previous topics when appropriate
- The YouTuber may follow up based on previous answers"""
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
            
            question_text = self.ai_client.generate_completion(conversation_history, model)
            
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
                "content": f"As the CANDIDATE, answer the question. Reference previous discussion if relevant. Keep it concise but informative (2-4 sentences). Return ONLY the answer text, no labels or formatting."
            })
            
            answer_text = self.ai_client.generate_completion(conversation_history, model)
            
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
    
    def _generate_conclusion(self, topic: str, dialogues: List[dict], model: Optional[str] = None) -> str:
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
        
        return self.ai_client.generate_completion(messages, model)
