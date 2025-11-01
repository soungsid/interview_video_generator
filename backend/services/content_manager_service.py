import logging
import re
from typing import Dict, Optional, List
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests

from clients.ai_client import AIClient

logger = logging.getLogger(__name__)


class ContentManagerService:
    """Service for managing dynamic content for video generation"""
    
    def __init__(self, ai_provider_name: Optional[str] = None):
        """
        Initialize ContentManagerService with AI client
        
        Args:
            ai_provider_name: Name of AI provider (deepseek, openai, etc.)
        """
        self.ai_client = AIClient(ai_provider_name)
        self.content_cache_dir = Path("./video_content_cache")
        self.content_cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ContentManagerService initialized with provider: {self.ai_client.provider_name}")
    
    async def generate_content_for_dialogue(
        self, 
        dialogue_text: str, 
        audio_duration: float,
        context: str,
        dialogue_number: int
    ) -> Dict[str, any]:
        """
        Generate appropriate visual content for a dialogue segment.
        
        Uses LLM to decide the best content type and generates it.
        
        Args:
            dialogue_text: The dialogue text
            audio_duration: Duration of audio in seconds
            context: Overall context/topic of the video
            dialogue_number: Dialogue sequence number
            
        Returns:
            Dictionary with:
                - content_type: str (code, diagram, text, image, none)
                - content_path: Optional[Path] (path to generated content)
                - content_data: Optional[Dict] (additional content metadata)
        """
        logger.info(f"Generating content for dialogue {dialogue_number}")
        
        # Use LLM to decide what content to show
        decision = await self._decide_content_type(dialogue_text, context, audio_duration)
        
        content_type = decision.get("type", "text")
        
        # Generate content based on type
        if content_type == "code":
            return await self._generate_code_visual(dialogue_text, dialogue_number, decision)
        elif content_type == "diagram":
            return await self._generate_diagram(dialogue_text, dialogue_number, decision)
        elif content_type == "text":
            return await self._generate_text_overlay(dialogue_text, dialogue_number, decision)
        elif content_type == "image":
            return await self._generate_image_placeholder(dialogue_number, decision)
        else:
            return {
                "content_type": "none",
                "content_path": None,
                "content_data": {}
            }
    
    async def _decide_content_type(
        self, 
        dialogue_text: str, 
        context: str, 
        audio_duration: float
    ) -> Dict[str, any]:
        """
        Use LLM to decide what type of content to display.
        
        Args:
            dialogue_text: The dialogue text
            context: Overall video context
            audio_duration: Duration in seconds
            
        Returns:
            Dictionary with content decision
        """
        prompt = f"""You are an expert at creating engaging video content for technical interviews.

Context: {context}
Audio Duration: {audio_duration} seconds
Dialogue: {dialogue_text}

Analyze this dialogue and decide what visual content would be most engaging to display.

Options:
1. "code" - If dialogue discusses code implementation, show formatted code snippet
2. "diagram" - If dialogue explains concepts, architecture, or relationships
3. "text" - If dialogue has key points or definitions to highlight
4. "image" - If dialogue would benefit from a relevant image/illustration
5. "none" - If visual content would be distracting

Respond in JSON format:
{{
    "type": "code|diagram|text|image|none",
    "reason": "brief explanation",
    "content_suggestion": "what to show or highlight",
    "key_points": ["point1", "point2", ...]
}}"""

        messages = [
            {"role": "system", "content": "You are an expert at video content planning. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.ai_client.generate_completion(messages, max_tokens=500)
            
            # Try to parse JSON response
            import json
            # Extract JSON from response (in case LLM adds extra text)
            json_match = re.search(r'\{[\s\S]+\}', response)
            if json_match:
                decision = json.loads(json_match.group())
                logger.info(f"Content decision: {decision.get('type')} - {decision.get('reason')}")
                return decision
            else:
                logger.warning("Could not parse LLM response as JSON, defaulting to text")
                return {"type": "text", "reason": "default", "content_suggestion": dialogue_text[:100]}
                
        except Exception as e:
            logger.error(f"Error deciding content type: {str(e)}")
            return {"type": "text", "reason": "error fallback", "content_suggestion": dialogue_text[:100]}
    
    async def _generate_code_visual(
        self, 
        dialogue_text: str, 
        dialogue_number: int, 
        decision: Dict
    ) -> Dict[str, any]:
        """
        Generate a code visualization.
        
        Extracts code from dialogue and creates a visually appealing code image.
        """
        # Extract code blocks
        code_blocks = re.findall(r'```[\w]*\n([\s\S]+?)```', dialogue_text)
        
        if not code_blocks:
            # Try to find inline code or use suggestion
            code_text = decision.get("content_suggestion", "// Code example")
        else:
            code_text = code_blocks[0]
        
        # Create code image using PIL
        output_path = self.content_cache_dir / f"code_{dialogue_number}.png"
        
        try:
            # Create image with dark background (like VS Code)
            img_width = 1200
            img_height = 800
            img = Image.new('RGB', (img_width, img_height), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)
            
            # Try to use monospace font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
            except Exception:
                font = ImageFont.load_default()
            
            # Draw code text
            y_position = 50
            line_height = 35
            for line in code_text.split('\n')[:20]:  # Limit to 20 lines
                draw.text((50, y_position), line, fill=(220, 220, 220), font=font)
                y_position += line_height
            
            img.save(output_path)
            logger.info(f"Code visual generated: {output_path}")
            
            return {
                "content_type": "code",
                "content_path": output_path,
                "content_data": {"code": code_text}
            }
            
        except Exception as e:
            logger.error(f"Error generating code visual: {str(e)}")
            return {"content_type": "none", "content_path": None, "content_data": {}}
    
    async def _generate_diagram(
        self, 
        dialogue_text: str, 
        dialogue_number: int, 
        decision: Dict
    ) -> Dict[str, any]:
        """
        Generate a simple diagram visualization.
        
        Uses matplotlib to create simple diagrams based on content.
        """
        output_path = self.content_cache_dir / f"diagram_{dialogue_number}.png"
        
        try:
            key_points = decision.get("key_points", [])
            
            if len(key_points) == 0:
                # Create a simple concept box
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.text(0.5, 0.5, decision.get("content_suggestion", "Concept")[:50],
                       ha='center', va='center', fontsize=20, 
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
            else:
                # Create a flowchart-like diagram
                fig, ax = plt.subplots(figsize=(12, 8))
                
                num_points = min(len(key_points), 5)
                y_positions = [0.8 - i * 0.15 for i in range(num_points)]
                
                for i, (point, y_pos) in enumerate(zip(key_points[:num_points], y_positions)):
                    ax.text(0.5, y_pos, f"{i+1}. {point[:40]}",
                           ha='center', va='center', fontsize=14,
                           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
                    
                    # Draw arrow to next point
                    if i < num_points - 1:
                        ax.annotate('', xy=(0.5, y_positions[i+1] + 0.05), 
                                   xytext=(0.5, y_pos - 0.05),
                                   arrowprops=dict(arrowstyle='->', lw=2))
                
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Diagram generated: {output_path}")
            
            return {
                "content_type": "diagram",
                "content_path": output_path,
                "content_data": {"key_points": key_points}
            }
            
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            return {"content_type": "none", "content_path": None, "content_data": {}}
    
    async def _generate_text_overlay(
        self, 
        dialogue_text: str, 
        dialogue_number: int, 
        decision: Dict
    ) -> Dict[str, any]:
        """
        Generate a text overlay image with key points.
        """
        output_path = self.content_cache_dir / f"text_{dialogue_number}.png"
        
        try:
            # Extract key text to display
            key_text = decision.get("content_suggestion", dialogue_text[:150])
            key_points = decision.get("key_points", [])
            
            # Create image
            img_width = 1200
            img_height = 800
            img = Image.new('RGB', (img_width, img_height), color=(245, 245, 245))
            draw = ImageDraw.Draw(img)
            
            # Try to load font
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Draw title box
            draw.rectangle([(50, 50), (img_width - 50, 150)], fill=(70, 130, 180), outline=(50, 100, 150), width=3)
            draw.text((img_width // 2, 100), "Key Points", fill=(255, 255, 255), 
                     font=title_font, anchor="mm")
            
            # Draw key points
            y_position = 200
            for i, point in enumerate(key_points[:4], 1):  # Max 4 points
                bullet_text = f"• {point[:60]}"
                draw.text((100, y_position), bullet_text, fill=(50, 50, 50), font=text_font)
                y_position += 120
            
            img.save(output_path)
            logger.info(f"Text overlay generated: {output_path}")
            
            return {
                "content_type": "text",
                "content_path": output_path,
                "content_data": {"text": key_text, "points": key_points}
            }
            
        except Exception as e:
            logger.error(f"Error generating text overlay: {str(e)}")
            return {"content_type": "none", "content_path": None, "content_data": {}}
    
    async def _generate_image_placeholder(
        self, 
        dialogue_number: int, 
        decision: Dict
    ) -> Dict[str, any]:
        """
        Generate a placeholder for images.
        
        In future versions, this could integrate with image APIs (Unsplash, etc.)
        """
        output_path = self.content_cache_dir / f"image_{dialogue_number}.png"
        
        try:
            # Create a simple placeholder image
            img_width = 1200
            img_height = 800
            img = Image.new('RGB', (img_width, img_height), color=(200, 220, 240))
            draw = ImageDraw.Draw(img)
            
            # Draw placeholder text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            suggestion = decision.get("content_suggestion", "Visual Content")
            draw.text((img_width // 2, img_height // 2), suggestion[:50], 
                     fill=(100, 100, 100), font=font, anchor="mm")
            
            img.save(output_path)
            logger.info(f"Image placeholder generated: {output_path}")
            
            return {
                "content_type": "image",
                "content_path": output_path,
                "content_data": {"suggestion": suggestion}
            }
            
        except Exception as e:
            logger.error(f"Error generating image placeholder: {str(e)}")
            return {"content_type": "none", "content_path": None, "content_data": {}}
