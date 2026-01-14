"""
Modul pentru procesare de limbaj natural (NLP) pentru evaluarea răspunsurilor.
Folosește similaritate semantică pentru a înțelege răspunsurile naturale.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag pentru a verifica dacă bibliotecile NLP sunt disponibile
NLP_AVAILABLE = False
SEMANTIC_SIMILARITY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    SEMANTIC_SIMILARITY_AVAILABLE = True
    logger.info("Sentence Transformers loaded successfully")
except ImportError:
    logger.warning("Sentence Transformers not available. Install with: pip install sentence-transformers scikit-learn")
    try:
        # Fallback la fuzzy matching
        from fuzzywuzzy import fuzz, process
        from fuzzywuzzy.utils import full_process
        NLP_AVAILABLE = True
        logger.info("FuzzyWuzzy loaded as fallback")
    except ImportError:
        logger.warning("FuzzyWuzzy not available. Install with: pip install fuzzywuzzy python-Levenshtein")

# Modelul pentru similaritate semantică (se încarcă la prima utilizare)
_semantic_model = None


def get_semantic_model():
    """Încarcă modelul pentru similaritate semantică (lazy loading)"""
    global _semantic_model
    if _semantic_model is None and SEMANTIC_SIMILARITY_AVAILABLE:
        try:
            import ssl
            import certifi
            import os
            
            # Fix pentru problema cu certificatul SSL
            # FORȚEAZĂ folosirea certificatului de la certifi (suprascrie setările PostgreSQL)
            try:
                ssl_cert = certifi.where()
                # Suprascrie variabilele de mediu chiar dacă sunt deja setate (pentru a evita calea greșită de la PostgreSQL)
                os.environ['SSL_CERT_FILE'] = ssl_cert
                os.environ['REQUESTS_CA_BUNDLE'] = ssl_cert
                # Setează și pentru requests
                import requests
                requests.utils.DEFAULT_CA_BUNDLE_PATH = ssl_cert
                logger.info(f"Using SSL certificate from certifi: {ssl_cert}")
            except Exception as cert_error:
                logger.warning(f"Could not set SSL certificate from certifi: {cert_error}")
                # Dacă certifi nu funcționează, dezactivează verificarea SSL (doar pentru descărcare)
                try:
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    # Setează pentru requests să nu verifice SSL
                    import requests
                    requests.packages.urllib3.disable_warnings()
                except:
                    pass
            
            # Folosim un model multilingv care funcționează bine pentru română și engleză
            # Paraphrase-Multilingual-MiniLM - ușor și rapid
            # Fix pentru problema cu meta tensor - încarcă modelul fără device specificat
            # Modelul va rămâne pe CPU implicit și va funcționa corect
            # Încarcă modelul - problema cu meta tensor apare doar la inițializare
            # dar modelul funcționează corect când este folosit (vezi "Batches: 100%" în log-uri)
            # Deci ignorăm eroarea de inițializare dacă apare, modelul va funcționa la utilizare
            try:
                _semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("Semantic model loaded: paraphrase-multilingual-MiniLM-L12-v2")
            except NotImplementedError as meta_error:
                # Eroarea cu meta tensor apare la inițializare, dar modelul funcționează la utilizare
                # Setăm modelul ca None și îl vom încărca la prima utilizare efectivă
                logger.warning(f"Meta tensor error at initialization (will work on first use): {meta_error}")
                # Nu setăm _semantic_model = None, ci încercăm să-l folosim oricum
                # Modelul va funcționa când este folosit efectiv pentru embeddings
                try:
                    # Încarcă fără device specificat
                    _semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', trust_remote_code=True)
                    logger.info("Semantic model loaded: paraphrase-multilingual-MiniLM-L12-v2 (after meta tensor error)")
                except:
                    # Dacă tot nu funcționează, lasă None - va folosi fallback
                    logger.error("Could not load model even after retry, will use fallback methods")
                    _semantic_model = None
            except Exception as load_error:
                logger.warning(f"Error loading model: {load_error}")
                _semantic_model = None
        except Exception as e:
            logger.error(f"Error loading semantic model: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    return _semantic_model


def semantic_similarity(text1: str, text2: str) -> float:
    """
    Calculează similaritatea semantică între două texte (0-1).
    
    Args:
        text1: Primul text
        text2: Al doilea text
    
    Returns:
        Scor de similaritate între 0 și 1 (1 = identic semantic, 0 = complet diferit)
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalizare de bază
    text1 = text1.strip().lower()
    text2 = text2.strip().lower()
    
    # Verificare exactă (după normalizare)
    if text1 == text2:
        return 1.0
    
    # Verificare substring (pentru răspunsuri parțiale)
    if text1 in text2 or text2 in text1:
        return 0.9
    
    # Folosește modelul semantic dacă este disponibil
    model = get_semantic_model()
    if model:
        try:
            # Încarcă modelul dacă nu este deja încărcat (lazy loading la utilizare efectivă)
            # Aceasta rezolvă problema cu meta tensor - modelul se încarcă corect când este folosit
            logger.info(f"Using NLP model for semantic similarity: '{text1[:30]}...' vs '{text2[:30]}...'")
            embeddings = model.encode([text1, text2], convert_to_numpy=True, show_progress_bar=False)
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            logger.info(f"NLP semantic similarity result: {similarity:.3f}")
            return float(similarity)
        except Exception as e:
            logger.warning(f"Error computing semantic similarity: {e}")
            # Dacă modelul nu funcționează, încearcă să-l reîncarce
            global _semantic_model
            _semantic_model = None
            try:
                model = get_semantic_model()
                if model:
                    embeddings = model.encode([text1, text2], convert_to_numpy=True, show_progress_bar=False)
                    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                    return float(similarity)
            except:
                pass
    
    # Fallback la fuzzy matching
    if NLP_AVAILABLE:
        try:
            from fuzzywuzzy import fuzz
            ratio = fuzz.ratio(text1, text2) / 100.0
            partial_ratio = fuzz.partial_ratio(text1, text2) / 100.0
            token_sort_ratio = fuzz.token_sort_ratio(text1, text2) / 100.0
            # Media ponderată
            similarity = (ratio * 0.3 + partial_ratio * 0.4 + token_sort_ratio * 0.3)
            return similarity
        except Exception as e:
            logger.warning(f"Error in fuzzy matching: {e}")
    
    # Fallback final - Levenshtein simplu
    return _simple_similarity(text1, text2)


