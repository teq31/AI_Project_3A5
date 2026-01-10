"""
SmarTest — Problema 3: CSP cu Backtracking
Constraint Satisfaction Problems cu optimizări: Forward Checking, MRV, AC-3
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any, Set
import random

# ---------- definiții probleme CSP ----------

CSP_PROBLEMS = {
    "simple": {
        "name": "CSP Simplu",
        "description": "Problema de satisfacere a constrângerilor cu variabile discrete",
        "optimizations": ["Backtracking", "Forward Checking", "MRV", "AC-3"],
        "default_optimization": "Backtracking"
    },
    "graph_coloring": {
        "name": "Graph Coloring CSP",
        "description": "Problema colorării grafurilor modelată ca CSP",
        "optimizations": ["Backtracking", "Forward Checking", "MRV", "AC-3"],
        "default_optimization": "Forward Checking"
    },
    "sudoku": {
        "name": "Sudoku CSP",
        "description": "Problema Sudoku modelată ca CSP",
        "optimizations": ["Backtracking", "Forward Checking", "MRV", "AC-3"],
        "default_optimization": "AC-3"
    }
}

# ---------- generare instanță CSP ----------

def generate_simple_csp_instance(variables: int = 4, domain_size: int = 3, constraints: int = 3, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o instanță CSP simplă"""
    if seed is not None:
        random.seed(seed)
    
    # Generează variabile
    var_names = [f"X{i+1}" for i in range(variables)]
    domains = {var: list(range(1, domain_size + 1)) for var in var_names}
    
    # Generează constrângeri binare aleatoare
    constraint_list = []
    for _ in range(constraints):
        var1, var2 = random.sample(var_names, 2)
        # Constrângere: var1 != var2
        constraint_list.append((var1, var2, "!="))
    
    # Alege optimizarea corectă în funcție de complexitatea problemei
    if variables <= 4 and constraints <= 3:
        # Pentru probleme simple, Backtracking de bază este suficient
        correct_optimization = "Backtracking"
    elif variables <= 5:
        # Pentru probleme medii, Forward Checking reduce spațiul de căutare
        correct_optimization = "Forward Checking"
    elif constraints / variables > 1.5:
        # Pentru multe constrângeri, AC-3 este eficient
        correct_optimization = "AC-3"
    else:
        # Pentru probleme cu multe variabile, MRV alege variabilele eficient
        correct_optimization = "MRV"
    
    return {
        "problem_type": "simple",
        "instance": {
            "variables": var_names,
            "domains": domains,
            "constraints": constraint_list,
            "description": f"Rezolvă un CSP cu {variables} variabile ({', '.join(var_names)}), fiecare cu domeniu {{1, 2, ..., {domain_size}}}, și {len(constraint_list)} constrângeri binare."
        },
        "correct_optimization": correct_optimization
    }

