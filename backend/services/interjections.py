import random
from typing import List


class InterjectionService:
    """Service for generating natural interjections and reactions in dialogues"""
    
    # Interjections pour le candidat (début de réponse)
    CANDIDATE_INTERJECTIONS_FR = [
        "Ok, ",
        "Eh bien, ",
        "Alors, ",
        "Oui, je suppose que vous voulez dire... Eh bien, ",
        "C'est une bonne question. ",
        "Hmm, laissez-moi réfléchir... ",
        "Absolument, ",
        "En fait, ",
        "D'accord, ",
        "Vous savez, ",
        "Effectivement, ",
        "Je dirais que ",
        "Pour être honnête, ",
        "Si je comprends bien votre question, ",
        "Intéressant comme question... ",
        "Bonne remarque. ",
        "Je pense que ",
        "À mon avis, ",
        "Clairement, ",
        "Sans aucun doute, "
    ]
    
    CANDIDATE_INTERJECTIONS_EN = [
        "Ok, ",
        "Well, ",
        "So, ",
        "Yes, I suppose you mean... Well, ",
        "That's a good question. ",
        "Hmm, let me think... ",
        "Absolutely, ",
        "Actually, ",
        "Alright, ",
        "You know, ",
        "Indeed, ",
        "I would say that ",
        "To be honest, ",
        "If I understand your question correctly, ",
        "Interesting question... ",
        "Good point. ",
        "I think that ",
        "In my opinion, ",
        "Clearly, ",
        "Without a doubt, "
    ]
    
    # Réactions de l'interviewer (fin de dialogue ou entre les questions)
    INTERVIEWER_REACTIONS_FR = [
        "Intéressant! ",
        "Merci pour cette réponse détaillée. ",
        "Ha ha, c'est vrai! ",
        "Excellente explication. ",
        "Je vois. ",
        "Très bien. ",
        "Parfait. ",
        "C'est un bon point. ",
        "D'accord, d'accord. ",
        "Fascinant! ",
        "Ça fait sens. ",
        "Exactement! ",
        "Ah oui, je comprends. ",
        "Super! ",
        "Belle réponse. ",
        "Intéressant comme approche. ",
        "Merci pour ces précisions. ",
        "Ha ha, bien dit! ",
        "C'est exactement ça. ",
        "Génial! "
    ]
    
    INTERVIEWER_REACTIONS_EN = [
        "Interesting! ",
        "Thanks for that detailed answer. ",
        "Ha ha, that's true! ",
        "Excellent explanation. ",
        "I see. ",
        "Very good. ",
        "Perfect. ",
        "That's a good point. ",
        "Alright, alright. ",
        "Fascinating! ",
        "That makes sense. ",
        "Exactly! ",
        "Ah yes, I understand. ",
        "Great! ",
        "Nice answer. ",
        "Interesting approach. ",
        "Thanks for clarifying. ",
        "Ha ha, well said! ",
        "That's exactly it. ",
        "Awesome! "
    ]
    
    @staticmethod
    def get_candidate_interjection(language: str = "en", probability: float = 0.7) -> str:
        """
        Get a random interjection for candidate's response
        
        Args:
            language: "en" or "fr"
            probability: Probability of adding an interjection (0.0 to 1.0)
        
        Returns:
            An interjection string or empty string
        """
        if random.random() > probability:
            return ""
        
        interjections = (
            InterjectionService.CANDIDATE_INTERJECTIONS_FR 
            if language == "fr" 
            else InterjectionService.CANDIDATE_INTERJECTIONS_EN
        )
        return random.choice(interjections)
    
    @staticmethod
    def get_interviewer_reaction(language: str = "en", probability: float = 0.4) -> str:
        """
        Get a random reaction for interviewer
        
        Args:
            language: "en" or "fr"
            probability: Probability of adding a reaction (0.0 to 1.0)
        
        Returns:
            A reaction string or empty string
        """
        if random.random() > probability:
            return ""
        
        reactions = (
            InterjectionService.INTERVIEWER_REACTIONS_FR 
            if language == "fr" 
            else InterjectionService.INTERVIEWER_REACTIONS_EN
        )
        return random.choice(reactions)
    
    @staticmethod
    def add_interjection_to_text(text: str, interjection: str) -> str:
        """
        Add an interjection to the beginning of a text
        
        Args:
            text: The original text
            interjection: The interjection to add
        
        Returns:
            Text with interjection prepended
        """
        if not interjection:
            return text
        return f"{interjection}{text}"
