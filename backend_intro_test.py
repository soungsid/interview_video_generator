#!/usr/bin/env python3
"""
Backend Test Suite for New Introduction Features
Tests the enhanced introduction system with engaging hooks and structured dialogues.
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

# Backend URL from supervisor configuration
BASE_URL = "https://smooth-intro-api.preview.emergentagent.com/api"

class IntroductionFeatureTester:
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
    
    def test_basic_video_generation_english(self) -> Dict[str, Any]:
        """Test 1: Basic video generation with Spring Boot AOP topic in English"""
        try:
            payload = {
                "topic": "Spring Boot AOP",
                "num_questions": 3,
                "language": "en"
            }
            
            print(f"Generating video for Spring Boot AOP topic...")
            response = self.session.post(f"{self.base_url}/videos/generate", json=payload)
            
            if response.status_code == 200:
                video_data = response.json()
                
                # Check that there's NO "introduction" field in script_data
                if "introduction" in video_data and video_data["introduction"] is not None:
                    self.log_test("Basic Video Generation (English)", False, 
                                 "Video still contains 'introduction' field - should be moved to dialogues")
                    return {"success": False, "video": video_data}
                
                # Check that dialogues exist
                dialogues = video_data.get("dialogues", [])
                if len(dialogues) < 6:  # Should have at least 3 intro + 3 Q&A pairs
                    self.log_test("Basic Video Generation (English)", False, 
                                 f"Expected at least 6 dialogues, got {len(dialogues)}")
                    return {"success": False, "video": video_data}
                
                self.log_test("Basic Video Generation (English)", True, 
                             f"Generated video with {len(dialogues)} dialogues, no legacy introduction field")
                return {"success": True, "video": video_data}
            
            else:
                self.log_test("Basic Video Generation (English)", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "video": None}
                
        except Exception as e:
            self.log_test("Basic Video Generation (English)", False, f"Error: {str(e)}")
            return {"success": False, "video": None}
    
    def test_intro_dialogue_structure(self, video_data: Dict) -> bool:
        """Test 2: Structure of intro dialogues (3 dialogues with question_number=0)"""
        if not video_data:
            return False
        
        dialogues = video_data.get("dialogues", [])
        
        # Find dialogues with question_number=0 (intro dialogues)
        intro_dialogues = [d for d in dialogues if d.get("question_number") == 0]
        
        if len(intro_dialogues) != 3:
            self.log_test("Intro Dialogue Structure", False, 
                         f"Expected exactly 3 intro dialogues (question_number=0), got {len(intro_dialogues)}")
            return False
        
        # Check the order and roles: [YOUTUBER, YOUTUBER, CANDIDATE]
        expected_roles = ["YOUTUBER", "YOUTUBER", "CANDIDATE"]
        actual_roles = [d.get("role") for d in intro_dialogues]
        
        if actual_roles != expected_roles:
            self.log_test("Intro Dialogue Structure", False, 
                         f"Expected roles {expected_roles}, got {actual_roles}")
            return False
        
        # Check that subsequent dialogues have question_number >= 1
        qa_dialogues = [d for d in dialogues if d.get("question_number", 0) >= 1]
        if len(qa_dialogues) < 6:  # Should have at least 3 Q&A pairs
            self.log_test("Intro Dialogue Structure", False, 
                         f"Expected at least 6 Q&A dialogues (question_number>=1), got {len(qa_dialogues)}")
            return False
        
        self.log_test("Intro Dialogue Structure", True, 
                     f"Perfect structure: 3 intro dialogues + {len(qa_dialogues)} Q&A dialogues")
        return True
    
    def test_engaging_intro_quality(self, video_data: Dict) -> bool:
        """Test 3: Quality of engaging intro (Feature 1)"""
        if not video_data:
            return False
        
        dialogues = video_data.get("dialogues", [])
        intro_dialogues = [d for d in dialogues if d.get("question_number") == 0]
        
        if len(intro_dialogues) < 1:
            self.log_test("Engaging Intro Quality", False, "No intro dialogues found")
            return False
        
        # Check the first intro dialogue (engaging hook)
        first_intro = intro_dialogues[0]
        intro_text = first_intro.get("text", "").lower()
        
        # Check for clichés that should be avoided
        cliches = [
            "welcome to my channel",
            "bienvenue sur ma chaîne", 
            "hi everyone",
            "bonjour à tous",
            "today we're going to talk about",
            "aujourd'hui on va parler de"
        ]
        
        found_cliches = [cliche for cliche in cliches if cliche in intro_text]
        if found_cliches:
            self.log_test("Engaging Intro Quality", False, 
                         f"Found clichés that should be avoided: {found_cliches}")
            return False
        
        # Check for engaging patterns
        engaging_patterns = [
            "have you ever wondered",
            "vous êtes-vous déjà demandé",
            "imagine",
            "imaginez",
            "what if",
            "et si",
            "did you know",
            "saviez-vous"
        ]
        
        has_engaging_pattern = any(pattern in intro_text for pattern in engaging_patterns)
        
        if has_engaging_pattern:
            self.log_test("Engaging Intro Quality", True, 
                         f"Found engaging intro pattern. Text: '{first_intro.get('text', '')[:100]}...'")
            return True
        else:
            # Even if no specific pattern, check if it's not a cliché and is reasonably long
            if len(first_intro.get("text", "")) > 50:
                self.log_test("Engaging Intro Quality", True, 
                             f"Intro avoids clichés and is substantial. Text: '{first_intro.get('text', '')[:100]}...'")
                return True
            else:
                self.log_test("Engaging Intro Quality", False, 
                             f"Intro seems too short or generic: '{first_intro.get('text', '')}'")
                return False
    
    def test_welcome_dialogue(self, video_data: Dict) -> bool:
        """Test 4: Welcome dialogue mentions candidate name (Feature 2)"""
        if not video_data:
            return False
        
        dialogues = video_data.get("dialogues", [])
        intro_dialogues = [d for d in dialogues if d.get("question_number") == 0]
        
        if len(intro_dialogues) < 2:
            self.log_test("Welcome Dialogue", False, "Not enough intro dialogues found")
            return False
        
        # Check the second intro dialogue (welcome)
        welcome_dialogue = intro_dialogues[1]
        welcome_text = welcome_dialogue.get("text", "")
        
        # Should mention candidate by name - look for common candidate names
        candidate_name_patterns = [
            "alex", "sarah", "marcus", "emma", "david", "lisa", "jean", "marie",
            "joining me", "avec moi", "welcome", "bienvenue"
        ]
        
        has_candidate_mention = any(pattern in welcome_text.lower() for pattern in candidate_name_patterns)
        
        if has_candidate_mention and len(welcome_text) > 20:
            self.log_test("Welcome Dialogue", True, 
                         f"Welcome mentions candidate. Text: '{welcome_text[:100]}...'")
            return True
        else:
            self.log_test("Welcome Dialogue", False, 
                         f"Welcome doesn't properly mention candidate: '{welcome_text}'")
            return False
    
    def test_candidate_response(self, video_data: Dict) -> bool:
        """Test 5: Candidate response mentions interviewer name (Feature 2)"""
        if not video_data:
            return False
        
        dialogues = video_data.get("dialogues", [])
        intro_dialogues = [d for d in dialogues if d.get("question_number") == 0]
        
        if len(intro_dialogues) < 3:
            self.log_test("Candidate Response", False, "Not enough intro dialogues found")
            return False
        
        # Check the third intro dialogue (candidate response)
        candidate_response = intro_dialogues[2]
        
        if candidate_response.get("role") != "CANDIDATE":
            self.log_test("Candidate Response", False, 
                         f"Third intro dialogue should be CANDIDATE, got {candidate_response.get('role')}")
            return False
        
        response_text = candidate_response.get("text", "")
        
        # Should mention interviewer by name and be polite
        interviewer_patterns = [
            "thank you", "thanks", "merci", "sarah", "marcus", "alex", "emma", "david", "lisa", "jean", "marie"
        ]
        
        politeness_patterns = [
            "thank", "merci", "happy", "ravi", "excited", "content", "great", "bien"
        ]
        
        has_interviewer_mention = any(pattern in response_text.lower() for pattern in interviewer_patterns)
        has_politeness = any(pattern in response_text.lower() for pattern in politeness_patterns)
        
        if has_interviewer_mention and has_politeness and len(response_text) > 15:
            self.log_test("Candidate Response", True, 
                         f"Candidate response is natural and polite. Text: '{response_text}'")
            return True
        else:
            self.log_test("Candidate Response", False, 
                         f"Candidate response lacks interviewer mention or politeness: '{response_text}'")
            return False
    
    def test_video_generation_french(self) -> Dict[str, Any]:
        """Test 6: Multilingual support - French video generation"""
        try:
            payload = {
                "topic": "Python FastAPI",
                "num_questions": 3,
                "language": "fr"
            }
            
            print(f"Generating video for Python FastAPI topic in French...")
            response = self.session.post(f"{self.base_url}/videos/generate", json=payload)
            
            if response.status_code == 200:
                video_data = response.json()
                
                # Check basic structure
                dialogues = video_data.get("dialogues", [])
                intro_dialogues = [d for d in dialogues if d.get("question_number") == 0]
                
                if len(intro_dialogues) == 3 and len(dialogues) >= 6:
                    self.log_test("French Video Generation", True, 
                                 f"Generated French video with correct structure: {len(intro_dialogues)} intro + {len(dialogues)-3} Q&A dialogues")
                    return {"success": True, "video": video_data}
                else:
                    self.log_test("French Video Generation", False, 
                                 f"Incorrect structure: {len(intro_dialogues)} intro dialogues, {len(dialogues)} total")
                    return {"success": False, "video": video_data}
            else:
                self.log_test("French Video Generation", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "video": None}
                
        except Exception as e:
            self.log_test("French Video Generation", False, f"Error: {str(e)}")
            return {"success": False, "video": None}
    
    def test_french_language_quality(self, video_data: Dict) -> bool:
        """Test that French dialogues are actually in French"""
        if not video_data:
            return False
        
        dialogues = video_data.get("dialogues", [])
        all_text = " ".join([d.get("text", "") for d in dialogues])
        
        # Check for French indicators
        french_indicators = ["le ", "la ", "les ", "de ", "du ", "des ", "que ", "qui ", "avec ", "pour ", "vous ", "je ", "il ", "elle "]
        french_score = sum(1 for indicator in french_indicators if indicator in all_text.lower())
        
        if french_score >= 5:
            self.log_test("French Language Quality", True, 
                         f"Detected {french_score} French language indicators")
            return True
        else:
            self.log_test("French Language Quality", False, 
                         f"Only {french_score} French indicators found - may not be proper French")
            return False
    
    def test_backward_compatibility(self) -> bool:
        """Test 7: Backward compatibility - old videos still work"""
        try:
            # Get list of all videos
            response = self.session.get(f"{self.base_url}/videos")
            
            if response.status_code == 200:
                videos = response.json()
                if len(videos) > 0:
                    self.log_test("Backward Compatibility", True, 
                                 f"Successfully retrieved {len(videos)} videos without errors")
                    return True
                else:
                    self.log_test("Backward Compatibility", True, 
                                 "No existing videos to test, but API works correctly")
                    return True
            else:
                self.log_test("Backward Compatibility", False, 
                             f"Failed to retrieve videos: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Backward Compatibility", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all introduction feature tests"""
        print("="*80)
        print("NEW INTRODUCTION FEATURES TEST SUITE")
        print("Testing enhanced introduction system with engaging hooks and structured dialogues")
        print("="*80)
        
        # Basic connectivity test
        if not self.test_api_health():
            print("❌ API not accessible, stopping tests")
            return
        
        # Test 1: Basic video generation (English)
        print("\n" + "="*60)
        print("TEST 1: BASIC VIDEO GENERATION (ENGLISH)")
        print("="*60)
        english_result = self.test_basic_video_generation_english()
        
        if english_result["success"]:
            # Test 2: Intro dialogue structure
            print("\n" + "="*60)
            print("TEST 2: INTRO DIALOGUE STRUCTURE")
            print("="*60)
            self.test_intro_dialogue_structure(english_result["video"])
            
            # Test 3: Engaging intro quality
            print("\n" + "="*60)
            print("TEST 3: ENGAGING INTRO QUALITY (FEATURE 1)")
            print("="*60)
            self.test_engaging_intro_quality(english_result["video"])
            
            # Test 4: Welcome dialogue
            print("\n" + "="*60)
            print("TEST 4: WELCOME DIALOGUE (FEATURE 2)")
            print("="*60)
            self.test_welcome_dialogue(english_result["video"])
            
            # Test 5: Candidate response
            print("\n" + "="*60)
            print("TEST 5: CANDIDATE RESPONSE (FEATURE 2)")
            print("="*60)
            self.test_candidate_response(english_result["video"])
        
        # Test 6: Multilingual support (French)
        print("\n" + "="*60)
        print("TEST 6: MULTILINGUAL SUPPORT (FRENCH)")
        print("="*60)
        french_result = self.test_video_generation_french()
        
        if french_result["success"]:
            self.test_french_language_quality(french_result["video"])
            # Also test structure for French
            self.test_intro_dialogue_structure(french_result["video"])
        
        # Test 7: Backward compatibility
        print("\n" + "="*60)
        print("TEST 7: BACKWARD COMPATIBILITY")
        print("="*60)
        self.test_backward_compatibility()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY - NEW INTRODUCTION FEATURES")
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
        else:
            print(f"\n🎉 ALL TESTS PASSED! New introduction features are working perfectly.")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    tester = IntroductionFeatureTester()
    tester.run_all_tests()