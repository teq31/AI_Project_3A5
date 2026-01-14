"""
Modul pentru evaluarea răspunsurilor la întrebările de teorie.
Folosește procesare de limbaj natural (NLP) pentru înțelegere semantică.
"""

import re
from typing import Dict, Any, List, Optional

# Import NLP utils (cu fallback dacă nu sunt disponibile)
try:
    from app.nlp_utils import (
        semantic_similarity, find_best_match, extract_key_concepts,
        understand_answer_intent, compare_answers_natural, normalize_text,
        SEMANTIC_SIMILARITY_AVAILABLE, NLP_AVAILABLE
    )
    NLP_ENABLED = True
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"NLP enabled: SEMANTIC_SIMILARITY_AVAILABLE={SEMANTIC_SIMILARITY_AVAILABLE}, NLP_AVAILABLE={NLP_AVAILABLE}")
except ImportError as e:
    NLP_ENABLED = False
    SEMANTIC_SIMILARITY_AVAILABLE = False
    NLP_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"NLP not available: {e}")
    # Funcții fallback simple
    def semantic_similarity(text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        text1, text2 = text1.lower().strip(), text2.lower().strip()
        if text1 == text2:
            return 1.0
        if text1 in text2 or text2 in text1:
            return 0.8
        return 0.0
    
    def find_best_match(user_answer: str, correct_answers: List[str], threshold: float = 0.7):
        if not user_answer or not correct_answers:
            return None, 0.0
        user_lower = user_answer.lower()
        for correct in correct_answers:
            if correct.lower() in user_lower or user_lower in correct.lower():
                return correct, 0.8
        return None, 0.0
    
    def extract_key_concepts(text: str, keywords: List[str]):
        found = [kw for kw in keywords if kw.lower() in text.lower()]
        return {"found_keywords": found, "scores": {}, "total_score": len(found) / len(keywords) if keywords else 0.0}
    
    def understand_answer_intent(answer: str):
        return {"intent": "answer", "confidence": 0.5, "has_answer": len(answer.strip()) > 2, "sentiment": "neutral"}
    
    def compare_answers_natural(user_answer: str, correct_answer: str, threshold: float = 0.75):
        sim = semantic_similarity(user_answer, correct_answer)
        return {"is_correct": sim >= threshold, "similarity": sim, "feedback": ""}
    
    def normalize_text(text: str) -> str:
        return text.strip() if text else ""


def _detect_uncertainty_or_unknown(answer: str) -> Optional[Dict[str, Any]]:
    """
    Detectează dacă răspunsul indică incertitudine sau lipsă de cunoștințe.
    
    Returns:
        None dacă răspunsul este normal, sau Dict cu "confidence" (0-1) și "type" 
        ("unknown", "uncertain", "partial_knowledge")
    """
    answer_lower = answer.lower().strip()
    
    # Pattern-uri pentru "nu știu" / "don't know" - EXTINSE
    unknown_patterns = [
        r'\bnu\s+știu\b', r'\bnu\s+stiu\b', r'\bdont\s+know\b', r'\bdon\'t\s+know\b',
        r'\bnu\s+cunosc\b', r'\bnu\s+știu\s+răspunsul\b', r'\bnu\s+stiu\s+raspunsul\b',
        r'\bnu\s+știu\s+ce\b', r'\bnu\s+stiu\s+ce\b', r'\bno\s+idea\b', r'\bno\s+clue\b',
        r'\bnu\s+am\s+idee\b', r'\bnu\s+știu\s+nimic\b', r'\bnu\s+stiu\s+nimic\b',
        r'\bnu\s+știu\s+exact\b', r'\bnu\s+stiu\s+exact\b', r'\bnu\s+știu\s+precis\b',
        r'\bnu\s+știu\s+deloc\b', r'\bnu\s+stiu\s+deloc\b', r'\bhabar\s+nu\s+am\b',
        r'\bnu\s+știu\s+răspunsul\b', r'\bnu\s+stiu\s+raspunsul\b',
        r'\bnu\s+știu\s+raspunsul\b', r'\bnu\s+stiu\s+raspunsul\b',
        r'\bnu\s+știu\s+sa\s+raspund\b', r'\bnu\s+stiu\s+sa\s+raspund\b',
        r'\bnu\s+știu\s+cum\s+sa\s+raspund\b', r'\bnu\s+stiu\s+cum\s+sa\s+raspund\b',
        r'\bnu\s+știu\s+nimic\s+despre\b', r'\bnu\s+stiu\s+nimic\s+despre\b',
        r'\bnu\s+știu\s+absolut\s+nimic\b', r'\bnu\s+stiu\s+absolut\s+nimic\b',
        r'\bnu\s+am\s+nici\s+o\s+idee\b', r'\bnu\s+am\s+nici\s+o\s+idee\b',
        r'\bnu\s+știu\s+deloc\s+ce\b', r'\bnu\s+stiu\s+deloc\s+ce\b',
        r'\bnu\s+știu\s+nimic\s+despre\s+asta\b', r'\bnu\s+stiu\s+nimic\s+despre\s+asta\b',
        r'\bno\s+idea\b', r'\bno\s+clue\b', r'\bi\s+dont\s+know\b', r'\bi\s+don\'t\s+know\b',
        r'\bhave\s+no\s+idea\b', r'\bclueless\b', r'\bno\s+knowledge\b',
        r'\bnu\s+știu\s+raspunsul\s+la\b', r'\bnu\s+stiu\s+raspunsul\s+la\b',
        r'\bnu\s+știu\s+ce\s+sa\s+zic\b', r'\bnu\s+stiu\s+ce\s+sa\s+zic\b',
        r'\bnu\s+știu\s+ce\s+sa\s+scriu\b', r'\bnu\s+stiu\s+ce\s+sa\s+scriu\b'
    ]
    
    # Pattern-uri pentru incertitudine
    uncertain_patterns = [
        r'\bnu\s+sunt\s+sigur\b', r'\bnu\s+sunt\s+sigura\b', r'\bnot\s+sure\b',
        r'\bnu\s+sunt\s+prea\s+sigur\b', r'\bnu\s+sunt\s+prea\s+sigura\b',
        r'\bpoate\b', r'\bpossibly\b', r'\bmaybe\b', r'\bperhaps\b',
        r'\bprobabil\b', r'\bprobably\b', r'\bcred\s+ca\b', r'\bcrez\s+ca\b',
        r'\bpresupun\b', r'\bpresupune\b', r'\bassume\b', r'\bguess\b',
        r'\bnu\s+sunt\s+convins\b', r'\bnu\s+sunt\s+convinsa\b', r'\bnot\s+convinced\b',
        r'\bparțial\b', r'\bpartial\b', r'\bparțial\s+știu\b', r'\bpartial\s+know\b'
    ]
    
    # Pattern-uri pentru cunoștințe parțiale
    partial_patterns = [
        r'\bștiu\s+doar\b', r'\bstiu\s+doar\b', r'\bknow\s+only\b',
        r'\bștiu\s+parțial\b', r'\bstiu\s+partial\b', r'\bpartial\s+knowledge\b',
        r'\bnu\s+știu\s+tot\b', r'\bnu\s+stiu\s+tot\b', r'\bdon\'t\s+know\s+everything\b',
        r'\bam\s+o\s+idee\b', r'\bhave\s+an\s+idea\b', r'\bștiu\s+ceva\b', r'\bstiu\s+ceva\b'
    ]
    
    # Verifică "nu știu" - cel mai clar indicator
    for pattern in unknown_patterns:
        if re.search(pattern, answer_lower, re.IGNORECASE):
            return {
                "confidence": 0.0,
                "type": "unknown",
                "message": "Ai indicat că nu știi răspunsul."
            }
    
    # Verifică incertitudine
    for pattern in uncertain_patterns:
        if re.search(pattern, answer_lower, re.IGNORECASE):
            return {
                "confidence": 0.3,
                "type": "uncertain",
                "message": "Ai indicat incertitudine în răspuns."
            }
    
    # Verifică cunoștințe parțiale
    for pattern in partial_patterns:
        if re.search(pattern, answer_lower, re.IGNORECASE):
            return {
                "confidence": 0.5,
                "type": "partial_knowledge",
                "message": "Ai indicat că ai cunoștințe parțiale."
            }
    
    return None


def _understand_answer_semantics(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Înțelege semantica răspunsului utilizatorului pentru a oferi evaluare mai precisă.
    
    Returns:
        Dict cu "intent" (ce înțelege sistemul), "confidence" (încredere 0-1),
        "has_content" (dacă răspunsul are conținut real), "keywords_found" (cuvinte cheie găsite)
    """
    answer_lower = answer.lower().strip()
    
    # Verifică dacă răspunsul este prea scurt sau gol
    if len(answer.strip()) < 3:
        return {
            "intent": "too_short",
            "confidence": 0.0,
            "has_content": False,
            "keywords_found": []
        }
    
    # Verifică dacă răspunsul conține doar punctuație sau caractere speciale
    if not re.search(r'[a-zA-ZăâîșțĂÂÎȘȚ]', answer):
        return {
            "intent": "no_text",
            "confidence": 0.0,
            "has_content": False,
            "keywords_found": []
        }
    
    # Extrage cuvinte cheie potențiale din întrebare
    question_text = question.get("question_text", "").lower()
    correct_keywords = [kw.lower() for kw in question.get("correct_keywords", [])]
    correct_answer = question.get("correct_answer", "").lower()
    
    # Caută cuvinte cheie în răspuns
    keywords_found = []
    for keyword in correct_keywords:
        if keyword in answer_lower:
            keywords_found.append(keyword)
    
    # Verifică dacă răspunsul conține răspunsul corect (parțial sau complet)
    has_correct_answer = False
    if correct_answer:
        correct_answer_lower = correct_answer.lower()
        # Verificare exactă sau substring
        if correct_answer_lower in answer_lower or answer_lower in correct_answer_lower:
            has_correct_answer = True
        # Verifică și cuvinte din răspunsul corect (pentru răspunsuri lungi)
        correct_words = [w for w in correct_answer_lower.split() if len(w) > 3]
        if correct_words:
            matching_words = sum(1 for word in correct_words if word in answer_lower)
            if matching_words >= len(correct_words) * 0.6:
                has_correct_answer = True
        # Verifică și pentru răspunsuri care conțin majoritatea cuvintelor cheie
        if not has_correct_answer and correct_words:
            matching_words = sum(1 for word in correct_words if word in answer_lower)
            if matching_words >= max(2, len(correct_words) * 0.5):  # Cel puțin 50% sau minim 2 cuvinte
                has_correct_answer = True
    
    # Determină intenția
    if has_correct_answer and len(keywords_found) >= 2:
        intent = "correct_attempt"
        confidence = 0.8
    elif len(keywords_found) > 0:
        intent = "partial_attempt"
        confidence = 0.5
    elif len(answer_lower.split()) >= 5:  # Răspuns lung - probabil o încercare serioasă
        intent = "detailed_attempt"
        confidence = 0.6
    else:
        intent = "minimal_attempt"
        confidence = 0.3
    
    return {
        "intent": intent,
        "confidence": confidence,
        "has_content": True,
        "keywords_found": keywords_found,
        "has_correct_answer": has_correct_answer
    }


def _detect_justification_required(question: Dict[str, Any]) -> bool:
    """
    Detectează dacă întrebarea cere explicit justificare.
    
    Returns:
        True dacă întrebarea cere justificare, False altfel
    """
    question_text = question.get("question_text", "").lower()
    theory_type = question.get("theory_type", "")
    
    # Verifică tipul de întrebare
    if theory_type == "justification":
        return True
    
    # Verifică dacă întrebarea conține cuvinte cheie care indică nevoia de justificare
    # MAI STRICTĂ: doar cuvinte care indică explicit justificare, nu doar "explică"
    justification_indicators = [
        r'\bjustifică\b', r'\bjustifica\b', r'\bjustify\b',
        r'\bși\s+explică\b', r'\bsi\s+explica\b', r'\band\s+explain\b',  # "și explică" = cere justificare
        r'\bși\s+justifică\b', r'\bsi\s+justifica\b', r'\band\s+justify\b',  # "și justifică"
        r'\bexplică\s+de\s+ce\b', r'\bexplica\s+de\s+ce\b', r'\bexplain\s+why\b',  # "explică de ce"
        r'\bde\s+ce\b.*\bexplică\b', r'\bwhy\b.*\bexplain\b',  # "de ce ... explică"
        r'\bmotiv\b.*\bexplică\b', r'\breason\b.*\bexplain\b',  # "motiv ... explică"
        r'\brațiune\b', r'\bratiune\b', r'\brationale\b',  # "rațiune" = justificare explicită
        r'\bargumentează\b', r'\bargumenteaza\b', r'\bargue\b',  # "argumentează"
        r'\bdemonstrează\b', r'\bdemonstreaza\b', r'\bdemonstrate\b',  # "demonstrează"
        r'\bprezintă\s+rațiunea\b', r'\bprezinta\s+ratiunea\b',  # "prezintă rațiunea"
        r'\bprezintă\s+motivul\b', r'\bprezinta\s+motivul\b'  # "prezintă motivul"
    ]
    
    for pattern in justification_indicators:
        if re.search(pattern, question_text, re.IGNORECASE):
            return True
    
    return False


def _parse_answer_with_justification(answer: str) -> Dict[str, Any]:
    """
    Parsează răspunsul în două părți: răspunsul principal și justificarea.
    
    Returns:
        Dict cu "main_answer" (răspunsul principal), "justification" (justificarea),
        "has_justification" (dacă există justificare), "separator" (separatorul găsit)
    """
    answer_original = answer.strip()
    answer_lower = answer_original.lower()
    
    # Separatori comuni între răspuns și justificare
    separators = [
        r'\bdeoarece\b', r'\bpentru\s+ca\b', r'\bpentru\s+că\b', r'\bbecause\b',
        r'\bmotivul\s+este\b', r'\bmotivul\s+este\b', r'\bthe\s+reason\s+is\b',
        r'\bexplicația\s+este\b', r'\bexplicatia\s+este\b', r'\bthe\s+explanation\s+is\b',
        r'\bjustificarea\s+este\b', r'\bjustificarea\s+este\b', r'\bthe\s+justification\s+is\b',
        r'\bpentru\s+că\b', r'\bpentru\s+ca\b', r'\bsince\b',
        r'\bîntrucât\b', r'\bintrucat\b', r'\bas\b',
        r'\bmotiv\b', r'\bmotivul\b', r'\breason\b',
        r'\bexplicație\b', r'\bexplicatie\b', r'\bexplanation\b',
        r'\bjustificare\b', r'\bjustification\b',
        r'\b:\s*',  # Două puncte
        r'\b-\s*',  # Linie
        r'\b,\s*și\s+', r'\b,\s+si\s+', r'\b,\s+and\s+',  # Virgulă + și
    ]
    
    main_answer = answer_original
    justification = ""
    separator_found = None
    split_position = -1
    
    # Caută primul separator care apare
    for separator in separators:
        match = re.search(separator, answer_lower, re.IGNORECASE)
        if match:
            split_position = match.start()
            separator_found = match.group(0)
            break
    
    # Dacă s-a găsit un separator, împarte răspunsul
    if split_position > 0:
        main_answer = answer_original[:split_position].strip()
        justification = answer_original[split_position:].strip()
        
        # Elimină separatorul din justificare dacă este la început
        if separator_found:
            justification = re.sub(r'^' + re.escape(separator_found), '', justification, flags=re.IGNORECASE).strip()
            justification = re.sub(r'^[:\-,\s]+', '', justification).strip()  # Elimină punctuație rămasă
    
    # Dacă nu s-a găsit separator explicit, încearcă să detecteze structura
    if not justification and len(answer_original.split()) > 5:
        # Dacă răspunsul este lung, probabil conține și justificare
        words = answer_original.split()
        
        # Verifică dacă primele cuvinte sunt răspunsuri scurte (da/nu/true/false/etc.)
        first_words = ' '.join(words[:3]).lower()
        short_answers = ['da', 'nu', 'yes', 'no', 'true', 'false', 'adevărat', 'adevarat', 'fals', 
                       'corect', 'greșit', 'gresit', 'correct', 'wrong', 'incorrect',
                       'este', 'is', 'nu este', 'nu e', 'is not', 'isn\'t']
        
        # Verifică dacă primele cuvinte conțin un răspuns scurt
        has_short_answer = any(short in first_words for short in short_answers)
        
        # Verifică și pentru răspunsuri numerice (ex: "1", "2", "opțiunea 1")
        has_numeric_answer = re.search(r'^\d+', words[0]) or any(re.search(r'\b\d+\b', w) for w in words[:2])
        
        if has_short_answer or has_numeric_answer:
            # Primele 1-3 cuvinte sunt probabil răspunsul principal
            # Găsește unde începe justificarea (după primul răspuns scurt)
            split_idx = 1
            for i, word in enumerate(words[:5]):
                word_lower = word.lower().strip('.,!?;:')
                if word_lower in short_answers or re.search(r'^\d+$', word):
                    split_idx = i + 1
                    break
            
            if split_idx < len(words):
                main_answer = ' '.join(words[:split_idx])
                justification = ' '.join(words[split_idx:])
                separator_found = "implicit"
        
        # Dacă nu s-a găsit răspuns scurt la început, verifică dacă există o propoziție scurtă urmată de explicație
        elif len(words) > 8:
            # Primele 3-5 cuvinte pot fi răspunsul principal, restul justificarea
            # Caută prima propoziție (terminată cu punct, semn de întrebare, sau virgulă)
            for i, word in enumerate(words):
                if i > 2 and i < len(words) - 3:  # Nu la început și nu la sfârșit
                    if word.endswith('.') or word.endswith('?') or word.endswith('!'):
                        # Probabil sfârșitul primei propoziții
                        main_answer = ' '.join(words[:i+1])
                        justification = ' '.join(words[i+1:])
                        separator_found = "sentence_boundary"
                        break
    
    has_justification = len(justification.strip()) > 10  # Minim 10 caractere pentru justificare
    
    return {
        "main_answer": main_answer,
        "justification": justification,
        "has_justification": has_justification,
        "separator": separator_found
    }


def grade_answer(answer: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluează răspunsul la o întrebare de teorie.
    Include detectare inteligentă pentru răspunsuri "nu știu" și înțelegere semantică.
    
    Args:
        answer: Răspunsul utilizatorului
        payload: Payload-ul întrebării (conține tipul și răspunsul corect)
    
    Returns:
        Dict cu "score" (0-100) și "feedback"
    """
    # Verifică mai întâi dacă utilizatorul indică lipsă de cunoștințe
    uncertainty = _detect_uncertainty_or_unknown(answer)
    if uncertainty:
        if uncertainty["type"] == "unknown":
            # Dacă spune clar "nu știu", oferă feedback educativ
            question = payload.get("question") or payload
            correct_answer = question.get("correct_answer", "")
            explanation = question.get("explanation", "")
            
            # Construiește feedback educativ și încurajator
            feedback_parts = [
                uncertainty['message'],
                "Nu este o problemă - învățarea este un proces!",
            ]
            
            if correct_answer:
                feedback_parts.append(f"Răspunsul corect este: {correct_answer}.")
            elif question.get("correct_keywords"):
                keywords = question.get("correct_keywords", [])[:3]
                feedback_parts.append(f"Concepte importante de menționat: {', '.join(keywords)}.")
            
            if explanation:
                feedback_parts.append(explanation)
            else:
                feedback_parts.append("Te încurajez să revii la acest concept și să încerci din nou!")
            
            return {
                "score": 0,
                "feedback": " ".join(feedback_parts)
            }
        elif uncertainty["type"] == "uncertain":
            # Pentru incertitudine, analizează dacă există și conținut util în răspuns
            question = payload.get("question") or payload
            semantics = _understand_answer_semantics(answer, question)
            
            if semantics["has_content"] and semantics["keywords_found"]:
                # Dacă are conținut util chiar dacă e incert, oferă scor parțial
                score = min(30, len(semantics["keywords_found"]) * 10)
                explanation = question.get("explanation", "")
                return {
                    "score": score,
                    "feedback": f"{uncertainty['message']} Totuși, ai menționat câteva concepte relevante ({', '.join(semantics['keywords_found'][:3])}). Te încurajez să fii mai sigur în răspunsuri! {explanation if explanation else ''}"
                }
            else:
                explanation = question.get("explanation", "")
                return {
                    "score": 10,  # Scor mic pentru încercare
                    "feedback": f"{uncertainty['message']} Înțeleg că nu ești sigur. Te încurajez să încerci să răspunzi - chiar dacă nu ești sigur, procesul de gândire este important! {explanation if explanation else ''}"
                }
        elif uncertainty["type"] == "partial_knowledge":
            # Pentru cunoștințe parțiale, continuă evaluarea normală dar cu context
            question = payload.get("question") or payload
            semantics = _understand_answer_semantics(answer, question)
            
            # Continuă cu evaluarea normală, dar ajustează feedback-ul
            # (va fi procesat în funcțiile specifice de grading)
            pass  # Continuă mai departe pentru evaluare normală
    
    question = payload.get("question") or payload  # Compatibilitate
    
    # Verifică dacă întrebarea cere justificare
    requires_justification = _detect_justification_required(question)
    
    if requires_justification:
        # Parsează răspunsul în răspuns principal + justificare
        parsed = _parse_answer_with_justification(answer)
        
        # Evaluează răspunsul principal
        theory_type = question.get("theory_type", "short_answer")
        question_text = question.get("question_text", "").lower()
        
        # Determină tipul de răspuns principal bazat pe întrebare
        # Verifică dacă este true/false
        is_true_false = any(word in question_text for word in ['adevărat', 'adevarat', 'fals', 'true', 'false', 
                                                               'corect', 'greșit', 'gresit', 'correct', 'wrong'])
        
        # Verifică dacă este multiple choice
        is_multiple_choice = question.get("options") is not None and len(question.get("options", [])) > 0
        
        # Creează o întrebare temporară pentru evaluarea răspunsului principal
        main_question = question.copy()
        
        # Evaluează răspunsul principal
        if is_true_false:
            main_result = _grade_true_false(parsed["main_answer"], main_question)
        elif is_multiple_choice:
            main_result = _grade_multiple_choice(parsed["main_answer"], main_question)
        else:
            # Pentru alte tipuri, folosește short_answer
            main_result = _grade_short_answer(parsed["main_answer"], main_question)
        
        # Evaluează justificarea
        if parsed["has_justification"]:
            justification_result = _grade_justification(parsed["justification"], question)
        else:
            justification_result = {
                "score": 0,
                "feedback": "Lipsește justificarea. Te rog să explici de ce ai ales acest răspuns."
            }
        
        # Combină scorurile (50% răspuns principal + 50% justificare)
        main_score = main_result["score"]
        justification_score = justification_result["score"]
        combined_score = int((main_score * 0.5) + (justification_score * 0.5))
        
        # Construiește feedback combinat
        feedback_parts = []
        
        # Feedback pentru răspunsul principal
        if main_score == 100:
            feedback_parts.append(f"✓ Răspunsul principal: CORECT ({main_score}%)")
        elif main_score > 0:
            feedback_parts.append(f"⚠ Răspunsul principal: PARȚIAL ({main_score}%)")
        else:
            feedback_parts.append(f"✗ Răspunsul principal: INCORECT ({main_score}%)")
        
        # Feedback pentru justificare
        if not parsed["has_justification"]:
            feedback_parts.append(f"\n✗ Justificare: LIPSEȘTE (0%)")
            feedback_parts.append("Te rog să explici de ce ai ales acest răspuns.")
        elif justification_score == 100:
            feedback_parts.append(f"\n✓ Justificare: COMPLETĂ ȘI CORECTĂ ({justification_score}%)")
        elif justification_score > 0:
            feedback_parts.append(f"\n⚠ Justificare: PARȚIALĂ ({justification_score}%)")
        else:
            feedback_parts.append(f"\n✗ Justificare: INCORECTĂ SAU INSUFICIENTĂ ({justification_score}%)")
        
        # Adaugă feedback-urile detaliate
        if main_result.get("feedback"):
            feedback_parts.append(f"\n\n📝 Detalii răspuns principal: {main_result['feedback']}")
        if justification_result.get("feedback") and parsed["has_justification"]:
            feedback_parts.append(f"\n📝 Detalii justificare: {justification_result['feedback']}")
        
        # Adaugă sugestii dacă justificarea lipsește
        if not parsed["has_justification"]:
            feedback_parts.append("\n💡 Sfat: Când întrebarea cere justificare, te rog să incluzi:")
            feedback_parts.append("- Răspunsul principal (da/nu, sau răspunsul scurt)")
            feedback_parts.append("- O explicație care să justifice de ce ai ales acest răspuns")
            feedback_parts.append("- Folosește cuvinte precum 'deoarece', 'pentru că', 'motivul este', etc.")
        
        # Combină similaritățile din răspunsul principal și justificare
        main_similarity = main_result.get("similarity", 0.0)
        justification_similarity = justification_result.get("similarity", 0.0) if parsed["has_justification"] else 0.0
        combined_similarity = (main_similarity * 0.5) + (justification_similarity * 0.5)
        
        # Determină metoda folosită (prioritizează NLP dacă este disponibil)
        main_method = main_result.get("method", "Fallback")
        justification_method = justification_result.get("method", "Fallback") if parsed["has_justification"] else "Fallback"
        # Dacă ambele folosesc NLP, arată NLP, altfel arată metoda principală
        final_method = main_method if "NLP" in main_method or "NLP" in justification_method else main_method
        
        return {
            "score": combined_score,
            "feedback": " ".join(feedback_parts),
            "main_score": main_score,
            "justification_score": justification_score,
            "has_justification": parsed["has_justification"],
            "main_answer": parsed["main_answer"],
            "justification": parsed["justification"],
            "similarity": combined_similarity,
            "method": final_method,
            "method": final_method
        }
    
    # Dacă nu cere justificare, continuă cu evaluarea normală
    theory_type = question.get("theory_type", "multiple_choice")
    
    if theory_type == "multiple_choice":
        return _grade_multiple_choice(answer, question)
    elif theory_type == "true_false":
        return _grade_true_false(answer, question)
    elif theory_type == "fill_blank":
        return _grade_fill_blank(answer, question)
    elif theory_type == "short_answer":
        return _grade_short_answer(answer, question)
    elif theory_type == "justification":
        return _grade_justification(answer, question)
    elif theory_type == "example":
        return _grade_example(answer, question)
    elif theory_type == "comparison":
        return _grade_comparison(answer, question)
    elif theory_type == "definition":
        return _grade_definition(answer, question)
    elif theory_type == "calculation":
        return _grade_calculation(answer, question)
    elif theory_type == "matrix_analysis":
        return _grade_matrix_analysis(answer, question)
    else:
        return {
            "score": 0,
            "feedback": f"Tip de întrebare necunoscut: {theory_type}"
        }


def _grade_multiple_choice(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare multiple choice - flexibil cu NLP și înțelegere semantică"""
    answer = answer.strip()
    correct_answer = question.get("correct_answer", "")
    correct_index = question.get("correct_index", -1)
    options = question.get("options", [])
    
    # Analiză NLP pentru intenție
    intent = understand_answer_intent(answer) if NLP_ENABLED else None
    
    # Analiză semantică
    semantics = _understand_answer_semantics(answer, question)
    
    answer_lower = answer.lower().strip()
    correct_lower = correct_answer.lower().strip()
    
    # 1. PRIORITATE: Verifică dacă răspunsul conține numărul opțiunii (1-based)
    # Aceasta este mai rapidă și mai precisă pentru răspunsuri numerice ("1", "2", etc.)
    # Pattern: "1", "2", "opțiunea 1", "varianta 2", "raspunsul este 3", etc.
    num_pattern = re.search(r'\b([1-9])\b', answer)
    if num_pattern:
        try:
            answer_num = int(num_pattern.group(1))
            if 1 <= answer_num <= len(options):
                user_index = answer_num - 1
                method = "Numeric Match"
                if user_index == correct_index:
                    return {
                        "score": 100,
                        "feedback": f"Corect! Răspunsul este: {correct_answer}. {question.get('explanation', '')}",
                        "similarity": 1.0,
                        "method": method
                    }
                else:
                    return {
                        "score": 0,
                        "feedback": f"Greșit. Ai ales: {options[user_index]}. Răspunsul corect este: {correct_answer}. {question.get('explanation', '')}",
                        "similarity": 0.0,
                        "method": method
                    }
        except (ValueError, IndexError):
            pass
    
    # 2. Verificare exactă a textului opțiunii corecte
    method = "Exact Match"
    if answer_lower == correct_lower:
        return {
            "score": 100,
            "feedback": f"Corect! {question.get('explanation', '')}",
            "similarity": 1.0,
            "method": method
        }
    
    # 3. Verificare dacă răspunsul conține textul complet al opțiunii corecte
    # Ex: "Raspunsul este O(b^(d/2))" sau "Este O(b^(d/2))"
    if correct_lower in answer_lower:
        # Verifică dacă este o potrivire bună (nu doar o parte mică)
        method = "Substring Match"
        if len(correct_lower) >= 3:  # Minim 3 caractere pentru a fi relevant
            return {
                "score": 100,
                "feedback": f"Corect! {question.get('explanation', '')}",
                "similarity": 0.9,
                "method": method
            }
    
    # 4. Verificare parțială - dacă răspunsul conține o parte semnificativă
    if len(correct_lower) > 5:  # Pentru răspunsuri lungi
        # Verifică dacă majoritatea cuvintelor cheie sunt prezente
        correct_words = [w for w in correct_lower.split() if len(w) > 2]
        answer_words = set(answer_lower.split())
        matching_words = sum(1 for word in correct_words if word in answer_words)
        
        method = "Partial Match"
        if matching_words >= len(correct_words) * 0.7:  # 70% din cuvinte
            return {
                "score": 85,
                "feedback": f"Parțial corect. Răspunsul complet corect este: {correct_answer}. {question.get('explanation', '')}",
                "similarity": 0.7,
                "method": method
            }
    
    # 5. Verifică dacă răspunsul este una dintre opțiunile greșite
    for i, option in enumerate(options):
        option_lower = option.lower().strip()
        if answer_lower == option_lower or option_lower in answer_lower:
            method = "Option Match"
            if i == correct_index:
                return {
                    "score": 100,
                    "feedback": f"Corect! {question.get('explanation', '')}",
                    "similarity": 1.0,
                    "method": method
                }
            else:
                return {
                    "score": 0,
                    "feedback": f"Greșit. Ai ales: {option}. Răspunsul corect este: {correct_answer}. {question.get('explanation', '')}",
                    "similarity": 0.0,
                    "method": method
                }
    
    # 6. Verificare finală - dacă răspunsul conține o parte din opțiunea corectă
    if answer_lower in correct_lower and len(answer_lower) >= 3:
        return {
            "score": 75,
            "feedback": f"Parțial corect. Răspunsul complet corect este: {correct_answer}. {question.get('explanation', '')}"
        }
    
    # Dacă nu s-a găsit nimic, verifică dacă răspunsul are conținut util
    if semantics["has_content"] and semantics["keywords_found"]:
        return {
            "score": 20,  # Scor mic pentru încercare cu conținut relevant
            "feedback": f"Răspunsul tău conține câteva concepte relevante ({', '.join(semantics['keywords_found'][:2])}), dar nu corespunde cu niciuna dintre opțiunile disponibile. Răspunsul corect este: {correct_answer}. {question.get('explanation', '')}"
        }
    
    return {
        "score": 0,
        "feedback": f"Răspuns invalid sau incorect. Răspunsul corect este: {correct_answer}. {question.get('explanation', '')}"
    }


def _grade_true_false(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare true/false - foarte flexibil cu NLP"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_answer = question.get("correct_answer", False)
    correct_answer_str = question.get("correct_answer_str", "")  # Pentru NLP
    
    # PRIORITATE 1: Folosește NLP dacă este disponibil și există correct_answer_str
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Pattern Match")
    if NLP_ENABLED and correct_answer_str and correct_answer_str.strip():
        try:
            similarity = semantic_similarity(answer_original, correct_answer_str)
            import logging
            logging.getLogger(__name__).info(f"NLP semantic similarity for true/false: {similarity:.2f}")
            
            # Dacă similaritatea este mare, verifică dacă răspunsul indică același boolean
            if similarity >= 0.60:
                # Încearcă să extragă boolean-ul din răspuns
                true_patterns = [r'\btrue\b', r'\badevărat\b', r'\badevarat\b', r'\bda\b', r'\byes\b', r'\b1\b', r'\bcorect\b']
                false_patterns = [r'\bfalse\b', r'\bfals\b', r'\bnu\b', r'\bno\b', r'\b0\b', r'\bgreșit\b', r'\bgresit\b']
                
                user_bool = None
                for pattern in true_patterns:
                    if re.search(pattern, answer_original, re.IGNORECASE):
                        user_bool = True
                        break
                if user_bool is None:
                    for pattern in false_patterns:
                        if re.search(pattern, answer_original, re.IGNORECASE):
                            user_bool = False
                            break
                
                if user_bool is not None and user_bool == correct_answer:
                    score = min(100, int(80 + similarity * 20))  # 80-100% bazat pe similaritate
                    return {
                        "score": score,
                        "feedback": f"Corect! (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                        "similarity": similarity,
                        "method": method
                    }
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error in NLP for true/false: {e}")
            # Continuă cu pattern matching
    
    # Lista extinsă de variante pentru True
    true_patterns = [
        r'\btrue\b', r'\badevărat\b', r'\badevarat\b', r'\bda\b', r'\byes\b',
        r'\b1\b', r'\bcorect\b', r'\bcorrect\b', r'\bvalid\b', r'\bvalidă\b',
        r'\beste\s+adevărat\b', r'\beste\s+adevarat\b', r'\beste\s+true\b',
        r'\beste\s+corect\b', r'\beste\s+correct\b', r'\beste\s+da\b',
        r'\brasunsul\s+este\s+adevărat\b', r'\brasunsul\s+este\s+adevarat\b',
        r'\brasunsul\s+este\s+true\b', r'\brasunsul\s+este\s+corect\b',
        r'\bcorrect\s+este\s+adevărat\b', r'\bcorrect\s+este\s+true\b',
        r'\bafirmația\s+este\s+adevărată\b', r'\bafirmatia\s+este\s+adevarata\b'
    ]
    
    # Lista extinsă de variante pentru False
    false_patterns = [
        r'\bfalse\b', r'\bfals\b', r'\bnu\b', r'\bno\b', r'\b0\b',
        r'\bgreșit\b', r'\bgresit\b', r'\bincorrect\b', r'\bwrong\b',
        r'\binvalid\b', r'\binvalidă\b', r'\binvalida\b',
        r'\beste\s+fals\b', r'\beste\s+false\b', r'\beste\s+greșit\b',
        r'\beste\s+gresit\b', r'\beste\s+incorrect\b', r'\beste\s+wrong\b',
        r'\beste\s+nu\b', r'\beste\s+no\b',
        r'\brasunsul\s+este\s+fals\b', r'\brasunsul\s+este\s+false\b',
        r'\brasunsul\s+este\s+greșit\b', r'\brasunsul\s+este\s+gresit\b',
        r'\brasunsul\s+este\s+incorrect\b', r'\brasunsul\s+este\s+wrong\b',
        r'\brasunsul\s+este\s+nu\b', r'\brasunsul\s+este\s+no\b',
        r'\bcorrect\s+este\s+fals\b', r'\bcorrect\s+este\s+false\b',
        r'\bafirmația\s+este\s+falsă\b', r'\bafirmatia\s+este\s+falsa\b',
        r'\bafirmația\s+este\s+greșită\b', r'\bafirmatia\s+este\s+gresita\b'
    ]
    
    # Verifică pattern-urile pentru True
    user_answer_bool = None
    for pattern in true_patterns:
        if re.search(pattern, answer, re.IGNORECASE):
            user_answer_bool = True
            break
    
    # Dacă nu s-a găsit True, verifică False
    if user_answer_bool is None:
        for pattern in false_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                user_answer_bool = False
                break
    
    # Dacă încă nu s-a găsit, verifică variante simple (fără regex)
    if user_answer_bool is None:
        simple_true = ["true", "adevărat", "adevarat", "da", "yes", "1", "corect", "correct", "valid", "validă"]
        simple_false = ["false", "fals", "nu", "no", "0", "greșit", "gresit", "incorrect", "wrong", "invalid", "invalidă", "invalida"]
        
        if any(word in answer for word in simple_true):
            user_answer_bool = True
        elif any(word in answer for word in simple_false):
            user_answer_bool = False
    
    method = "Pattern Match"
    if user_answer_bool is None:
        return {
            "score": 0,
            "feedback": f"Răspuns invalid. Te rog să răspunzi cu 'Adevărat'/'True' sau 'Fals'/'False'. Răspunsul corect este: {'Adevărat' if correct_answer else 'Fals'}. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }
    
    if user_answer_bool == correct_answer:
        return {
            "score": 100,
            "feedback": f"Corect! {question.get('explanation', '')}",
            "similarity": 1.0,
            "method": method
        }
    else:
        return {
            "score": 0,
            "feedback": f"Greșit. Răspunsul corect este: {'Adevărat' if correct_answer else 'Fals'}. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }


def _grade_fill_blank(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare fill-in-the-blank - flexibil cu NLP"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_answers_list = question.get("correct_answers", [])
    correct_answer = question.get("correct_answer", "")  # Pentru NLP
    case_sensitive = question.get("case_sensitive", False)
    
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Exact Match")
    if not correct_answers_list:
        return {
            "score": 0,
            "feedback": "Eroare: Nu există răspunsuri corecte definite pentru această întrebare.",
            "similarity": 0.0,
            "method": method
        }
    
    # PRIORITATE 1: Folosește NLP dacă este disponibil și există correct_answer
    if NLP_ENABLED and correct_answer and correct_answer.strip():
        try:
            similarity = semantic_similarity(answer_original, correct_answer)
            import logging
            logging.getLogger(__name__).info(f"NLP semantic similarity for fill_blank: {similarity:.2f}")
            
            # Dacă similaritatea este suficient de mare, acceptă răspunsul
            if similarity >= 0.70:
                score = min(100, int(70 + similarity * 30))  # 70-100% bazat pe similaritate
                return {
                    "score": score,
                    "feedback": f"Corect! (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": method
                }
            elif similarity >= 0.50:
                score = int(50 + (similarity - 0.50) * 100)  # 50-70%
                return {
                    "score": score,
                    "feedback": f"Răspuns parțial corect (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": method
                }
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error in NLP for fill_blank: {e}")
            # Continuă cu verificarea exactă
    
    answer_normalized = answer if case_sensitive else answer.lower()
    
    # Verifică fiecare variantă de răspuns corect
    for correct_variant in correct_answers_list:
        if isinstance(correct_variant, list):
            # Multiple blanks - verifică dacă răspunsul conține toate valorile
            variant_normalized = [v if case_sensitive else v.lower() for v in correct_variant]
            
            # Verificare exactă - toate valorile trebuie să fie prezente
            if all(val in answer_normalized for val in variant_normalized):
                return {
                    "score": 100,
                    "feedback": f"Corect! {question.get('explanation', '')}",
                    "similarity": 1.0,
                    "method": method
                }
            
            # Verificare flexibilă - valorile pot fi în orice ordine și pot avea text în jur
            # Ex: "alpha este -∞ și beta este +∞" sau "-∞, +∞"
            all_found = True
            for val in variant_normalized:
                # Verifică dacă valoarea este prezentă (ca substring sau ca cuvânt complet)
                if val not in answer_normalized:
                    # Verifică variante alternative (ex: "minus infinit" pentru "-∞")
                    val_alternatives = [
                        val.replace("-∞", "minus infinit").replace("+∞", "plus infinit"),
                        val.replace("-∞", "negative infinity").replace("+∞", "positive infinity"),
                        val.replace("-∞", "-infinity").replace("+∞", "+infinity"),
                        val.replace("∞", "infinit").replace("∞", "infinity")
                    ]
                    if not any(alt in answer_normalized for alt in val_alternatives if alt):
                        all_found = False
                        break
            
            if all_found:
                return {
                    "score": 100,
                    "feedback": f"Corect! {question.get('explanation', '')}",
                    "similarity": 0.9,
                    "method": method
                }
        else:
            # Single blank - verificare flexibilă
            variant_normalized = correct_variant if case_sensitive else correct_variant.lower()
            
            # Verificare exactă
            if answer_normalized == variant_normalized:
                return {
                    "score": 100,
                    "feedback": f"Corect! {question.get('explanation', '')}",
                    "similarity": 1.0,
                    "method": method
                }
            
            # Verificare dacă răspunsul conține valoarea corectă
            if variant_normalized in answer_normalized:
                return {
                    "score": 100,
                    "feedback": f"Corect! {question.get('explanation', '')}",
                    "similarity": 0.9,
                    "method": method
                }
            
            # Verificare variante alternative (pentru simboluri speciale)
            alternatives = [
                variant_normalized.replace("-∞", "minus infinit").replace("+∞", "plus infinit"),
                variant_normalized.replace("-∞", "negative infinity").replace("+∞", "positive infinity"),
                variant_normalized.replace("-∞", "-infinity").replace("+∞", "+infinity"),
            ]
            for alt in alternatives:
                if alt and alt in answer_normalized:
                    return {
                        "score": 100,
                        "feedback": f"Corect! {question.get('explanation', '')}",
                        "similarity": 0.85,
                        "method": method
                    }
    
    # Verificare parțială pentru multiple blanks
    if correct_answers_list and isinstance(correct_answers_list[0], list):
        correct_variant = correct_answers_list[0]
        variant_normalized = [v.lower() if not case_sensitive else v for v in correct_variant]
        
        matches = 0
        for val in variant_normalized:
            if val in answer_normalized:
                matches += 1
            else:
                # Verifică alternative
                alternatives = [
                    val.replace("-∞", "minus infinit").replace("+∞", "plus infinit"),
                    val.replace("-∞", "negative infinity").replace("+∞", "positive infinity"),
                ]
                if any(alt in answer_normalized for alt in alternatives if alt):
                    matches += 1
        
        total = len(correct_variant)
        
        if matches > 0:
            partial_score = int((matches / total) * 100)
            return {
                "score": partial_score,
                "feedback": f"Parțial corect ({matches}/{total} părți corecte). Răspunsul complet corect este: {', '.join(correct_variant)}. {question.get('explanation', '')}"
            }
    
    # Răspuns greșit
    correct_display = correct_answers_list[0]
    if isinstance(correct_display, list):
        correct_display = ", ".join(correct_display)
    
    return {
        "score": 0,
        "feedback": f"Greșit. Răspunsul corect este: {correct_display}. {question.get('explanation', '')}"
    }


def _grade_short_answer(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare cu răspuns scurt - flexibil cu NLP și înțelegere semantică"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_keywords = [kw.lower() for kw in question.get("correct_keywords", [])]
    min_keywords = question.get("min_keywords", 2)
    correct_answer = question.get("correct_answer", "")
    
    # Analiză NLP pentru intenție
    intent = understand_answer_intent(answer) if NLP_ENABLED else None
    
    # Analiză semantică
    semantics = _understand_answer_semantics(answer, question)
    
    if not correct_keywords:
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
        return {
            "score": 0,
            "feedback": "Eroare: Nu există cuvinte cheie definite pentru această întrebare.",
            "similarity": 0.0,
            "method": method
        }
    
    # Dacă răspunsul este prea scurt sau fără conținut
    if not semantics["has_content"]:
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
        return {
            "score": 0,
            "feedback": f"Răspuns prea scurt sau fără conținut. Te rog oferă un răspuns mai detaliat. Concepte importante: {', '.join(correct_keywords[:3])}. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }
    
    # PRIORITATE 1: Verifică răspunsul corect complet cu NLP (dacă există)
    # Aceasta este verificarea cea mai importantă - dacă răspunsul este semantic similar cu răspunsul corect, este acceptat
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
    
    if NLP_ENABLED and correct_answer and correct_answer.strip():
        try:
            # PRIORITATE 1: Folosește semantic_similarity direct (este mai eficient)
            # compare_answers_natural returnează un dict, dar noi avem nevoie doar de similarity
            if SEMANTIC_SIMILARITY_AVAILABLE:
                # Folosește semantic_similarity care folosește modelul Sentence Transformer
                similarity = semantic_similarity(answer_original, correct_answer)
                import logging
                logging.getLogger(__name__).info(f"NLP semantic similarity: {similarity:.2f} for answer: '{answer_original[:50]}...' vs correct: '{correct_answer[:50]}...' (SEMANTIC_SIMILARITY_AVAILABLE={SEMANTIC_SIMILARITY_AVAILABLE})")
            else:
                # Fallback la semantic_similarity simplu (care folosește fuzzy matching)
                similarity = semantic_similarity(answer_original, correct_answer)
                import logging
                logging.getLogger(__name__).info(f"Fallback similarity: {similarity:.2f} for answer: '{answer_original[:50]}...' vs correct: '{correct_answer[:50]}...' (SEMANTIC_SIMILARITY_AVAILABLE={SEMANTIC_SIMILARITY_AVAILABLE})")
            
            # Dacă similaritatea este suficient de mare, acceptă răspunsul
            # Prag foarte scăzut (0.40) pentru a accepta răspunsuri corecte care exprimă ideea corectă
            # Sistemul AI trebuie să înțeleagă sensul, nu doar cuvintele
            if similarity >= 0.40:
                # Dacă similaritatea este foarte mare (>= 0.80), dă scor maxim - răspunsul este semantic corect
                if similarity >= 0.80:
                    score = 100
                    feedback_msg = f"Excelent! Răspunsul tău este semantic corect (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                elif similarity >= 0.65:
                    # Similaritate bună - răspunsul exprimă corect ideea principală
                    score = min(100, int(85 + (similarity - 0.65) * 100))  # 85-100%
                    feedback_msg = f"Corect! Răspunsul tău exprimă corect ideea principală (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                elif similarity >= 0.50:
                    # Similaritate moderată - răspunsul este parțial corect semantic
                    score = min(85, int(70 + (similarity - 0.50) * 100))  # 70-85%
                    feedback_msg = f"Bun răspuns! Răspunsul tău este parțial corect semantic (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                else:
                    # Similaritate scăzută dar acceptabilă - răspunsul are sens dar nu este complet
                    score = min(70, int(50 + (similarity - 0.40) * 200))  # 50-70%
                    feedback_msg = f"Răspuns parțial. Răspunsul tău are sens dar nu este complet (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                
                return {
                    "score": score,
                    "feedback": feedback_msg,
                    "similarity": similarity,
                    "method": method
                }
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error in NLP comparison: {e}")
            # Continuă cu verificarea conceptelor
    
    # PRIORITATE 2: Folosește NLP pentru extragere concepte (similaritate semantică)
    # IMPORTANT: Această verificare este DOAR dacă similaritatea completă nu a fost suficientă
    # Nu trebuie să dea scoruri mai mari decât similaritatea completă
    if NLP_ENABLED:
        try:
            concepts_result = extract_key_concepts(answer_original, correct_keywords)
            found_keywords = concepts_result["found_keywords"]
            concept_scores = concepts_result["scores"]
            total_concept_score = concepts_result["total_score"]
            
            # Evaluează bazat pe concepte găsite
            found_count = len(found_keywords)
            
            if found_count >= min_keywords:
                # Scor bazat pe concepte găsite și similaritatea lor
                avg_similarity = sum(concept_scores.values()) / len(concept_scores) if concept_scores else 0.7
                
                # IMPORTANT: Scorul bazat pe concepte NU trebuie să fie mai mare decât 85%
                # pentru că similaritatea completă are prioritate
                # Dacă similaritatea medie este mare (>= 0.7), dă scor bun dar nu maxim
                if avg_similarity >= 0.7:
                    score = int((found_count / len(correct_keywords)) * 85)  # Maxim 85% pentru concepte
                    score = max(60, min(85, score))  # 60-85% dacă similaritatea este bună
                else:
                    score = int((found_count / len(correct_keywords)) * 75 * avg_similarity)
                    score = max(50, min(75, score))  # 50-75% dacă are minimul necesar
                
                if found_count == len(correct_keywords) and avg_similarity >= 0.8:
                    return {
                        "score": 85,  # Nu 100% pentru că similaritatea completă are prioritate
                        "feedback": f"Bun răspuns! Ai menționat toate conceptele importante (similaritate medie: {avg_similarity:.0%}). {question.get('explanation', '')}",
                        "similarity": avg_similarity,
                        "method": method
                    }
                else:
                    return {
                        "score": score,
                        "feedback": f"Răspuns parțial. Ai menționat {found_count} din {len(correct_keywords)} concepte importante (similaritate medie: {avg_similarity:.0%}). {question.get('explanation', '')}",
                        "similarity": avg_similarity,
                        "method": method
                    }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error in NLP concept extraction: {e}")
            # Continuă cu fallback
    
    # Normalizare cuvinte cheie - elimină diacritice și variante
    def normalize_word(word):
        """Normalizează un cuvânt pentru matching flexibil"""
        replacements = {
            'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
            'ă': 'a', 'â': 'a', 'î': 'i', 'ş': 's', 'ţ': 't'
        }
        normalized = word.lower()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized
    
    # Numără câte cuvinte cheie sunt prezente în răspuns (flexibil)
    found_keywords = []
    answer_words = set(answer.split())
    answer_normalized = normalize_word(answer)
    
    for keyword in correct_keywords:
        keyword_normalized = normalize_word(keyword)
        
        # Verificare exactă
        if keyword in answer or keyword_normalized in answer_normalized:
            found_keywords.append(keyword)
            continue
        
        # Verificare ca substring (pentru cuvinte compuse)
        if keyword in answer or keyword_normalized in answer_normalized:
            found_keywords.append(keyword)
            continue
        
        # Verificare dacă cuvântul cheie este un cuvânt complet în răspuns
        # Ex: "ordine" găsește "ordinea", "ordine", "ordini"
        keyword_base = keyword.split()[0] if ' ' in keyword else keyword
        if len(keyword_base) >= 4:  # Doar pentru cuvinte de minim 4 caractere
            # Verifică dacă există un cuvânt care începe cu keyword_base
            for word in answer_words:
                if len(word) >= len(keyword_base) and word.startswith(keyword_base[:4]):
                    found_keywords.append(keyword)
                    break
    
    found_count = len(found_keywords)
    
    # Calculare scor (fallback fără NLP)
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
    # Calculează similaritate aproximativă bazată pe concepte găsite
    fallback_similarity = found_count / len(correct_keywords) if correct_keywords else 0.0
    
    if found_count >= min_keywords:
        # Răspuns corect sau aproape corect
        score = min(100, int((found_count / len(correct_keywords)) * 100))
        if found_count == len(correct_keywords):
            return {
                "score": 100,
                "feedback": f"Corect! Ai menționat toate conceptele importante. {question.get('explanation', '')}",
                "similarity": 1.0,
                "method": method
            }
        elif found_count >= min_keywords:
            return {
                "score": max(75, score),  # Minim 75% dacă are minimul necesar
                "feedback": f"Bun răspuns! Ai menționat {found_count} din {len(correct_keywords)} concepte importante. {question.get('explanation', '')}",
                "similarity": fallback_similarity,
                "method": method
            }
    elif found_count > 0:
        # Răspuns parțial
        score = int((found_count / min_keywords) * 70)  # Max 70% dacă nu are minimul
        return {
            "score": score,
            "feedback": f"Răspuns parțial. Ai menționat {found_count} concepte, dar ar trebui să menționezi cel puțin {min_keywords}. Concepte importante: {', '.join(correct_keywords)}. {question.get('explanation', '')}",
            "similarity": fallback_similarity,
            "method": method
        }
    else:
        # Răspuns greșit sau incomplet - dar verifică dacă are conținut util
        if semantics["has_content"] and len(answer_original.split()) >= 5:
            # Răspuns lung dar fără concepte cheie - poate e o încercare serioasă dar greșită
            return {
                "score": 15,  # Scor mic pentru efort
                "feedback": f"Înțeleg că ai încercat să răspunzi detaliat, dar răspunsul nu include conceptele cheie necesare. Ar trebui să menționezi cel puțin {min_keywords} dintre următoarele concepte: {', '.join(correct_keywords[:5])}. {question.get('explanation', '')}",
                "similarity": 0.15,
                "method": method
            }
        
        # Răspuns incomplet sau incorect
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
        return {
            "score": 0,
            "feedback": f"Răspuns incomplet sau incorect. Ar trebui să menționezi cel puțin {min_keywords} dintre următoarele concepte: {', '.join(correct_keywords)}. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }


def _grade_justification(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare care cere justificare - foarte flexibil cu NLP"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_keywords = [kw.lower() for kw in question.get("correct_keywords", [])]
    required_concepts = [c.lower() for c in question.get("required_concepts", [])]
    min_keywords = question.get("min_keywords", 2)
    
    if not correct_keywords and not required_concepts:
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
        return {
            "score": 0,
            "feedback": "Eroare: Nu există criterii definite pentru această întrebare.",
            "similarity": 0.0,
            "method": method
        }
    
    # Analiză NLP pentru intenție
    intent = understand_answer_intent(answer_original) if NLP_ENABLED else None
    
    all_keywords = correct_keywords + required_concepts
    
    # PRIORITATE 1: Verifică dacă justificarea este semantic similară cu răspunsul corect (dacă există)
    # Aceasta este mai importantă decât doar căutarea cuvintelor cheie
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
    correct_answer = question.get("correct_answer", "")
    
    if NLP_ENABLED and correct_answer and correct_answer.strip():
        try:
            # Compară justificarea cu răspunsul corect folosind NLP
            similarity = semantic_similarity(answer_original, correct_answer)
            import logging
            logging.getLogger(__name__).info(f"NLP semantic similarity for justification: {similarity:.2f} for answer: '{answer_original[:50]}...' vs correct: '{correct_answer[:50]}...'")
            
            # Dacă similaritatea este suficient de mare, acceptă justificarea
            # Prag scăzut (0.40) pentru a accepta justificări corecte semantic
            if similarity >= 0.40:
                if similarity >= 0.80:
                    score = 100
                    feedback_msg = f"Excelentă justificare! Răspunsul tău este semantic corect (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                elif similarity >= 0.65:
                    score = min(100, int(85 + (similarity - 0.65) * 100))
                    feedback_msg = f"Bună justificare! Răspunsul tău exprimă corect ideea principală (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                elif similarity >= 0.50:
                    score = min(85, int(70 + (similarity - 0.50) * 100))
                    feedback_msg = f"Justificare parțial corectă. Răspunsul tău este parțial corect semantic (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                else:
                    score = min(70, int(50 + (similarity - 0.40) * 200))
                    feedback_msg = f"Justificare parțială. Răspunsul tău are sens dar nu este complet (similaritate: {similarity:.0%}). {question.get('explanation', '')}"
                
                return {
                    "score": score,
                    "feedback": feedback_msg,
                    "similarity": similarity,
                    "method": method
                }
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error in NLP comparison for justification: {e}")
            # Continuă cu verificarea conceptelor
    
    # PRIORITATE 2: Folosește NLP pentru extragere concepte (similaritate semantică)
    if NLP_ENABLED:
        concepts_result = extract_key_concepts(answer_original, all_keywords)
        found_keywords = concepts_result["found_keywords"]
        concept_scores = concepts_result["scores"]
        total_concept_score = concepts_result["total_score"]
    else:
        # Fallback la metoda veche
        def normalize_word(word):
            replacements = {'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't'}
            normalized = word.lower()
            for old, new in replacements.items():
                normalized = normalized.replace(old, new)
            return normalized
        
        answer_normalized = normalize_word(answer)
        found_keywords = []
        concept_scores = {}
        for keyword in all_keywords:
            keyword_normalized = normalize_word(keyword)
            if keyword_normalized in answer_normalized or keyword in answer:
                found_keywords.append(keyword)
                concept_scores[keyword] = 1.0
        total_concept_score = len(found_keywords) / len(all_keywords) if all_keywords else 0.0
    
    found_count = len(found_keywords)
    total_keywords = len(all_keywords)
    
    # Verificare dacă răspunsul conține cuvinte cheie de justificare (folosind NLP dacă e disponibil)
    justification_words = ['deoarece', 'pentru ca', 'pentru că', 'because', 'since', 
                          'motiv', 'rațiune', 'justificare', 'justification', 'reason',
                          'explicație', 'explicatie', 'explanation', 'cauză', 'cauza']
    has_justification = any(word in answer for word in justification_words)
    
    # Verifică și intenția NLP
    if intent and intent.get("intent") == "justification":
        has_justification = True
    
    if found_count >= min_keywords and has_justification:
        # IMPORTANT: Scorul bazat pe concepte NU trebuie să fie mai mare decât 85%
        # pentru că similaritatea completă are prioritate
        # Folosește scorurile de similaritate semantică dacă sunt disponibile
        if NLP_ENABLED and concept_scores:
            avg_similarity = sum(concept_scores.values()) / len(concept_scores)
            score = min(85, int((found_count / total_keywords) * 85 * avg_similarity))  # Maxim 85%
            score = max(60, score)  # Minim 60%
        else:
            score = min(85, int((found_count / total_keywords) * 85))  # Maxim 85%
            score = max(60, score)  # Minim 60%
        
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
        if score >= 80:
            similarity_msg = f" (similaritate semantică: {avg_similarity:.0%})" if NLP_ENABLED and concept_scores else ""
            return {
                "score": score,  # Nu 100% pentru că similaritatea completă are prioritate
                "feedback": f"Bună justificare! Ai menționat {found_count} din {total_keywords} concepte importante{similarity_msg}. {question.get('explanation', '')}",
                "similarity": avg_similarity if (NLP_ENABLED and concept_scores) else total_concept_score,
                "method": method
            }
        else:
            similarity_msg = f" (similaritate medie: {avg_similarity:.0%})" if NLP_ENABLED and concept_scores else ""
            return {
                "score": score,
                "feedback": f"Justificare parțială. Ai menționat {found_count} din {total_keywords} concepte importante{similarity_msg}. {question.get('explanation', '')}",
                "similarity": avg_similarity if (NLP_ENABLED and concept_scores) else total_concept_score,
                "method": method
            }
    elif found_count >= min_keywords:
        score = int((found_count / total_keywords) * 80)  # Penalizare pentru lipsa cuvintelor de justificare
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
        return {
            "score": score,
            "feedback": f"Răspuns parțial. Ai menționat conceptele, dar ar trebui să incluzi o justificare mai clară (folosind 'deoarece', 'pentru că', etc.). {question.get('explanation', '')}",
            "similarity": total_concept_score,
            "method": method
        }
    elif found_count > 0:
        score = int((found_count / min_keywords) * 60)
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
        return {
            "score": score,
            "feedback": f"Justificare incompletă. Ai menționat {found_count} concepte, dar ar trebui să menționezi cel puțin {min_keywords}. Concepte importante: {', '.join(all_keywords[:5])}. {question.get('explanation', '')}",
            "similarity": total_concept_score,
            "method": method
        }
    else:
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
        return {
            "score": 0,
            "feedback": f"Justificare insuficientă. Ar trebui să menționezi cel puțin {min_keywords} dintre următoarele concepte: {', '.join(all_keywords[:5])}. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }


def _grade_example(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare care cere exemple - foarte flexibil cu NLP"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_keywords = [kw.lower() for kw in question.get("correct_keywords", [])]
    correct_answer = question.get("correct_answer", "")
    example_types = question.get("example_types", [])
    min_keywords = question.get("min_keywords", 2)
    
    # PRIORITATE 1: Folosește NLP dacă este disponibil și există correct_answer
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Keyword Matching")
    if NLP_ENABLED and correct_answer and correct_answer.strip():
        try:
            similarity = semantic_similarity(answer_original, correct_answer)
            import logging
            logging.getLogger(__name__).info(f"NLP semantic similarity for example: {similarity:.2f}")
            
            # Dacă similaritatea este suficient de mare, acceptă răspunsul
            if similarity >= 0.70:
                score = min(100, int(70 + similarity * 30))  # 70-100% bazat pe similaritate
                return {
                    "score": score,
                    "feedback": f"Excelent exemplu! (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": method
                }
            elif similarity >= 0.50:
                score = int(50 + (similarity - 0.50) * 100)  # 50-70%
                return {
                    "score": score,
                    "feedback": f"Bun exemplu! (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": method
                }
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error in NLP for example: {e}")
            # Continuă cu verificarea keyword-urilor
    
    # Fallback: verificare keyword-uri
    if not correct_keywords:
        # Încearcă să extragă keywords din correct_answer sau explanation
        if correct_answer:
            words = correct_answer.split()
            correct_keywords = [w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5]
        elif question.get("explanation"):
            words = question.get("explanation", "").split()
            correct_keywords = [w.lower().strip('.,!?;:') for w in words if len(w) > 4][:5]
        else:
            return {
                "score": 0,
                "feedback": "Eroare: Nu există criterii definite pentru această întrebare.",
                "similarity": 0.0,
                "method": method
            }
    
    # Verifică dacă răspunsul conține cuvinte cheie de exemplu
    example_words = ['exemplu', 'exemple', 'example', 'examples', 'instanță', 'instanta',
                    'instance', 'caz', 'cazuri', 'case', 'cases', 'situație', 'situatie',
                    'situation', 'de exemplu', 'for example', 'e.g.', 'ex:', 'cum ar fi']
    has_example_indicator = any(word in answer for word in example_words)
    
    # Normalizare
    def normalize_word(word):
        replacements = {'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't'}
        normalized = word.lower()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized
    
    answer_normalized = normalize_word(answer)
    
    # Numără conceptele găsite
    found_keywords = []
    for keyword in correct_keywords:
        keyword_normalized = normalize_word(keyword)
        if keyword_normalized in answer_normalized or keyword in answer:
            found_keywords.append(keyword)
    
    found_count = len(found_keywords)
    
    if found_count >= min_keywords and has_example_indicator:
        score = min(100, int((found_count / len(correct_keywords)) * 100))
        return {
            "score": score,
            "feedback": f"Bun exemplu! Ai oferit un exemplu relevant care include conceptele importante. {question.get('explanation', '')}",
            "similarity": found_count / len(correct_keywords) if correct_keywords else 0.0,
            "method": method
        }
    elif found_count >= min_keywords:
        score = int((found_count / len(correct_keywords)) * 75)  # Penalizare pentru lipsa indicatorului
        return {
            "score": score,
            "feedback": f"Exemplu parțial. Ai menționat conceptele, dar ar trebui să fie mai clar că este un exemplu. {question.get('explanation', '')}",
            "similarity": found_count / len(correct_keywords) if correct_keywords else 0.0,
            "method": method
        }
    elif found_count > 0:
        score = int((found_count / min_keywords) * 50)
        return {
            "score": score,
            "feedback": f"Exemplu incomplet. Ai menționat {found_count} concepte, dar ar trebui să menționezi cel puțin {min_keywords}. Concepte importante: {', '.join(correct_keywords[:5])}. {question.get('explanation', '')}",
            "similarity": found_count / min_keywords if min_keywords > 0 else 0.0,
            "method": method
        }
    else:
        return {
            "score": 0,
            "feedback": f"Exemplu insuficient sau incorect. Ar trebui să menționezi cel puțin {min_keywords} dintre următoarele concepte: {', '.join(correct_keywords[:5])}. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }


def _grade_comparison(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare care cere comparare - foarte flexibil cu NLP"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    concepts_to_compare = question.get("concepts_to_compare", [])
    comparison_keywords = [kw.lower() for kw in question.get("comparison_keywords", [])]
    min_keywords = question.get("min_keywords", 3)
    correct_answer = question.get("correct_answer", "")
    
    if not concepts_to_compare or len(concepts_to_compare) < 2:
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
        return {
            "score": 0,
            "feedback": "Eroare: Nu există concepte definite pentru comparare.",
            "similarity": 0.0,
            "method": method
        }
    
    # PRIORITATE 1: Folosește NLP dacă este disponibil și există correct_answer
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
    if NLP_ENABLED and correct_answer and correct_answer.strip():
        try:
            similarity = semantic_similarity(answer_original, correct_answer)
            logging.getLogger(__name__).info(f"NLP semantic similarity for comparison: {similarity:.2f}")
            
            if similarity >= 0.80:
                return {
                    "score": 100,
                    "feedback": f"Excelentă comparație! Răspunsul tău este semantic corect (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
                }
            elif similarity >= 0.65:
                score = int(85 + (similarity - 0.65) / 0.15 * 15)  # 85-100%
                return {
                    "score": score,
                    "feedback": f"Bună comparație! Exprimi corect ideea principală (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
                }
            elif similarity >= 0.50:
                score = int(70 + (similarity - 0.50) / 0.15 * 15)  # 70-85%
                return {
                    "score": score,
                    "feedback": f"Comparație parțial corectă semantic (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
                }
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error in NLP semantic similarity for comparison: {e}")
            # Continuă cu fallback
    
    # PRIORITATE 2: Fallback la keyword matching
    # Verifică dacă răspunsul menționează ambele concepte
    concept1 = concepts_to_compare[0].lower()
    concept2 = concepts_to_compare[1].lower() if len(concepts_to_compare) > 1 else ""
    
    has_concept1 = concept1 in answer
    has_concept2 = concept2 in answer if concept2 else True
    
    # Verifică cuvinte cheie de comparare
    comparison_words = ['diferă', 'difera', 'differ', 'diferență', 'diferenta', 'difference',
                      'similar', 'similaritate', 'similarity', 'compară', 'compara', 'compare',
                      'vs', 'versus', 'față de', 'fata de', 'compared to', 'în comparație',
                      'in comparatie', 'mai', 'less', 'decât', 'decât', 'than', 'și', 'and',
                      'dar', 'but', 'însă', 'insa', 'however', 'pe de altă parte', 'on the other hand']
    has_comparison = any(word in answer for word in comparison_words)
    
    # Numără conceptele de comparare găsite
    found_keywords = []
    for keyword in comparison_keywords:
        if keyword in answer:
            found_keywords.append(keyword)
    
    found_count = len(found_keywords)
    similarity_fallback = found_count / len(comparison_keywords) if comparison_keywords else 0.0
    
    if has_concept1 and has_concept2 and has_comparison and found_count >= min_keywords:
        score = min(100, int((found_count / len(comparison_keywords)) * 100))
        return {
            "score": score,
            "feedback": f"Excelentă comparație! Ai comparat corect ambele concepte și ai menționat aspectele importante. {question.get('explanation', '')}",
            "similarity": similarity_fallback,
            "method": method
        }
    elif has_concept1 and has_concept2 and found_count >= min_keywords:
        score = int((found_count / len(comparison_keywords)) * 80)
        return {
            "score": score,
            "feedback": f"Bună comparație! Ai menționat ambele concepte și aspectele importante. {question.get('explanation', '')}",
            "similarity": similarity_fallback,
            "method": method
        }
    elif (has_concept1 or has_concept2) and found_count > 0:
        score = int((found_count / min_keywords) * 60)
        return {
            "score": score,
            "feedback": f"Comparație incompletă. Ai menționat un concept, dar ar trebui să compari ambele: {concept1} și {concept2}. {question.get('explanation', '')}",
            "similarity": similarity_fallback,
            "method": method
        }
    else:
        return {
            "score": 0,
            "feedback": f"Comparație insuficientă. Ar trebui să compari {concept1} și {concept2}, menționând cel puțin {min_keywords} aspecte. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }


def _grade_definition(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare care cere definiție - foarte flexibil"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_keywords = [kw.lower() for kw in question.get("correct_keywords", [])]
    definition_elements = [e.lower() for e in question.get("definition_elements", [])]
    min_keywords = question.get("min_keywords", 3)
    correct_answer = question.get("correct_answer", "")
    
    if not correct_keywords and not definition_elements:
        method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
        return {
            "score": 0,
            "feedback": "Eroare: Nu există criterii definite pentru această întrebare.",
            "similarity": 0.0,
            "method": method
        }
    
    # PRIORITATE 1: Folosește NLP dacă este disponibil și există correct_answer
    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback (Simple Matching)")
    if NLP_ENABLED and correct_answer and correct_answer.strip():
        try:
            similarity = semantic_similarity(answer_original, correct_answer)
            logging.getLogger(__name__).info(f"NLP semantic similarity for definition: {similarity:.2f}")
            
            if similarity >= 0.80:
                return {
                    "score": 100,
                    "feedback": f"Excelent! Răspunsul tău este semantic corect (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
                }
            elif similarity >= 0.65:
                score = int(85 + (similarity - 0.65) / 0.15 * 15)  # 85-100%
                return {
                    "score": score,
                    "feedback": f"Bun răspuns! Exprimi corect ideea principală (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
                }
            elif similarity >= 0.50:
                score = int(70 + (similarity - 0.50) / 0.15 * 15)  # 70-85%
                return {
                    "score": score,
                    "feedback": f"Răspuns parțial corect semantic (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
                }
            elif similarity >= 0.40:
                score = int(50 + (similarity - 0.40) / 0.10 * 20)  # 50-70%
                return {
                    "score": score,
                    "feedback": f"Răspunsul are sens dar nu este complet (similaritate: {similarity:.0%}). {question.get('explanation', '')}",
                    "similarity": similarity,
                    "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
                }
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error in NLP semantic similarity for definition: {e}")
            # Continuă cu fallback
    
    # PRIORITATE 2: Fallback la keyword matching
    # Normalizare
    def normalize_word(word):
        replacements = {'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't'}
        normalized = word.lower()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized
    
    answer_normalized = normalize_word(answer)
    all_elements = correct_keywords + definition_elements
    
    # Numără elementele găsite
    found_elements = []
    for element in all_elements:
        element_normalized = normalize_word(element)
        if element_normalized in answer_normalized or element in answer:
            found_elements.append(element)
    
    found_count = len(found_elements)
    similarity_fallback = found_count / len(all_elements) if all_elements else 0.0
    
    if found_count >= min_keywords:
        score = min(100, int((found_count / len(all_elements)) * 100))
        if score >= 90:
            return {
                "score": 100,
                "feedback": f"Definiție completă și corectă! Ai inclus toate elementele esențiale. {question.get('explanation', '')}",
                "similarity": similarity_fallback,
                "method": method
            }
        else:
            return {
                "score": score,
                "feedback": f"Bună definiție! Ai inclus {found_count} din {len(all_elements)} elemente esențiale. {question.get('explanation', '')}",
                "similarity": similarity_fallback,
                "method": method
            }
    elif found_count > 0:
        score = int((found_count / min_keywords) * 70)
        return {
            "score": score,
            "feedback": f"Definiție parțială. Ai menționat {found_count} elemente, dar ar trebui să incluzi cel puțin {min_keywords}. Elemente importante: {', '.join(all_elements[:5])}. {question.get('explanation', '')}",
            "similarity": similarity_fallback,
            "method": method
        }
    else:
        return {
            "score": 0,
            "feedback": f"Definiție insuficientă. Ar trebui să incluzi cel puțin {min_keywords} dintre următoarele elemente: {', '.join(all_elements[:5])}. {question.get('explanation', '')}",
            "similarity": 0.0,
            "method": method
        }


def _grade_calculation(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare care cere calcul - foarte flexibil"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_answer = question.get("correct_answer", "")
    correct_answer_numeric = question.get("correct_answer_numeric", None)
    acceptable_range = question.get("acceptable_range", None)
    
    # Încearcă să extragă numere din răspuns
    import re
    numbers = re.findall(r'-?\d+\.?\d*', answer_original)
    
    # Verificare numerică
    if correct_answer_numeric is not None:
        for num_str in numbers:
            try:
                num_value = float(num_str)
                if acceptable_range:
                    min_val, max_val = acceptable_range
                    if min_val <= num_value <= max_val:
                        return {
                            "score": 100,
                            "feedback": f"Corect! Răspunsul {num_value} este în intervalul acceptabil. {question.get('explanation', '')}"
                        }
                elif abs(num_value - correct_answer_numeric) < 0.01:  # Toleranță pentru erori de rotunjire
                    return {
                        "score": 100,
                        "feedback": f"Corect! Răspunsul {num_value} este corect. {question.get('explanation', '')}"
                    }
            except ValueError:
                continue
    
    # Verificare text (pentru răspunsuri ca "O(b^d)", "exponential", etc.)
    correct_lower = correct_answer.lower()
    if correct_lower in answer or answer in correct_lower:
        return {
            "score": 100,
            "feedback": f"Corect! {question.get('explanation', '')}"
        }
    
    # Verificare parțială
    if correct_lower in answer:
        return {
            "score": 85,
            "feedback": f"Parțial corect. Răspunsul complet corect este: {correct_answer}. {question.get('explanation', '')}"
        }
    
    # Verificare dacă răspunsul conține concepte cheie despre calcul
    calculation_keywords = ['complexitate', 'complexity', 'o(', 'big o', 'theta', 'omega',
                           'exponential', 'exponențial', 'polynomial', 'polinomial', 'logaritmic',
                           'logarithmic', 'liniar', 'linear', 'constant', 'constantă']
    has_calculation_concept = any(kw in answer for kw in calculation_keywords)
    
    if has_calculation_concept:
        return {
            "score": 50,
            "feedback": f"Răspuns parțial. Ai menționat concepte relevante, dar răspunsul complet corect este: {correct_answer}. {question.get('explanation', '')}"
        }
    
    return {
        "score": 0,
        "feedback": f"Răspuns incorect. Răspunsul corect este: {correct_answer}. {question.get('explanation', '')}"
    }


def _grade_matrix_analysis(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul la o întrebare despre analiza jocurilor matriceale - foarte flexibil"""
    answer_original = answer.strip()
    answer = answer_original.lower()
    correct_answer = question.get("correct_answer", "")
    correct_keywords = [kw.lower() for kw in question.get("correct_keywords", [])]
    analysis_type = question.get("analysis_type", "nash_equilibrium")
    
    # Verificare răspuns exact
    correct_lower = correct_answer.lower()
    if correct_lower in answer or answer in correct_lower:
        return {
            "score": 100,
            "feedback": f"Corect! {question.get('explanation', '')}"
        }
    
    # Verificare cuvinte cheie
    found_keywords = []
    for keyword in correct_keywords:
        if keyword in answer:
            found_keywords.append(keyword)
    
    found_count = len(found_keywords)
    
    # Verificare pentru Nash equilibrium
    if analysis_type == "nash_equilibrium":
        nash_keywords = ['nash', 'echilibru', 'equilibrium', 'best response', 'raspuns optim',
                        'raspuns optim', 'optimal response', 'nu poate îmbunătăți', 'nu poate imbunatati']
        has_nash_concept = any(kw in answer for kw in nash_keywords)
        
        if has_nash_concept and found_count >= 2:
            return {
                "score": 85,
                "feedback": f"Bună analiză! Ai identificat corect conceptul de echilibru Nash. {question.get('explanation', '')}"
            }
        elif has_nash_concept:
            return {
                "score": 70,
                "feedback": f"Analiză parțială. Ai menționat echilibru Nash, dar ar trebui să incluzi mai multe detalii. {question.get('explanation', '')}"
            }
    
    if found_count >= len(correct_keywords) * 0.7:
        return {
            "score": 80,
            "feedback": f"Bună analiză! Ai menționat majoritatea conceptelor importante. {question.get('explanation', '')}"
        }
    elif found_count > 0:
        return {
            "score": int((found_count / len(correct_keywords)) * 60),
            "feedback": f"Analiză parțială. Ai menționat {found_count} concepte, dar ar trebui să incluzi mai multe. Concepte importante: {', '.join(correct_keywords[:5])}. {question.get('explanation', '')}"
        }
    else:
        return {
            "score": 0,
            "feedback": f"Analiză insuficientă. Răspunsul corect este: {correct_answer}. Concepte importante: {', '.join(correct_keywords[:5])}. {question.get('explanation', '')}"
        }

