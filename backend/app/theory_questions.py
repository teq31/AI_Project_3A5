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
        Dacă nu există template pentru tipul cerut, generează dinamic din teoria topic-ului.
        
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
        
        # Dacă nu este specificat tipul, alege aleatoriu
        if not question_type:
            available_types = ["multiple_choice", "true_false", "fill_blank", 
                             "short_answer", "justification", "definition", 
                             "example", "comparison"]
            question_type = random.choice(available_types)
        
        # Încearcă mai întâi să folosească template-urile existente
        templates = topic.get("question_templates", [])
        matching_templates = [t for t in templates if t.get("type") == question_type]
        
        # Dacă există template-uri pentru tipul cerut, folosește-le
        if matching_templates:
            template = random.choice(matching_templates)
            return self._build_question_from_template(template, topic, seed)
        
        # Altfel, generează dinamic din teoria topic-ului
        return self._generate_dynamic_question(topic, question_type, seed)
    
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
        explanation = template.get("explanation", "")
        
        # Folosește explanation ca correct_answer pentru similaritate semantică
        # Dacă nu există explanation, construiește un răspuns din keywords
        correct_answer = explanation if explanation else " ".join(correct_keywords[:5])
        
        return {
            "type": "theory",
            "theory_type": "short_answer",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "correct_answer": correct_answer,  # Adăugat pentru similaritate semantică
            "min_keywords": min_keywords,
            "explanation": explanation,
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
        explanation = template.get("explanation", "")
        
        # Folosește explanation ca correct_answer pentru similaritate semantică
        # Dacă nu există explanation, construiește un răspuns din keywords și concepts
        if explanation:
            correct_answer = explanation
        else:
            all_concepts = correct_keywords + required_concepts
            correct_answer = " ".join(all_concepts[:5])
        
        return {
            "type": "theory",
            "theory_type": "justification",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "required_concepts": required_concepts,
            "correct_answer": correct_answer,  # Adăugat pentru similaritate semantică
            "min_keywords": min_keywords,
            "explanation": explanation,
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
        explanation = template.get("explanation", "")
        
        # Folosește explanation ca correct_answer pentru similaritate semantică
        correct_answer = explanation if explanation else " ".join(correct_keywords[:5])
        
        return {
            "type": "theory",
            "theory_type": "example",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "example_types": example_types,
            "correct_answer": correct_answer,  # Adăugat pentru similaritate semantică
            "min_keywords": min_keywords,
            "explanation": explanation,
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
        explanation = template.get("explanation", "")
        
        # Folosește explanation ca correct_answer pentru similaritate semantică
        correct_answer = explanation if explanation else " ".join(comparison_keywords[:5])
        
        return {
            "type": "theory",
            "theory_type": "comparison",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "concepts_to_compare": concepts_to_compare,
            "comparison_keywords": comparison_keywords,
            "correct_answer": correct_answer,  # Adăugat pentru similaritate semantică
            "min_keywords": min_keywords,
            "explanation": explanation,
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
        explanation = template.get("explanation", "")
        
        # Folosește explanation ca correct_answer pentru similaritate semantică
        correct_answer = explanation if explanation else " ".join(correct_keywords[:5])
        
        return {
            "type": "theory",
            "theory_type": "definition",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": template.get("difficulty", topic.get("difficulty", "medium")),
            "question_text": template["template"],
            "correct_keywords": correct_keywords,
            "definition_elements": definition_elements,
            "correct_answer": correct_answer,  # Adăugat pentru similaritate semantică
            "min_keywords": min_keywords,
            "explanation": explanation,
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
    
    def _generate_dynamic_question(self, topic: Dict, question_type: str, 
                                  seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic o întrebare bazată pe teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        theory = topic.get("theory", {})
        
        if question_type == "multiple_choice":
            return self._generate_dynamic_multiple_choice(topic, theory, seed)
        elif question_type == "true_false":
            return self._generate_dynamic_true_false(topic, theory, seed)
        elif question_type == "fill_blank":
            return self._generate_dynamic_fill_blank(topic, theory, seed)
        elif question_type == "short_answer":
            return self._generate_dynamic_short_answer(topic, theory, seed)
        elif question_type == "justification":
            return self._generate_dynamic_justification(topic, theory, seed)
        elif question_type == "definition":
            return self._generate_dynamic_definition(topic, theory, seed)
        elif question_type == "example":
            return self._generate_dynamic_example(topic, theory, seed)
        elif question_type == "comparison":
            return self._generate_dynamic_comparison(topic, theory, seed)
        else:
            # Fallback la short_answer
            return self._generate_dynamic_short_answer(topic, theory, seed)
    
    def _generate_dynamic_multiple_choice(self, topic: Dict, theory: Dict, 
                                         seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare multiple choice din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        # Extrage informații din teorie
        definition = theory.get("definition", "")
        key_concepts = theory.get("key_concepts", [])
        theorems = theory.get("theorems", [])
        
        # Alege o sursă aleatorie pentru întrebare
        sources = []
        if definition:
            sources.append(("definition", definition))
        if key_concepts:
            for concept in key_concepts[:3]:  # Limitează la primele 3
                if isinstance(concept, dict):
                    sources.append(("concept", concept))
        if theorems:
            for theorem in theorems[:2]:  # Limitează la primele 2
                sources.append(("theorem", theorem))
        
        if not sources:
            # Fallback: folosește numele topic-ului
            question_text = f"Care este definiția corectă pentru {topic.get('topic_name', 'acest concept')}?"
            correct_answer = definition if definition else f"Concept din domeniul {topic.get('category', 'AI')}"
        else:
            source_type, source_data = random.choice(sources)
            
            if source_type == "definition":
                question_text = f"Care este definiția corectă pentru {topic.get('topic_name', 'acest concept')}?"
                correct_answer = definition
            elif source_type == "concept":
                concept_name = source_data.get("concept", "acest concept")
                question_text = f"Care este definiția corectă pentru {concept_name}?"
                correct_answer = source_data.get("definition", "")
            elif source_type == "theorem":
                theorem_name = source_data.get("name", "teorema")
                question_text = f"Conform {theorem_name}, care este afirmația corectă?"
                correct_answer = source_data.get("statement", "")
            else:
                question_text = f"Care este definiția corectă pentru {topic.get('topic_name', 'acest concept')}?"
                correct_answer = definition if definition else ""
        
        # Generează distractors din alte concepte sau greșeli comune
        distractors = []
        common_mistakes = theory.get("common_mistakes", [])
        for mistake in common_mistakes[:2]:
            distractors.append(mistake.get("mistake", ""))
        
        # Adaugă distractors generice dacă nu sunt suficiente
        generic_distractors = [
            "Este un algoritm de optimizare",
            "Este o metodă de căutare",
            "Garantează întotdeauna soluția optimă",
            "Funcționează doar pentru probleme mici"
        ]
        while len(distractors) < 3:
            distractor = random.choice(generic_distractors)
            if distractor not in distractors:
                distractors.append(distractor)
        
        # Amestecă opțiunile
        options = [correct_answer] + distractors[:3]
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return {
            "type": "theory",
            "theory_type": "multiple_choice",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "options": options,
            "correct_index": correct_index,
            "correct_answer": correct_answer,
            "explanation": definition if definition else f"Răspunsul corect este bazat pe teoria {topic.get('topic_name', '')}.",
            "theory_reference": {
                "definition": definition,
                "key_concepts": key_concepts
            }
        }
    
    def _generate_dynamic_true_false(self, topic: Dict, theory: Dict, 
                                    seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare true/false din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        theorems = theory.get("theorems", [])
        common_mistakes = theory.get("common_mistakes", [])
        key_concepts = theory.get("key_concepts", [])
        
        # Alege o sursă pentru afirmație
        if theorems:
            theorem = random.choice(theorems)
            question_text = theorem.get("statement", "")
            correct_answer = True
            explanation = theorem.get("importance", theorem.get("proof_hint", ""))
        elif common_mistakes:
            mistake = random.choice(common_mistakes)
            question_text = mistake.get("mistake", "")
            correct_answer = False
            explanation = mistake.get("correction", "")
        elif key_concepts:
            concept = random.choice(key_concepts)
            if isinstance(concept, dict):
                # Creează o afirmație falsă bazată pe concept
                concept_name = concept.get("concept", "")
                question_text = f"{concept_name} garantează întotdeauna soluția optimă."
                correct_answer = False
                explanation = concept.get("definition", "")
            else:
                question_text = f"{topic.get('topic_name', 'Acest concept')} este întotdeauna corect."
                correct_answer = False
                explanation = theory.get("definition", "")
        else:
            # Fallback
            question_text = f"{topic.get('topic_name', 'Acest concept')} este întotdeauna aplicabil."
            correct_answer = False
            explanation = theory.get("definition", "")
        
        # Pentru NLP, convertim boolean-ul într-un string explicativ
        if correct_answer is True:
            correct_answer_str = f"Afirmația este adevărată. {explanation}"
        else:
            correct_answer_str = f"Afirmația este falsă. {explanation}"
        
        return {
            "type": "theory",
            "theory_type": "true_false",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "correct_answer": correct_answer,  # Boolean pentru grading
            "correct_answer_str": correct_answer_str,  # String pentru NLP
            "explanation": explanation,
            "theory_reference": {
                "definition": theory.get("definition", ""),
                "key_concepts": key_concepts
            }
        }
    
    def _generate_dynamic_fill_blank(self, topic: Dict, theory: Dict, 
                                    seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare fill-in-the-blank din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        key_concepts = theory.get("key_concepts", [])
        definition = theory.get("definition", "")
        
        # Caută formule sau definiții cu părți care pot fi completate
        if key_concepts:
            concept = random.choice(key_concepts)
            if isinstance(concept, dict):
                formula = concept.get("formula", "")
                concept_name = concept.get("concept", "")
                
                if formula:
                    # Extrage partea cheie din formulă
                    if "=" in formula:
                        parts = formula.split("=", 1)
                        question_text = f"{concept_name}: {parts[0].strip()} = _____"
                        correct_answers = [parts[1].strip(), formula]
                    else:
                        question_text = f"{concept_name}: _____"
                        correct_answers = [formula, concept_name]
                else:
                    # Folosește definiția
                    question_text = f"{concept_name} este: _____"
                    correct_answers = [concept.get("definition", ""), concept_name]
            else:
                question_text = f"{topic.get('topic_name', 'Acest concept')} este: _____"
                correct_answers = [definition, topic.get("topic_name", "")]
        else:
            # Fallback
            question_text = f"{topic.get('topic_name', 'Acest concept')} este: _____"
            correct_answers = [definition, topic.get("topic_name", "")]
        
        # Pentru NLP, folosește primul răspuns corect ca string
        correct_answer_str = correct_answers[0] if correct_answers else definition if definition else topic.get("topic_name", "")
        if isinstance(correct_answer_str, list):
            correct_answer_str = ", ".join(correct_answer_str)
        
        return {
            "type": "theory",
            "theory_type": "fill_blank",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "correct_answers": correct_answers,
            "correct_answer": str(correct_answer_str),  # Pentru NLP
            "case_sensitive": False,
            "explanation": definition if definition else f"Răspunsul corect este bazat pe definiția {topic.get('topic_name', '')}.",
            "theory_reference": {
                "definition": definition,
                "key_concepts": key_concepts
            }
        }
    
    def _generate_dynamic_short_answer(self, topic: Dict, theory: Dict, 
                                      seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare short answer din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        definition = theory.get("definition", "")
        key_concepts = theory.get("key_concepts", [])
        
        # Generează întrebări variate
        question_templates = [
            f"Explică ce este {topic.get('topic_name', 'acest concept')}.",
            f"Care este definiția pentru {topic.get('topic_name', 'acest concept')}?",
            f"Descrie {topic.get('topic_name', 'acest concept')}.",
        ]
        
        if key_concepts:
            concept = random.choice(key_concepts)
            if isinstance(concept, dict):
                question_templates.append(f"Explică conceptul {concept.get('concept', '')}.")
        
        question_text = random.choice(question_templates)
        
        # Extrage keywords din definiție și concepte
        correct_keywords = []
        if definition:
            # Extrage cuvinte cheie din definiție (cuvinte de 4+ litere)
            words = definition.split()
            correct_keywords = [w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5]
        
        if key_concepts:
            for concept in key_concepts[:2]:
                if isinstance(concept, dict):
                    concept_name = concept.get("concept", "")
                    if concept_name:
                        correct_keywords.append(concept_name.lower())
        
        # Elimină duplicatele
        correct_keywords = list(dict.fromkeys(correct_keywords))[:5]
        
        # Asigură-te că avem cel puțin 2 keywords
        if len(correct_keywords) < 2:
            topic_name = topic.get("topic_name", "").lower()
            if topic_name and topic_name not in correct_keywords:
                correct_keywords.append(topic_name)
            if definition:
                words = definition.split()
                additional = [w.lower().strip('.,!?;:') for w in words if len(w) > 3 and w.lower().strip('.,!?;:') not in correct_keywords][:3]
                correct_keywords.extend(additional)
        
        # Asigură-te că correct_answer este setat
        if not definition:
            definition = f"{topic.get('topic_name', 'Acest concept')} este un concept important din domeniul {topic.get('category', 'AI')}."
        
        return {
            "type": "theory",
            "theory_type": "short_answer",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "correct_keywords": correct_keywords[:5],
            "correct_answer": definition,
            "min_keywords": max(2, min(3, len(correct_keywords) // 2)),
            "explanation": definition,
            "theory_reference": {
                "definition": definition,
                "key_concepts": key_concepts
            }
        }
    
    def _generate_dynamic_justification(self, topic: Dict, theory: Dict, 
                                       seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare justification din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        key_concepts = theory.get("key_concepts", [])
        examples = theory.get("examples", [])
        
        # Generează întrebări care cer justificare
        question_templates = [
            f"De ce este {topic.get('topic_name', 'acest concept')} important? Justificați.",
            f"Care sunt avantajele {topic.get('topic_name', 'acest concept')}? Justificați.",
            f"Când ar trebui folosit {topic.get('topic_name', 'acest concept')}? Justificați.",
        ]
        
        if examples:
            example = random.choice(examples)
            example_name = example.get("name", "")
            if example_name:
                question_templates.append(f"De ce este {example_name} un exemplu bun pentru {topic.get('topic_name', 'acest concept')}? Justificați.")
        
        question_text = random.choice(question_templates)
        
        # Extrage keywords și concepte
        correct_keywords = []
        required_concepts = []
        
        if key_concepts:
            for concept in key_concepts[:3]:
                if isinstance(concept, dict):
                    concept_name = concept.get("concept", "")
                    if concept_name:
                        required_concepts.append(concept_name)
                        correct_keywords.append(concept_name.lower())
                    definition = concept.get("definition", "")
                    if definition:
                        words = definition.split()
                        correct_keywords.extend([w.lower().strip('.,!?;:') for w in words if len(w) > 4][:3])
        
        # Elimină duplicatele
        correct_keywords = list(dict.fromkeys(correct_keywords))[:8]
        
        # Asigură-te că avem keywords
        if not correct_keywords:
            definition = theory.get("definition", "")
            if definition:
                words = definition.split()
                correct_keywords = [w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5]
            topic_name = topic.get("topic_name", "").lower()
            if topic_name and topic_name not in correct_keywords:
                correct_keywords.append(topic_name)
        
        explanation = theory.get("definition", "")
        if not explanation:
            explanation = f"{topic.get('topic_name', 'Acest concept')} este important pentru aplicarea algoritmilor de căutare și optimizare."
        if examples:
            example = examples[0]
            explanation += f" Exemplu: {example.get('name', '')} - {example.get('description', '')}"
        
        return {
            "type": "theory",
            "theory_type": "justification",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "correct_keywords": correct_keywords[:8],
            "required_concepts": required_concepts[:2],
            "correct_answer": explanation,
            "min_keywords": max(3, min(4, len(correct_keywords) // 2)),
            "explanation": explanation,
            "theory_reference": {
                "definition": theory.get("definition", ""),
                "key_concepts": key_concepts
            }
        }
    
    def _generate_dynamic_definition(self, topic: Dict, theory: Dict, 
                                   seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare definition din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        key_concepts = theory.get("key_concepts", [])
        
        if key_concepts:
            concept = random.choice(key_concepts)
            if isinstance(concept, dict):
                concept_name = concept.get("concept", "")
                question_text = f"Care este definiția pentru {concept_name}? Exemplificați."
                correct_answer = concept.get("definition", "")
                example = concept.get("example", "")
                explanation = correct_answer
                if example:
                    explanation += f" Exemplu: {example}"
                
                # Extrage keywords
                words = correct_answer.split()
                correct_keywords = [w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5]
                correct_keywords.append(concept_name.lower())
            else:
                question_text = f"Care este definiția pentru {topic.get('topic_name', 'acest concept')}? Exemplificați."
                correct_answer = theory.get("definition", "")
                explanation = correct_answer
                words = correct_answer.split()
                correct_keywords = [w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5]
        else:
            question_text = f"Care este definiția pentru {topic.get('topic_name', 'acest concept')}? Exemplificați."
            correct_answer = theory.get("definition", "")
            explanation = correct_answer
            words = correct_answer.split()
            correct_keywords = [w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5]
        
        return {
            "type": "theory",
            "theory_type": "definition",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "correct_keywords": correct_keywords[:5],
            "correct_answer": correct_answer if correct_answer else " ".join(correct_keywords),
            "min_keywords": max(3, len(correct_keywords) // 2),
            "explanation": explanation if explanation else f"Definiția corectă este bazată pe teoria {topic.get('topic_name', '')}.",
            "theory_reference": {
                "definition": theory.get("definition", ""),
                "key_concepts": key_concepts
            }
        }
    
    def _generate_dynamic_example(self, topic: Dict, theory: Dict, 
                                 seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare example din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        examples = theory.get("examples", [])
        key_concepts = theory.get("key_concepts", [])
        algorithms = theory.get("algorithms", [])
        optimization_tips = theory.get("optimization_tips", [])
        definition = theory.get("definition", "")
        
        question_text = f"Dați un exemplu de aplicare a {topic.get('topic_name', 'acest concept')}."
        
        correct_keywords = []
        explanation = ""
        
        if examples:
            example = random.choice(examples)
            example_name = example.get("name", "")
            example_desc = example.get("description", "")
            explanation = f"Exemplu: {example_name}. {example_desc}"
            correct_keywords.append(example_name.lower())
            words = example_desc.split()
            correct_keywords.extend([w.lower().strip('.,!?;:') for w in words if len(w) > 4][:4])
        elif algorithms:
            # Folosește algoritmi ca exemple
            algorithm = random.choice(algorithms)
            algo_name = algorithm.get("name", topic.get("topic_name", ""))
            improvement = algorithm.get("improvement", "")
            if improvement:
                explanation = f"Exemplu: {algo_name} poate fi folosit pentru {improvement.lower()}."
                words = improvement.split()
                correct_keywords.extend([w.lower().strip('.,!?;:') for w in words if len(w) > 4][:4])
            else:
                explanation = f"Exemplu: {algo_name} este folosit în jocuri de strategie precum șah sau X și O."
                correct_keywords.extend(["joc", "strategie", "șah", "x", "o"])
        elif optimization_tips:
            # Folosește tips ca exemple
            tip = random.choice(optimization_tips)
            explanation = f"Exemplu: {tip}."
            words = tip.split()
            correct_keywords.extend([w.lower().strip('.,!?;:') for w in words if len(w) > 4][:4])
        elif key_concepts:
            # Folosește exemple din concepte
            for concept in key_concepts[:3]:
                if isinstance(concept, dict):
                    example = concept.get("example", "")
                    concept_name = concept.get("concept", "")
                    if example:
                        if not explanation:
                            explanation = f"Exemplu: {example}"
                        else:
                            explanation += f" Alt exemplu: {example}."
                        correct_keywords.append(concept_name.lower())
                        words = example.split()
                        correct_keywords.extend([w.lower().strip('.,!?;:') for w in words if len(w) > 4][:3])
                    elif concept_name:
                        # Construiește un exemplu bazat pe concept
                        concept_def = concept.get("definition", "")
                        if concept_def:
                            correct_keywords.append(concept_name.lower())
                            words = concept_def.split()
                            correct_keywords.extend([w.lower().strip('.,!?;:') for w in words if len(w) > 4][:3])
        
        # Dacă încă nu avem keywords, folosește definiția și numele topic-ului
        if not correct_keywords:
            topic_name = topic.get("topic_name", "")
            if topic_name:
                correct_keywords.append(topic_name.lower())
            if definition:
                words = definition.split()
                correct_keywords.extend([w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5])
                if not explanation:
                    explanation = f"Un exemplu de aplicare a {topic_name} ar putea fi ilustrat prin: {definition[:100]}..."
        
        # Dacă încă nu avem explanation, construiește unul generic dar relevant
        if not explanation:
            topic_name = topic.get("topic_name", "")
            explanation = f"Un exemplu de aplicare a {topic_name} ar putea fi o situație practică unde se folosește {topic_name.lower()} pentru a rezolva o problemă specifică."
            if definition:
                # Extrage cuvinte cheie din definiție pentru a face răspunsul mai relevant
                key_terms = [w for w in definition.split() if len(w) > 5][:3]
                if key_terms:
                    explanation = f"Un exemplu de aplicare a {topic_name} ar putea include: {', '.join(key_terms)}."
        
        correct_keywords = list(dict.fromkeys(correct_keywords))[:6]
        
        # Asigură-te că avem cel puțin 2 keywords
        if len(correct_keywords) < 2:
            topic_name = topic.get("topic_name", "").lower()
            if topic_name and topic_name not in correct_keywords:
                correct_keywords.append(topic_name)
            if definition:
                words = definition.split()
                additional = [w.lower().strip('.,!?;:') for w in words if len(w) > 4 and w.lower().strip('.,!?;:') not in correct_keywords][:2]
                correct_keywords.extend(additional)
        
        return {
            "type": "theory",
            "theory_type": "example",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "correct_keywords": correct_keywords[:6],
            "correct_answer": explanation,
            "min_keywords": max(2, min(3, len(correct_keywords) // 2)),
            "explanation": explanation,
            "theory_reference": {
                "definition": definition,
                "examples": examples
            }
        }
    
    def _generate_dynamic_comparison(self, topic: Dict, theory: Dict, 
                                    seed: Optional[int]) -> Dict[str, Any]:
        """Generează dinamic întrebare comparison din teoria topic-ului"""
        if seed is not None:
            random.seed(seed)
        
        key_concepts = theory.get("key_concepts", [])
        
        if len(key_concepts) >= 2:
            # Alege două concepte pentru comparare
            concepts = random.sample(key_concepts, min(2, len(key_concepts)))
            concept1 = concepts[0] if isinstance(concepts[0], dict) else None
            concept2 = concepts[1] if isinstance(concepts[1], dict) else None
            
            if concept1 and concept2:
                name1 = concept1.get("concept", "")
                name2 = concept2.get("concept", "")
                question_text = f"Comparați {name1} și {name2}."
                
                # Extrage keywords din ambele definiții
                def1 = concept1.get("definition", "")
                def2 = concept2.get("definition", "")
                comparison_keywords = []
                words1 = def1.split()
                words2 = def2.split()
                comparison_keywords.extend([w.lower().strip('.,!?;:') for w in words1 + words2 if len(w) > 4][:6])
                comparison_keywords.extend([name1.lower(), name2.lower()])
                
                explanation = f"{name1}: {def1}. {name2}: {def2}."
            else:
                question_text = f"Comparați două aspecte ale {topic.get('topic_name', 'acest concept')}."
                comparison_keywords = []
                explanation = theory.get("definition", "")
        else:
            question_text = f"Comparați {topic.get('topic_name', 'acest concept')} cu o metodă alternativă."
            comparison_keywords = []
            explanation = theory.get("definition", "")
        
        comparison_keywords = list(dict.fromkeys(comparison_keywords))[:6]
        
        return {
            "type": "theory",
            "theory_type": "comparison",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic.get("difficulty", "medium"),
            "question_text": question_text,
            "comparison_keywords": comparison_keywords,
            "correct_answer": explanation if explanation else " ".join(comparison_keywords[:5]),
            "min_keywords": max(3, len(comparison_keywords) // 2),
            "explanation": explanation if explanation else f"Comparația ar trebui să evidențieze diferențele și similaritățile.",
            "theory_reference": {
                "definition": theory.get("definition", ""),
                "key_concepts": key_concepts
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