def _simple_similarity(text1: str, text2: str) -> float:
    """Similaritate simplă bazată pe distanță Levenshtein"""
    if not text1 or not text2:
        return 0.0
    
    # Normalizare
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    
    if text1 == text2:
        return 1.0
    
    # Verificare substring
    if text1 in text2 or text2 in text1:
        return 0.85
    
    # Distanță Levenshtein simplificată
    len1, len2 = len(text1), len(text2)
    max_len = max(len1, len2)
    if max_len == 0:
        return 1.0
    
    # Calculează distanța (simplificat)
    matches = sum(1 for a, b in zip(text1, text2) if a == b)
    similarity = matches / max_len
    
    return similarity


def find_best_match(user_answer: str, correct_answers: List[str], threshold: float = 0.7) -> Tuple[Optional[str], float]:
    """
    Găsește cel mai bun match pentru răspunsul utilizatorului din lista de răspunsuri corecte.
    
    Args:
        user_answer: Răspunsul utilizatorului
        correct_answers: Lista de răspunsuri corecte posibile
        threshold: Prag minim de similaritate (0-1)
    
    Returns:
        Tuple (răspunsul cel mai similar, scorul de similaritate) sau (None, 0.0)
    """
    if not user_answer or not correct_answers:
        return None, 0.0
    
    best_match = None
    best_score = 0.0
    
    for correct_answer in correct_answers:
        score = semantic_similarity(user_answer, correct_answer)
        if score > best_score:
            best_score = score
            best_match = correct_answer
    
    if best_score >= threshold:
        return best_match, best_score
    
    return None, best_score


