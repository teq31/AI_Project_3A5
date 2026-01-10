"""
Modul pentru generarea întrebărilor bazate pe teoria din cursuri.
Citește teoria din fișiere JSON și generează întrebări din template-uri.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, Optional, List

# Calea către directorul cu teoria
THEORY_DATA_PATH = Path(__file__).parent.parent / "data" / "theory"


class TheoryQuestionGenerator:
    """Generează întrebări bazate pe teoria din cursuri"""
    
    def __init__(self, theory_file: str = "example_theory.json"):
        """Încarcă teoria dintr-un fișier JSON"""
        theory_path = THEORY_DATA_PATH / theory_file
        if not theory_path.exists():
            raise FileNotFoundError(f"Theory file not found: {theory_path}")
        
        with open(theory_path, 'r', encoding='utf-8') as f:
            self.theory_data = json.load(f)
    
    def get_available_topics(self) -> List[Dict[str, Any]]:
        """Returnează lista de topic-uri disponibile"""
        return [
            {
                "topic_id": topic["topic_id"],
                "topic_name": topic["topic_name"],
                "difficulty": topic.get("difficulty", "medium"),
                "category": topic.get("category", "general")
            }
            for topic in self.theory_data.get("topics", [])
        ]
    
    def generate_question(self, topic_id: Optional[str] = None, 
                         question_type: Optional[str] = None, 
                         seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generează o întrebare aleatorie pentru un topic.
        
        Args:
            topic_id: ID-ul topicului (ex: "nash_equilibrium_basics"). Dacă None, alege aleatoriu.
            question_type: Tipul întrebării (opțional, altfel aleatoriu)
            seed: Seed pentru reproducibilitate
        """
        if seed is not None:
            random.seed(seed)
        
        # Alege topic-ul
        topics = self.theory_data.get("topics", [])
        if not topics:
            raise ValueError("No topics found in theory data")
        
        if topic_id:
            topic = next((t for t in topics if t["topic_id"] == topic_id), None)
            if not topic:
                raise ValueError(f"Topic {topic_id} not found")
        else:
            topic = random.choice(topics)
        
        # Alege template-ul
        templates = topic.get("question_templates", [])
        if not templates:
            raise ValueError(f"No question templates found for topic {topic['topic_id']}")
        
        if question_type:
            templates = [t for t in templates if t.get("type") == question_type]
            if not templates:
                raise ValueError(f"No templates found for type {question_type} in topic {topic['topic_id']}")
        
        template = random.choice(templates)
        
        # Generează întrebarea
        return self._build_question_from_template(template, topic, seed)
    
    def _build_question_from_template(self, template: Dict, topic: Dict, 
                                     seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebarea din template"""
        question_type = template.get("type", "multiple_choice")
        
        if question_type == "multiple_choice":
            return self._build_multiple_choice(template, topic, seed)
        elif question_type == "true_false":
            return self._build_true_false(template, topic, seed)
        elif question_type == "fill_blank":
            return self._build_fill_blank(template, topic, seed)
        elif question_type == "short_answer":
            return self._build_short_answer(template, topic, seed)
        elif question_type == "justification":
            return self._build_justification(template, topic, seed)
        elif question_type == "example":
            return self._build_example(template, topic, seed)
        elif question_type == "comparison":
            return self._build_comparison(template, topic, seed)
        elif question_type == "definition":
            return self._build_definition(template, topic, seed)
        elif question_type == "calculation":
            return self._build_calculation(template, topic, seed)
        elif question_type == "matrix_analysis":
            return self._build_matrix_analysis(template, topic, seed)
        else:
            raise ValueError(f"Unsupported question type: {question_type}")
    
    def _build_multiple_choice(self, template: Dict, topic: Dict, 
                               seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare multiple choice"""
        if seed is not None:
            random.seed(seed)
        
        # Amestecă opțiunile
        correct_answer = template["correct_answer"]
        distractors = template.get("distractors", [])
        options = [correct_answer] + distractors
        random.shuffle(options)
        
        correct_index = options.index(correct_answer)
        
        return {
            "type": "theory",
            "theory_type": "multiple_choice",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "options": options,
            "correct_index": correct_index,
            "correct_answer": correct_answer,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "key_concepts": topic.get("theory", {}).get("key_concepts", [])
            }
        }
    
    def _build_true_false(self, template: Dict, topic: Dict, 
                         seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare true/false"""
        correct_answer = template["correct_answer"]
        
        return {
            "type": "theory",
            "theory_type": "true_false",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_answer": correct_answer,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "key_concepts": topic.get("theory", {}).get("key_concepts", [])
            }
        }
    
    def _build_fill_blank(self, template: Dict, topic: Dict, 
                         seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare fill-in-the-blank"""
        correct_answers = template.get("correct_answers", [])
        case_sensitive = template.get("case_sensitive", False)
        
        return {
            "type": "theory",
            "theory_type": "fill_blank",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_answers": correct_answers,
            "case_sensitive": case_sensitive,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "key_concepts": topic.get("theory", {}).get("key_concepts", [])
            }
        }
    
    def _build_short_answer(self, template: Dict, topic: Dict, 
                           seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare cu răspuns scurt"""
        correct_keywords = template.get("correct_keywords", [])
        min_keywords = template.get("min_keywords", 2)
        
        return {
            "type": "theory",
            "theory_type": "short_answer",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "min_keywords": min_keywords,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "key_concepts": topic.get("theory", {}).get("key_concepts", [])
            }
        }
    
    def _build_justification(self, template: Dict, topic: Dict, 
                           seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare care cere justificare"""
        correct_keywords = template.get("correct_keywords", [])
        required_concepts = template.get("required_concepts", [])
        min_keywords = template.get("min_keywords", 2)
        
        return {
            "type": "theory",
            "theory_type": "justification",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "required_concepts": required_concepts,
            "min_keywords": min_keywords,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "key_concepts": topic.get("theory", {}).get("key_concepts", [])
            }
        }
    
    def _build_example(self, template: Dict, topic: Dict, 
                      seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare care cere exemple"""
        correct_keywords = template.get("correct_keywords", [])
        example_types = template.get("example_types", [])
        min_keywords = template.get("min_keywords", 2)
        
        return {
            "type": "theory",
            "theory_type": "example",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "example_types": example_types,
            "min_keywords": min_keywords,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "examples": topic.get("theory", {}).get("examples", [])
            }
        }
    
    def _build_comparison(self, template: Dict, topic: Dict, 
                         seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare care cere compararea a două concepte"""
        concepts_to_compare = template.get("concepts_to_compare", [])
        comparison_keywords = template.get("comparison_keywords", [])
        min_keywords = template.get("min_keywords", 3)
        
        return {
            "type": "theory",
            "theory_type": "comparison",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "concepts_to_compare": concepts_to_compare,
            "comparison_keywords": comparison_keywords,
            "min_keywords": min_keywords,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "key_concepts": topic.get("theory", {}).get("key_concepts", [])
            }
        }
    
    def _build_definition(self, template: Dict, topic: Dict, 
                        seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare care cere definiție"""
        correct_keywords = template.get("correct_keywords", [])
        definition_elements = template.get("definition_elements", [])
        min_keywords = template.get("min_keywords", 3)
        
        return {
            "type": "theory",
            "theory_type": "definition",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "definition_elements": definition_elements,
            "min_keywords": min_keywords,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "key_concepts": topic.get("theory", {}).get("key_concepts", [])
            }
        }
    
    def _build_calculation(self, template: Dict, topic: Dict, 
                          seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare care cere calcul (cu răspunsuri flexibile)"""
        correct_answer = template.get("correct_answer", "")
        correct_answer_numeric = template.get("correct_answer_numeric", None)
        acceptable_range = template.get("acceptable_range", None)  # (min, max) pentru răspunsuri numerice
        calculation_steps = template.get("calculation_steps", [])
        
        return {
            "type": "theory",
            "theory_type": "calculation",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_answer": correct_answer,
            "correct_answer_numeric": correct_answer_numeric,
            "acceptable_range": acceptable_range,
            "calculation_steps": calculation_steps,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "formulas": topic.get("theory", {}).get("formulas", [])
            }
        }
    
    def _build_matrix_analysis(self, template: Dict, topic: Dict, 
                              seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebare despre analiza jocurilor matriceale (Nash, etc.)"""
        matrix_data = template.get("matrix_data", {})
        analysis_type = template.get("analysis_type", "nash_equilibrium")  # nash, dominant_strategy, etc.
        correct_answer = template.get("correct_answer", "")
        correct_keywords = template.get("correct_keywords", [])
        
        return {
            "type": "theory",
            "theory_type": "matrix_analysis",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "matrix_data": matrix_data,
            "analysis_type": analysis_type,
            "correct_answer": correct_answer,
            "correct_keywords": correct_keywords,
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic.get("theory", {}).get("definition", ""),
                "examples": topic.get("theory", {}).get("examples", [])
            }
        }


def build_question_payload(topic_id: Optional[str] = None,
                       question_type: Optional[str] = None,
                       theory_file: str = "example_theory.json",
                       seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Funcție helper pentru generarea unei întrebări de teorie.
    
    Args:
        topic_id: ID-ul topicului (opțional)
        question_type: Tipul întrebării (opțional)
        theory_file: Numele fișierului cu teoria (default: "example_theory.json")
        seed: Seed pentru reproducibilitate
    """
    generator = TheoryQuestionGenerator(theory_file)
    question = generator.generate_question(topic_id, question_type, seed)
    
    return {
        "question": question,
        "payload": question  # Pentru compatibilitate cu sistemul existent
    }

