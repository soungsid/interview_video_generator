#!/usr/bin/env python3
"""
Backend Test Suite for Persona-based Interview Generation System
Tests the new persona system with natural interjections and multilingual support.
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

# Backend URL from supervisor configuration
BASE_URL = "https://smooth-intro-api.preview.emergentagent.com/api"

class PersonaInterviewTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_api_health(self) -> bool:
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"API version: {data.get('version', 'unknown')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_database_health(self) -> bool:
        """Test database connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/health/database")
            if response.status_code == 200:
                self.log_test("Database Health Check", True, "MongoDB connection successful")
                return True
            else:
                self.log_test("Database Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_initialize_personas(self) -> bool:
        """Test persona initialization"""
        try:
            response = self.session.post(f"{self.base_url}/personas/initialize-defaults")
            if response.status_code == 200:
                personas = response.json()
                self.log_test("Initialize Default Personas", True, f"Created/Found {len(personas)} personas")
                return True
            else:
                self.log_test("Initialize Default Personas", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Initialize Default Personas", False, f"Error: {str(e)}")
            return False
    
    def test_get_all_personas(self) -> Dict[str, Any]:
        """Test GET /api/personas - List all personas"""
        try:
            response = self.session.get(f"{self.base_url}/personas")
            if response.status_code == 200:
                personas = response.json()
                if len(personas) >= 10:
                    self.log_test("GET All Personas", True, f"Found {len(personas)} personas")
                    return {"success": True, "personas": personas}
                else:
                    self.log_test("GET All Personas", False, f"Expected at least 10 personas, got {len(personas)}")
                    return {"success": False, "personas": personas}
            else:
                self.log_test("GET All Personas", False, f"Status: {response.status_code}")
                return {"success": False, "personas": []}
        except Exception as e:
            self.log_test("GET All Personas", False, f"Error: {str(e)}")
            return {"success": False, "personas": []}
    
    def test_get_personas_by_type(self) -> bool:
        """Test GET /api/personas/type/{INTERVIEWER|CANDIDATE}"""
        success = True
        
        # Test INTERVIEWER type
        try:
            response = self.session.get(f"{self.base_url}/personas/type/INTERVIEWER")
            if response.status_code == 200:
                interviewers = response.json()
                expected_specialties = ["Python", "Java Spring Boot", "JavaScript React", "DevOps", "Finance", "Marketing", "Droit"]
                found_specialties = [p.get("specialty") for p in interviewers if p.get("specialty")]
                
                if len(interviewers) >= 7:
                    self.log_test("GET Interviewers", True, f"Found {len(interviewers)} interviewers with specialties: {found_specialties}")
                else:
                    self.log_test("GET Interviewers", False, f"Expected at least 7 interviewers, got {len(interviewers)}")
                    success = False
            else:
                self.log_test("GET Interviewers", False, f"Status: {response.status_code}")
                success = False
        except Exception as e:
            self.log_test("GET Interviewers", False, f"Error: {str(e)}")
            success = False
        
        # Test CANDIDATE type
        try:
            response = self.session.get(f"{self.base_url}/personas/type/CANDIDATE")
            if response.status_code == 200:
                candidates = response.json()
                if len(candidates) >= 3:
                    self.log_test("GET Candidates", True, f"Found {len(candidates)} candidates")
                else:
                    self.log_test("GET Candidates", False, f"Expected at least 3 candidates, got {len(candidates)}")
                    success = False
            else:
                self.log_test("GET Candidates", False, f"Status: {response.status_code}")
                success = False
        except Exception as e:
            self.log_test("GET Candidates", False, f"Error: {str(e)}")
            success = False
        
        return success
    
    def test_persona_data_quality(self, personas: List[Dict]) -> bool:
        """Test that personas have correct data structure and content"""
        success = True
        
        required_fields = ["id", "name", "type", "voice_id", "language", "personality_traits", "is_active"]
        
        for persona in personas:
            # Check required fields
            missing_fields = [field for field in required_fields if field not in persona]
            if missing_fields:
                self.log_test("Persona Data Quality", False, f"Persona {persona.get('name', 'unknown')} missing fields: {missing_fields}")
                success = False
                continue
            
            # Check voice_id is not empty
            if not persona.get("voice_id"):
                self.log_test("Persona Data Quality", False, f"Persona {persona['name']} has empty voice_id")
                success = False
            
            # Check personality traits
            if not persona.get("personality_traits") or len(persona["personality_traits"]) == 0:
                self.log_test("Persona Data Quality", False, f"Persona {persona['name']} has no personality traits")
                success = False
        
        if success:
            self.log_test("Persona Data Quality", True, f"All {len(personas)} personas have valid data structure")
        
        return success
    
    def test_interview_generation_python(self) -> Dict[str, Any]:
        """Test interview generation for Python topic (should select Sarah)"""
        try:
            payload = {
                "topic": "Python FastAPI development and best practices",
                "num_questions": 3,
                "language": "en"
            }
            
            print(f"Generating interview for Python topic...")
            response = self.session.post(f"{self.base_url}/videos/generate", json=payload)
            
            if response.status_code == 200:
                video_data = response.json()
                
                # Check basic structure
                required_fields = ["id", "topic", "introduction", "dialogues", "conclusion"]
                missing_fields = [field for field in required_fields if field not in video_data]
                
                if missing_fields:
                    self.log_test("Python Interview Generation", False, f"Missing fields: {missing_fields}")
                    return {"success": False, "video": None}
                
                # Check dialogues count (should be 6: 3 questions + 3 answers)
                dialogues = video_data.get("dialogues", [])
                if len(dialogues) < 6:
                    self.log_test("Python Interview Generation", False, f"Expected at least 6 dialogues, got {len(dialogues)}")
                    return {"success": False, "video": video_data}
                
                self.log_test("Python Interview Generation", True, f"Generated video with {len(dialogues)} dialogues")
                return {"success": True, "video": video_data}
            
            else:
                self.log_test("Python Interview Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "video": None}
                
        except Exception as e:
            self.log_test("Python Interview Generation", False, f"Error: {str(e)}")
            return {"success": False, "video": None}
    
    def test_interview_generation_java(self) -> Dict[str, Any]:
        """Test interview generation for Java topic (should select Marcus)"""
        try:
            payload = {
                "topic": "Java Spring Boot microservices architecture",
                "num_questions": 3,
                "language": "en"
            }
            
            print(f"Generating interview for Java topic...")
            response = self.session.post(f"{self.base_url}/videos/generate", json=payload)
            
            if response.status_code == 200:
                video_data = response.json()
                dialogues = video_data.get("dialogues", [])
                
                if len(dialogues) >= 6:
                    self.log_test("Java Interview Generation", True, f"Generated video with {len(dialogues)} dialogues")
                    return {"success": True, "video": video_data}
                else:
                    self.log_test("Java Interview Generation", False, f"Expected at least 6 dialogues, got {len(dialogues)}")
                    return {"success": False, "video": video_data}
            else:
                self.log_test("Java Interview Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "video": None}
                
        except Exception as e:
            self.log_test("Java Interview Generation", False, f"Error: {str(e)}")
            return {"success": False, "video": None}
    
    def test_interview_generation_french(self) -> Dict[str, Any]:
        """Test interview generation in French (should select Jean for Marketing)"""
        try:
            payload = {
                "topic": "Marketing digital et stratégies de contenu",
                "num_questions": 3,
                "language": "fr"
            }
            
            print(f"Generating interview for French marketing topic...")
            response = self.session.post(f"{self.base_url}/videos/generate", json=payload)
            
            if response.status_code == 200:
                video_data = response.json()
                dialogues = video_data.get("dialogues", [])
                
                if len(dialogues) >= 6:
                    self.log_test("French Interview Generation", True, f"Generated video with {len(dialogues)} dialogues")
                    return {"success": True, "video": video_data}
                else:
                    self.log_test("French Interview Generation", False, f"Expected at least 6 dialogues, got {len(dialogues)}")
                    return {"success": False, "video": video_data}
            else:
                self.log_test("French Interview Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "video": None}
                
        except Exception as e:
            self.log_test("French Interview Generation", False, f"Error: {str(e)}")
            return {"success": False, "video": None}
    
    def test_natural_interjections(self, video_data: Dict) -> bool:
        """Test that dialogues contain natural interjections"""
        if not video_data:
            return False
        
        dialogues = video_data.get("dialogues", [])
        
        # English interjections to look for
        english_interjections = ["Ok,", "Well,", "So,", "That's a good question", "Actually,", "You know,", "I think", "Absolutely"]
        
        # French interjections to look for  
        french_interjections = ["Ok,", "Eh bien,", "Alors,", "C'est une bonne question", "En fait,", "Vous savez,", "Je pense", "Absolument"]
        
        candidate_dialogues = [d for d in dialogues if d.get("role") == "CANDIDATE"]
        interviewer_dialogues = [d for d in dialogues if d.get("role") == "YOUTUBER"]
        
        # Check candidate interjections
        candidate_with_interjections = 0
        for dialogue in candidate_dialogues:
            text = dialogue.get("text", "")
            if any(interjection in text for interjection in english_interjections + french_interjections):
                candidate_with_interjections += 1
        
        # Check interviewer reactions (should be less frequent)
        interviewer_reactions = 0
        for dialogue in interviewer_dialogues:
            text = dialogue.get("text", "")
            if any(reaction in text for reaction in ["Interesting!", "Great!", "Perfect!", "Excellent!", "Intéressant!", "Parfait!"]):
                interviewer_reactions += 1
        
        candidate_percentage = (candidate_with_interjections / len(candidate_dialogues)) * 100 if candidate_dialogues else 0
        
        if candidate_percentage >= 50:  # At least 50% of candidate responses should have interjections
            self.log_test("Natural Interjections", True, 
                         f"Found interjections in {candidate_with_interjections}/{len(candidate_dialogues)} candidate responses ({candidate_percentage:.1f}%)")
            return True
        else:
            self.log_test("Natural Interjections", False, 
                         f"Only {candidate_with_interjections}/{len(candidate_dialogues)} candidate responses have interjections ({candidate_percentage:.1f}%)")
            return False
    
    def test_dialogue_quality(self, video_data: Dict) -> bool:
        """Test dialogue quality and natural conversation flow"""
        if not video_data:
            return False
        
        dialogues = video_data.get("dialogues", [])
        success = True
        
        # Check that candidate answers are detailed (at least 100 characters)
        candidate_dialogues = [d for d in dialogues if d.get("role") == "CANDIDATE"]
        short_answers = [d for d in candidate_dialogues if len(d.get("text", "")) < 100]
        
        if len(short_answers) > 0:
            self.log_test("Dialogue Quality - Answer Length", False, 
                         f"{len(short_answers)}/{len(candidate_dialogues)} candidate answers are too short")
            success = False
        else:
            self.log_test("Dialogue Quality - Answer Length", True, 
                         f"All {len(candidate_dialogues)} candidate answers are detailed")
        
        # Check that questions are meaningful (at least 20 characters)
        interviewer_dialogues = [d for d in dialogues if d.get("role") == "YOUTUBER"]
        short_questions = [d for d in interviewer_dialogues if len(d.get("text", "")) < 20]
        
        if len(short_questions) > 0:
            self.log_test("Dialogue Quality - Question Length", False, 
                         f"{len(short_questions)}/{len(interviewer_dialogues)} questions are too short")
            success = False
        else:
            self.log_test("Dialogue Quality - Question Length", True, 
                         f"All {len(interviewer_dialogues)} questions are meaningful")
        
        return success
    
    def test_multilingual_support(self, english_video: Dict, french_video: Dict) -> bool:
        """Test that multilingual support works correctly"""
        success = True
        
        if not english_video or not french_video:
            self.log_test("Multilingual Support", False, "Missing video data for comparison")
            return False
        
        # Check English video contains English text
        english_dialogues = english_video.get("dialogues", [])
        english_text = " ".join([d.get("text", "") for d in english_dialogues])
        
        # Check French video contains French text
        french_dialogues = french_video.get("dialogues", [])
        french_text = " ".join([d.get("text", "") for d in french_dialogues])
        
        # Simple heuristic: French text should contain French-specific words
        french_indicators = ["le ", "la ", "les ", "de ", "du ", "des ", "que ", "qui ", "avec ", "pour "]
        english_indicators = ["the ", "and ", "with ", "for ", "that ", "this ", "have ", "will "]
        
        french_score = sum(1 for indicator in french_indicators if indicator in french_text.lower())
        english_score = sum(1 for indicator in english_indicators if indicator in english_text.lower())
        
        if french_score >= 3 and english_score >= 3:
            self.log_test("Multilingual Support", True, 
                         f"Detected language-specific patterns (FR: {french_score}, EN: {english_score})")
        else:
            self.log_test("Multilingual Support", False, 
                         f"Language detection unclear (FR: {french_score}, EN: {english_score})")
            success = False
        
        return success
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("="*80)
        print("PERSONA-BASED INTERVIEW GENERATION SYSTEM TESTS")
        print("="*80)
        
        # Basic connectivity tests
        if not self.test_api_health():
            print("❌ API not accessible, stopping tests")
            return
        
        if not self.test_database_health():
            print("❌ Database not accessible, stopping tests")
            return
        
        # Initialize personas
        self.test_initialize_personas()
        
        # Test persona APIs
        personas_result = self.test_get_all_personas()
        if personas_result["success"]:
            self.test_persona_data_quality(personas_result["personas"])
        
        self.test_get_personas_by_type()
        
        # Test interview generation with different topics and languages
        print("\n" + "="*60)
        print("TESTING INTERVIEW GENERATION WITH PERSONA SELECTION")
        print("="*60)
        
        python_result = self.test_interview_generation_python()
        java_result = self.test_interview_generation_java()
        french_result = self.test_interview_generation_french()
        
        # Test natural dialogue features
        print("\n" + "="*60)
        print("TESTING NATURAL DIALOGUE FEATURES")
        print("="*60)
        
        if python_result["success"]:
            self.test_natural_interjections(python_result["video"])
            self.test_dialogue_quality(python_result["video"])
        
        if java_result["success"]:
            self.test_natural_interjections(java_result["video"])
            self.test_dialogue_quality(java_result["video"])
        
        if french_result["success"]:
            self.test_natural_interjections(french_result["video"])
            self.test_dialogue_quality(french_result["video"])
        
        # Test multilingual support
        if python_result["success"] and french_result["success"]:
            self.test_multilingual_support(python_result["video"], french_result["video"])
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    tester = PersonaInterviewTester()
    tester.run_all_tests()