def extract_key_concepts(text: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Extrage concepte cheie din text folosind similaritate semantică.
    
    Args:
        text: Textul de analizat
        keywords: Lista de cuvinte/concepte cheie de căutat
    
    Returns:
        Dict cu "found_keywords" (lista conceptelor găsite), 
        "scores" (scoruri de similaritate), "total_score" (scor total)
    """
    if not text or not keywords:
        return {
            "found_keywords": [],
            "scores": {},
            "total_score": 0.0
        }
    
    found_keywords = []
    scores = {}
    
    text_lower = text.lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Verificare exactă
        if keyword_lower in text_lower:
            found_keywords.append(keyword)
            scores[keyword] = 1.0
            continue
        
        # Verificare similaritate semantică (prag mai jos pentru flexibilitate)
        similarity = semantic_similarity(text, keyword)
        if similarity >= 0.5:  # Prag mai jos pentru a găsi mai multe concepte
            found_keywords.append(keyword)
            scores[keyword] = similarity
    
    # Scor total (media scorurilor)
    total_score = sum(scores.values()) / len(keywords) if keywords else 0.0
    
    return {
        "found_keywords": found_keywords,
        "scores": scores,
        "total_score": total_score
    }


def understand_answer_intent(answer: str) -> Dict[str, Any]:
    """
    Înțelege intenția răspunsului utilizatorului folosind NLP.
    
    Returns:
        Dict cu "intent" (tipul intenției), "confidence" (încredere 0-1),
        "has_answer" (dacă conține un răspuns), "sentiment" (pozitiv/negativ/neutru)
    """
    if not answer or len(answer.strip()) < 2:
        return {
            "intent": "empty",
            "confidence": 0.0,
            "has_answer": False,
            "sentiment": "neutral"
        }
    
    answer_lower = answer.lower().strip()
    
    # Detectare intenții
    intents = {
        "uncertainty": ["nu știu", "nu stiu", "don't know", "no idea", "nu sunt sigur", "not sure"],
        "affirmation": ["da", "yes", "adevărat", "adevarat", "true", "corect", "correct"],
        "negation": ["nu", "no", "fals", "false", "greșit", "gresit", "wrong", "incorrect"],
        "partial": ["parțial", "partial", "poate", "maybe", "probabil", "probably"],
        "justification": ["deoarece", "pentru că", "pentru ca", "because", "motiv", "reason"]
    }
    
    detected_intent = "answer"
    confidence = 0.5
    
    for intent, patterns in intents.items():
        for pattern in patterns:
            if pattern in answer_lower:
                detected_intent = intent
                confidence = 0.8
                break
        if detected_intent != "answer":
            break
    
    # Detectare sentiment simplă
    positive_words = ["corect", "bun", "da", "adevărat", "adevarat", "exact", "perfect"]
    negative_words = ["greșit", "gresit", "nu", "fals", "incorrect", "wrong"]
    
    sentiment = "neutral"
    if any(word in answer_lower for word in positive_words):
        sentiment = "positive"
    elif any(word in answer_lower for word in negative_words):
        sentiment = "negative"
    
    has_answer = len(answer.split()) >= 2 or detected_intent in ["affirmation", "negation"]
    
    return {
        "intent": detected_intent,
        "confidence": confidence,
        "has_answer": has_answer,
        "sentiment": sentiment
    }


def normalize_text(text: str) -> str:
    """
    Normalizează textul pentru procesare NLP.
    - Elimină diacritice opțional
    - Normalizează spații
    - Elimină caractere speciale opțional
    """
    if not text:
        return ""
    
    # Normalizare de bază
    text = text.strip()
    
    # Normalizează spații multiple
    text = re.sub(r'\s+', ' ', text)
    
    # Opțional: elimină diacritice (pentru matching mai flexibil)
    # text = text.replace('ă', 'a').replace('â', 'a').replace('î', 'i')
    # text = text.replace('ș', 's').replace('ț', 't')
    
    return text


def compare_answers_natural(user_answer: str, correct_answer: str, 
                           threshold: float = 0.65) -> Dict[str, Any]:
    """
    Compară răspunsul utilizatorului cu răspunsul corect folosind NLP.
    
    Args:
        user_answer: Răspunsul utilizatorului
        correct_answer: Răspunsul corect
        threshold: Prag minim pentru considerare "corect" (0-1) - default 0.65 pentru flexibilitate
    
    Returns:
        Dict cu "is_correct" (bool), "similarity" (0-1), "feedback" (mesaj)
    """
    similarity = semantic_similarity(user_answer, correct_answer)
    is_correct = similarity >= threshold
    
    if is_correct:
        feedback = "Răspuns corect!"
    elif similarity >= threshold * 0.8:  # 80% din prag
        feedback = f"Răspuns aproape corect (similaritate: {similarity:.0%})"
    else:
        feedback = f"Răspuns incorect (similaritate: {similarity:.0%})"
    
    return {
        "is_correct": is_correct,
        "similarity": similarity,
        "feedback": feedback
    }

