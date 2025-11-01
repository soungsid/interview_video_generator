import logging
from typing import List, Optional
from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class MockProvider(BaseAIProvider):
    """Mock AI provider for testing purposes"""
    
    def __init__(self):
        self.default_model = "mock-model"
        logger.info("MockProvider initialized for testing")
    
    def generate_completion(self, messages: List[dict], model: Optional[str] = None, max_tokens: int = 4000) -> str:
        """Generate a mock completion for testing"""
        try:
            # Extract the user prompt to generate contextual responses
            user_message = ""
            for msg in messages:
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # Generate contextual mock responses based on the prompt
            if "engaging introduction" in user_message.lower() or "captivating introduction" in user_message.lower():
                if "spring boot aop" in user_message.lower():
                    return "Have you ever wondered how Spring Boot magically intercepts your method calls without you even noticing? That's the power of Aspect-Oriented Programming in action. Today, we'll uncover the secrets behind this elegant framework feature."
                elif "python fastapi" in user_message.lower():
                    return "Vous êtes-vous déjà demandé comment Python FastAPI peut être si rapide tout en restant si simple à utiliser? Ce n'est pas de la magie — c'est de l'ingénierie brillante. Aujourd'hui, nous allons découvrir ce qui se cache derrière cette performance exceptionnelle."
                else:
                    return "Have you ever wondered what makes modern software development so powerful? Today we're diving deep into the fascinating world of cutting-edge technology."
            
            elif "welcome" in user_message.lower() and "guest" in user_message.lower():
                if "alex" in user_message.lower():
                    return "Joining me today is Alex, a seasoned software engineer with expertise in enterprise applications. Welcome Alex! How are you doing today?"
                elif "marie" in user_message.lower():
                    return "Avec moi aujourd'hui, Marie, une développeuse experte en Python et architectures modernes. Bienvenue Marie! Comment allez-vous?"
                else:
                    return "Joining me today is our expert guest. Welcome! How are you doing today?"
            
            elif "candidate" in user_message.lower() and ("thank" in user_message.lower() or "merci" in user_message.lower()):
                if "sarah" in user_message.lower():
                    return "Thank you Sarah! I'm doing great, thanks. Really excited to be here and share some insights about this fascinating topic."
                elif "jean" in user_message.lower():
                    return "Merci Jean! Je vais très bien, merci. Je suis ravi d'être ici avec vous pour discuter de ce sujet passionnant."
                else:
                    return "Thank you! I'm doing excellent, thanks. Happy to be here with you today."
            
            elif "question" in user_message.lower() and "#1" in user_message:
                if "spring boot aop" in user_message.lower():
                    return "Let's start with the fundamentals. Can you explain what Aspect-Oriented Programming is and how it fits into the Spring Boot ecosystem?"
                elif "python fastapi" in user_message.lower():
                    return "Commençons par les bases. Pouvez-vous nous expliquer ce qui rend FastAPI si performant comparé aux autres frameworks Python?"
                else:
                    return "Let's start with the basics. Can you give us an overview of this technology and its main benefits?"
            
            elif "question" in user_message.lower() and "#2" in user_message:
                return "That's really interesting! Can you walk us through a practical example of how this would work in a real-world application?"
            
            elif "question" in user_message.lower() and "#3" in user_message:
                return "Excellent explanation! What are some common pitfalls developers should avoid when implementing this approach?"
            
            elif "answer" in user_message.lower() or "comprehensive answer" in user_message.lower():
                if "interjection" in user_message.lower():
                    interjection = ""
                    if "Ok," in user_message:
                        interjection = "Ok, "
                    elif "Well," in user_message:
                        interjection = "Well, "
                    elif "Eh bien," in user_message:
                        interjection = "Eh bien, "
                    
                    if "spring boot aop" in user_message.lower():
                        return f"{interjection}Aspect-Oriented Programming in Spring Boot is essentially a programming paradigm that allows you to separate cross-cutting concerns from your business logic. Think of it as a way to add functionality to your methods without modifying the actual method code. For example, you can add logging, security checks, or transaction management through aspects. The beauty of Spring AOP is that it uses proxy-based mechanisms to intercept method calls at runtime, making it completely transparent to your application code."
                    elif "python fastapi" in user_message.lower():
                        return f"{interjection}FastAPI doit sa performance exceptionnelle à plusieurs facteurs clés. Premièrement, il est construit sur Starlette pour les parties web et Pydantic pour la validation des données, deux bibliothèques extrêmement optimisées. Deuxièmement, il utilise les annotations de type Python pour générer automatiquement la documentation et la validation, ce qui élimine beaucoup de code boilerplate. Enfin, son support natif de l'asynchrone permet de gérer des milliers de requêtes concurrentes avec une empreinte mémoire minimale."
                    else:
                        return f"{interjection}This is a really comprehensive topic that involves multiple layers of complexity. The key thing to understand is that modern frameworks are designed with performance and developer experience in mind. They leverage advanced patterns like dependency injection, asynchronous processing, and compile-time optimizations to deliver both speed and maintainability. The result is code that's not only fast but also easy to read and maintain."
                else:
                    return "This is a comprehensive answer that covers the key aspects of the topic with detailed explanations and practical examples."
            
            elif "reaction" in user_message.lower():
                reactions = [
                    "Interesting! That's a great point.",
                    "Perfect! I love that explanation.",
                    "Excellent! That's exactly right.",
                    "Intéressant! C'est un excellent point.",
                    "Parfait! J'adore cette explication."
                ]
                return reactions[len(user_message) % len(reactions)]
            
            elif "conclusion" in user_message.lower():
                return "Thanks for watching today's deep dive! If you found this helpful, don't forget to like and subscribe for more technical content. Next week, we'll be exploring advanced patterns in microservices architecture. See you then!"
            
            else:
                # Default response for any other prompt
                return "This is a mock response generated for testing purposes. The actual AI provider would generate contextual content based on the prompt."
        
        except Exception as e:
            logger.error(f"Mock provider error: {str(e)}")
            return "Mock response: Error generating content"
    
    def get_default_model(self) -> str:
        return self.default_model