def generate_graph_coloring_csp_instance(vertices: int = 4, colors: int = 3, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o instanță CSP pentru graph coloring"""
    if seed is not None:
        random.seed(seed)
    
    var_names = [f"V{i+1}" for i in range(vertices)]
    domains = {var: list(range(1, colors + 1)) for var in var_names}
    
    # Generează muchii (constrângeri: nodurile adiacente trebuie să aibă culori diferite)
    edges = []
    for i in range(vertices):
        for j in range(i + 1, min(i + 3, vertices)):
            if random.random() > 0.3:  # 70% probabilitate de muchie
                edges.append((var_names[i], var_names[j]))
    
    constraint_list = [(v1, v2, "!=") for v1, v2 in edges]
    
    # Alege optimizarea corectă
    if vertices <= 4:
        correct_optimization = "Forward Checking"
    elif len(edges) / vertices > 1.2:
        correct_optimization = "AC-3"
    else:
        correct_optimization = "MRV"
    
    return {
        "problem_type": "graph_coloring",
        "instance": {
            "variables": var_names,
            "domains": domains,
            "constraints": constraint_list,
            "edges": edges,
            "colors": colors,
            "description": f"Colorează un graf cu {vertices} noduri folosind {colors} culori, astfel încât nodurile conectate să aibă culori diferite."
        },
        "correct_optimization": correct_optimization
    }

def generate_sudoku_csp_instance(size: int = 4, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o instanță CSP pentru Sudoku (simplificat)"""
    if seed is not None:
        random.seed(seed)
    
    # Pentru Sudoku, AC-3 este de obicei cea mai bună alegere datorită constrângerilor puternice
    correct_optimization = "AC-3"
    
    return {
        "problem_type": "sudoku",
        "instance": {
            "size": size,
            "description": f"Rezolvă un puzzle Sudoku {size}x{size} (simplificat) modelat ca CSP, unde fiecare celulă trebuie să aibă o valoare unică pe rând, coloană și regiune."
        },
        "correct_optimization": correct_optimization
    }

# ---------- generare întrebare ----------

def generate_csp_question(problem_type: str = "simple", optimization: str = "FC", seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o întrebare despre CSP și optimizarea sa"""
    if seed is not None:
        random.seed(seed)
    
    if problem_type == "simple":
        instance_data = generate_simple_csp_instance(
            variables=random.randint(4, 6),
            domain_size=random.randint(3, 4),
            constraints=random.randint(3, 5),
            seed=seed
        )
    elif problem_type == "graph_coloring":
        instance_data = generate_graph_coloring_csp_instance(
            vertices=random.randint(4, 6),
            colors=random.randint(3, 4),
            seed=seed
        )
    elif problem_type == "sudoku":
        instance_data = generate_sudoku_csp_instance(size=4, seed=seed)
    else:
        raise ValueError(f"Problem type {problem_type} not supported")
    
    problem_info = CSP_PROBLEMS[problem_type]
    correct_optimization = instance_data["correct_optimization"]
    
    # Generează opțiuni (corectă + 3 greșite)
    all_optimizations = problem_info["optimizations"]
    wrong_optimizations = [opt for opt in all_optimizations if opt != correct_optimization]
    options = [correct_optimization] + random.sample(wrong_optimizations, min(3, len(wrong_optimizations)))
    random.shuffle(options)
    
    return {
        "problem_type": problem_type,
        "problem_name": problem_info["name"],
        "instance": instance_data["instance"],
        "correct_optimization": correct_optimization,
        "options": options,
        "all_optimizations": all_optimizations
    }

# ---------- formatare text întrebare ----------

def format_question_text(csp_data: Dict[str, Any]) -> str:
    """Formatează textul întrebării"""
    problem_name = csp_data["problem_name"]
    instance_desc = csp_data["instance"]["description"]
    
    text = f"Pentru problema {problem_name} și instanța dată:\n"
    text += f"{instance_desc}\n\n"
    text += "Care este cea mai potrivită optimizare pentru algoritmul de backtracking dintre următoarele?\n"
    
    for i, option in enumerate(csp_data["options"], 1):
        text += f"{i}. {option}\n"
    
    return text

# ---------- parsing răspuns ----------

def _parse_answer(answer: str, options: List[str]) -> Optional[str]:
    """
    Parsează răspunsul utilizatorului - versiune flexibilă îmbunătățită.
    Acceptă: numere (1-4), nume complete, abrevieri, variante de scriere, răspunsuri parțiale.
    """
    import re
    
    if not answer or not answer.strip():
        return None
    
    s = answer.strip()
    s_lower = s.lower()
    
    # Normalizează textul: elimină diacritice pentru matching mai flexibil
    def normalize_text(text: str) -> str:
        """Normalizează textul eliminând diacritice și caractere speciale"""
        replacements = {
            'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
            'Ă': 'a', 'Â': 'a', 'Î': 'i', 'Ș': 's', 'Ț': 't'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    s_normalized = normalize_text(s_lower)
    
    # Strategia 1: Caută număr (1, 2, 3, 4) - acceptă și "opțiunea 1", "varianta 2", etc.
    num_patterns = [
        r'\b([1-4])\b',  # Simplu: "1", "2", etc.
        r'(?:opțiunea|optiunea|varianta|varianta|aleg|alegerea)\s*([1-4])',  # "opțiunea 1"
        r'(?:numărul|numarul|număr|numar)\s*([1-4])',  # "numărul 1"
    ]
    for pattern in num_patterns:
        num_match = re.search(pattern, s_normalized)
        if num_match:
            idx = int(num_match.group(1)) - 1
            if 0 <= idx < len(options):
                return options[idx]
    
    # Strategia 2: Caută nume optimizare direct - matching flexibil
    for opt in options:
        opt_lower = opt.lower()
        opt_normalized = normalize_text(opt_lower)
        
        # Verifică potrivire exactă
        if opt_normalized == s_normalized:
            return opt
        
        # Verifică dacă optimizarea e conținută complet în răspuns
        if opt_normalized in s_normalized:
            pattern = r'\b' + re.escape(opt_normalized) + r'\b'
            if re.search(pattern, s_normalized):
                return opt
        
        # Verifică dacă răspunsul e conținut în optimizare (pentru răspunsuri parțiale)
        if s_normalized in opt_normalized and len(s_normalized) >= 3:
            return opt
    
    # Strategia 3: Caută cuvinte cheie și abrevieri extinse
    keywords = {
        "backtracking": ["backtracking", "backtrack", "bt", "backtracking de baza"],
        "forward": ["forward checking", "forward", "fc", "forward check", "verificare inainte"],
        "mrv": ["mrv", "minimum remaining values", "minimum remaining", "min remaining", 
                "minimum remaining value", "valori minime ramase"],
        "ac-3": ["ac-3", "ac3", "arc consistency", "arc consistency 3", "ac 3", 
                 "arc consist", "consistenta arcului", "consistență arc"]
    }
    
    for opt in options:
        opt_lower = opt.lower()
        opt_normalized = normalize_text(opt_lower)
        
        for key, key_list in keywords.items():
            if key in opt_normalized:
                for keyword in key_list:
                    keyword_normalized = normalize_text(keyword.lower())
                    if keyword_normalized in s_normalized:
                        pattern = r'\b' + re.escape(keyword_normalized) + r'\b'
                        if re.search(pattern, s_normalized):
                            return opt
    
    # Strategia 4: Matching parțial bazat pe cuvinte importante
    strategy_words = {}
    for opt in options:
        opt_normalized = normalize_text(opt.lower())
        common_words = {'the', 'and', 'or', 'of', 'for', 'with', 'algorithm', 'method'}
        words = [w for w in re.findall(r'\b\w+\b', opt_normalized) 
                if w not in common_words and len(w) >= 3]
        strategy_words[opt] = words
    
    best_match = None
    best_score = 0
    
    for opt, words in strategy_words.items():
        if not words:
            continue
        matches = sum(1 for word in words if word in s_normalized)
        score = matches / len(words) if words else 0
        if score > best_score and score >= 0.5:
            best_score = score
            best_match = opt
    
    if best_match:
        return best_match
    
    return None

# ---------- evaluare răspuns ----------

def grade_answer(answer: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul utilizatorului"""
    correct_optimization = payload["correct_optimization"]
    options = payload["options"]
    
    parsed = _parse_answer(answer, options)
    
    if parsed is None:
        return {
            "score": 0,
            "feedback": "Nu am putut identifica optimizarea din răspunsul tău. Te rog indică numărul opțiunii (1-4) sau numele optimizării."
        }
    
    if parsed == correct_optimization:
        return {
            "score": 100,
            "feedback": f"Corect! Optimizarea '{correct_optimization}' este cea mai potrivită pentru această problemă."
        }
    else:
        return {
            "score": 0,
            "feedback": f"Greșit. Ai selectat '{parsed}', dar răspunsul corect este '{correct_optimization}'."
        }

# ---------- explicație soluție ----------

def build_explanation(csp_data: Dict[str, Any]) -> str:
    """Construiește explicația soluției"""
    problem_type = csp_data["problem_type"]
    correct_optimization = csp_data["correct_optimization"]
    
    explanations = {
        "Backtracking": "Backtracking de bază explorează sistematic spațiul de soluții, revenind când o constrângere este încălcată. Este simplu și eficient pentru probleme mici.",
        "Forward Checking": "Forward Checking verifică constrângerile înainte de a atribui o valoare, eliminând valori inconsistente din domeniile variabilelor neasignate. Reduce semnificativ spațiul de căutare.",
        "MRV": "Minimum Remaining Values (MRV) alege variabila cu cel mai mic număr de valori disponibile. Această euristică reduce probabilitatea de backtracking și accelerează rezolvarea.",
        "AC-3": "Arc Consistency 3 (AC-3) aplică consistența arcului pentru a elimina valori inconsistente din domenii. Este foarte eficient pentru probleme cu multe constrângeri puternice."
    }
    
    base_explanation = f"Optimizarea corectă este '{correct_optimization}'.\n\n"
    
    if correct_optimization in explanations:
        base_explanation += explanations[correct_optimization]
    else:
        base_explanation += f"'{correct_optimization}' este cea mai potrivită optimizare pentru această instanță CSP."
    
    return base_explanation

# ---------- pachet complet întrebare ----------

def build_question_payload(problem_type: str = "simple", optimization: str = "FC", seed: Optional[int] = None) -> Dict[str, Any]:
    """Construiește pachetul complet de întrebare"""
    csp_data = generate_csp_question(problem_type=problem_type, optimization=optimization, seed=seed)
    qtext = format_question_text(csp_data)
    expl = build_explanation(csp_data)
    
    return {
        "id": f"CSP-{random.randint(100000, 999999)}",
        "problem_type": csp_data["problem_type"],
        "problem_name": csp_data["problem_name"],
        "instance": csp_data["instance"],
        "question_text": qtext,
        "options": csp_data["options"],
        "correct_optimization": csp_data["correct_optimization"],
        "solution": {
            "optimization": csp_data["correct_optimization"],
            "explanation": expl
        }
    }


