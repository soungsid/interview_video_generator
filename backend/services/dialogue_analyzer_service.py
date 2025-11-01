import logging
import re
from typing import Dict, Optional
from clients.ai_client import AIClient

logger = logging.getLogger(__name__)


class DialogueAnalyzerService:
    """Service for analyzing dialogue content, especially code snippets"""
    
    def __init__(self, ai_provider_name: Optional[str] = None):
        """
        Initialize DialogueAnalyzerService with AI client
        
        Args:
            ai_provider_name: Name of AI provider (deepseek, openai, etc.)
        """
        self.ai_client = AIClient(ai_provider_name)
        logger.info(f"DialogueAnalyzerService initialized with provider: {self.ai_client.provider_name}")
    
    def contains_code(self, text: str) -> bool:
        """
        Check if text contains code snippets using pattern matching.
        
        Simple readable annotations like @SpringBootApplication are considered readable
        and don't trigger this detection. Multi-line code blocks do.
        
        Args:
            text: The text to analyze
            
        Returns:
            True if text contains significant code blocks, False otherwise
        """
        # Patterns that indicate code
        code_patterns = [
            r'```[\s\S]+?```',  # Code blocks with triple backticks
            r'public\s+(class|interface|void|static)',  # Java keywords
            r'private\s+(class|interface|void|static)',  # Java keywords
            r'def\s+\w+\s*\(',  # Python function definitions
            r'function\s+\w+\s*\(',  # JavaScript functions
            r'const\s+\w+\s*=\s*\(',  # Arrow functions
            r'\{[\s\S]{30,}\}',  # Multi-line code blocks (30+ chars between braces)
            r'if\s*\([^)]+\)\s*\{',  # If statements with braces
            r'for\s*\([^)]+\)\s*\{',  # For loops with braces
            r'while\s*\([^)]+\)\s*\{',  # While loops with braces
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                logger.info(f"Code pattern detected: {pattern[:30]}...")
                return True
        
        return False
    
    def is_readable_annotation(self, text: str) -> bool:
        """
        Check if text only contains readable annotations/decorators
        like @SpringBootApplication, @Override, etc.
        
        Args:
            text: The text to check
            
        Returns:
            True if text only contains simple readable annotations
        """
        # Simple annotation pattern: @Word or @Word(simple parameters)
        simple_annotation_pattern = r'^[^@]*@\w+(\([^{}\[\]]*\))?[^@{}[\]]*$'
        
        if re.match(simple_annotation_pattern, text, re.DOTALL):
            return True
        
        return False
    
    async def analyze_and_enrich_dialogue(self, dialogue_text: str) -> Dict[str, any]:
        """
        Analyze dialogue text and enrich it with information about code handling.
        
        If the text contains code snippets:
        1. Use LLM to analyze the dialogue
        2. LLM decides how to handle the code (describe it, skip it, etc.)
        3. Return enriched dialogue suitable for audio generation
        
        Args:
            dialogue_text: The original dialogue text
            
        Returns:
            Dictionary with:
                - contains_code: bool
                - processed_text: str (text suitable for audio)
                - original_text: str
                - analysis: Optional[str] (LLM's analysis if code was found)
        """
        # Check if text contains code
        has_code = self.contains_code(dialogue_text)
        
        # If only readable annotations, no processing needed
        if has_code and self.is_readable_annotation(dialogue_text):
            logger.info("Only readable annotations detected, no processing needed")
            return {
                "contains_code": False,
                "processed_text": dialogue_text,
                "original_text": dialogue_text,
                "analysis": "Only readable annotations - no processing needed"
            }
        
        # If no code, return as is
        if not has_code:
            return {
                "contains_code": False,
                "processed_text": dialogue_text,
                "original_text": dialogue_text,
                "analysis": None
            }
        
        # If code detected, use LLM to process it
        logger.info("Code detected in dialogue, using LLM to process...")
        
        try:
            # Ask LLM to process the dialogue
            prompt = f"""You are an expert at processing interview dialogue for audio generation.

The following dialogue contains code snippets that cannot be read naturally in audio.
Your task is to transform this dialogue into a version suitable for audio while preserving the meaning.

Guidelines:
1. Replace code blocks with natural descriptions (e.g., "In this code example..." or "The implementation shows...")
2. Keep technical terms and readable annotations like @SpringBootApplication
3. Maintain the conversational tone
4. Be concise but clear
5. If the code is the main point, describe what it does instead of reading it

Original dialogue:
{dialogue_text}

Return ONLY the processed dialogue text suitable for audio generation, without any explanations or metadata."""

            messages = [
                {"role": "system", "content": "You are an expert at adapting technical content for audio presentation."},
                {"role": "user", "content": prompt}
            ]
            
            processed_text = self.ai_client.generate_completion(messages, max_tokens=1000)
            
            logger.info("Dialogue successfully processed by LLM")
            
            return {
                "contains_code": True,
                "processed_text": processed_text.strip(),
                "original_text": dialogue_text,
                "analysis": "LLM processed code-heavy dialogue for audio"
            }
            
        except Exception as e:
            logger.error(f"Error processing dialogue with LLM: {str(e)}")
            # Fallback: return original text with warning
            return {
                "contains_code": True,
                "processed_text": dialogue_text,
                "original_text": dialogue_text,
                "analysis": f"Error processing with LLM: {str(e)}"
            }
    
    def extract_code_blocks(self, text: str) -> list:
        """
        Extract all code blocks from text.
        
        Args:
            text: Text to extract code from
            
        Returns:
            List of code block strings
        """
        # Extract code blocks with triple backticks
        code_blocks = re.findall(r'```[\s\S]+?```', text)
        
        return code_blocks
