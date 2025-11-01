import logging
from typing import Optional

from clients.ai_providers.base_provider import BaseAIProvider
from entities.persona import Language

logger = logging.getLogger(__name__)


class SEOService:
    """Service for generating SEO-friendly video titles"""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
    
    def generate_seo_title(
        self,
        topic: str,
        language: Language,
        num_questions: int = None,
        model: Optional[str] = None,
        max_tokens: int = 200
    ) -> str:
        """Generate an SEO-friendly title with relevant keywords
        
        Args:
            topic: The interview topic
            language: Language for the title
            num_questions: Optional number of questions in the interview
            model: AI model to use
            max_tokens: Maximum tokens for generation
        
        Returns:
            SEO-optimized title
        """
        lang_code = language.value
        
        system_prompt = f"""You are an expert in YouTube SEO and content optimization.
Your task is to create compelling, SEO-friendly video titles.
Speak in {lang_code} language."""
        
        context = f" with {num_questions} questions" if num_questions else ""
        
        if lang_code == 'fr':
            user_prompt = f"""Créez un titre YouTube optimisé pour le SEO pour une vidéo d'interview technique sur: {topic}{context}

Règles importantes:
1. Inclure les mots-clés principaux liés à {topic}
2. Le titre doit être engageant et inciter au clic
3. Longueur optimale: 50-70 caractères
4. Utiliser des nombres si pertinent (ex: "Top 10", "5 Conseils", etc.)
5. Inclure des mots d'action ou des promesses de valeur
6. Format professionnel pour interview technique

Exemples de bons titres:
- "{topic}: Guide Complet pour Développeurs en 2025"
- "Maîtriser {topic} - Interview Expert avec Cas Pratiques"
- "{topic} Expliqué: {num_questions or 10} Questions Essentielles"

Retournez UNIQUEMENT le titre, sans guillemets ni explications."""
        else:
            user_prompt = f"""Create an SEO-optimized YouTube title for a technical interview video about: {topic}{context}

Important rules:
1. Include main keywords related to {topic}
2. Title should be engaging and click-worthy
3. Optimal length: 50-70 characters
4. Use numbers if relevant (e.g., "Top 10", "5 Tips", etc.)
5. Include action words or value promises
6. Professional format for technical interview

Examples of good titles:
- "{topic}: Complete Guide for Developers in 2025"
- "Master {topic} - Expert Interview with Real Examples"
- "{topic} Explained: {num_questions or 10} Essential Questions"

Return ONLY the title, without quotes or explanations."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        title = self.ai_provider.generate_completion(messages, model, max_tokens)
        
        # Clean up the title (remove quotes if present)
        title = title.strip().strip('"').strip("'")
        
        logger.info(f"Generated SEO title: {title}")
        return title
