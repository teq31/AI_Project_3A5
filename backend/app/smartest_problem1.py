"""
SmarTest — Problema 1: Identificare problemă și strategie de rezolvare
Probleme: n-queens, generalised Hanoi, graph coloring, knight's tour
Strategii: Backtracking, Greedy, Hill Climbing, Simulated Annealing, Genetic Algorithm, etc.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
import random

# ---------- definiții probleme ----------

PROBLEMS = {
    "n-queens": {
        "name": "n-queens",
        "description": "Problema reginelor pe o tablă de șah",
        "strategies": ["Backtracking", "Genetic Algorithm", "Simulated Annealing", "Constraint Satisfaction"],
        "default_strategy": "Backtracking"
    },
    "hanoi": {
        "name": "generalised Hanoi",
        "description": "Problema turnurilor din Hanoi generalizată",
        "strategies": ["Recursive Backtracking", "Iterative Deepening", "A* Search", "Dynamic Programming"],
        "default_strategy": "Recursive Backtracking"
    },
    "graph_coloring": {
        "name": "graph coloring",
        "description": "Problema colorării grafurilor",
        "strategies": ["Backtracking", "Greedy Coloring", "Welsh-Powell", "Constraint Satisfaction"],
        "default_strategy": "Backtracking"
    },
    "knight_tour": {
        "name": "knight's tour",
        "description": "Problema turului calului pe tablă de șah",
        "strategies": ["Backtracking", "Warnsdorff's Heuristic", "Divide and Conquer", "Neural Network"],
        "default_strategy": "Backtracking"
    }
}

# ---------- generare instanță problemă ----------

def generate_n_queens_instance(n: int = 4, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o instanță pentru n-queens"""
    if seed is not None:
        random.seed(seed)
    
    # Alege strategia corectă în funcție de dimensiunea problemei
    if n <= 6:
        # Pentru probleme mici, Backtracking este eficient și garantează soluția optimă
        correct_strategy = "Backtracking"
    elif n == 7:
        # Pentru probleme medii, Constraint Satisfaction cu propagare este eficient
        correct_strategy = "Constraint Satisfaction"
    else:  # n >= 8
        # Pentru probleme mari, algoritmi metaheuristici sunt mai rapizi
        # Simulated Annealing este de obicei mai bun decât Genetic Algorithm pentru n-queens
        correct_strategy = "Simulated Annealing"
    
    return {
        "problem_type": "n-queens",
        "instance": {
            "n": n,
            "description": f"Plasează {n} regine pe o tablă de {n}x{n} astfel încât să nu se atace reciproc."
        },
        "correct_strategy": correct_strategy
    }

def generate_hanoi_instance(disks: int = 3, pegs: int = 3, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o instanță pentru Hanoi"""
    if seed is not None:
        random.seed(seed)
    
    # Alege strategia corectă în funcție de numărul de discuri
    if disks <= 4:
        # Pentru puține discuri, Recursive Backtracking este natural și eficient
        correct_strategy = "Recursive Backtracking"
    elif disks == 5:
        # Pentru probleme medii, Iterative Deepening găsește soluția optimă eficient
        correct_strategy = "Iterative Deepening"
    else:  # disks >= 6
        # Pentru multe discuri, Dynamic Programming evită recalcularea subproblemelor
        correct_strategy = "Dynamic Programming"
    
    return {
        "problem_type": "hanoi",
        "instance": {
            "disks": disks,
            "pegs": pegs,
            "description": f"Mută {disks} discuri de pe tija inițială pe tija finală folosind {pegs} tije, respectând regulile clasice."
        },
        "correct_strategy": correct_strategy
    }

def generate_graph_coloring_instance(vertices: int = 5, edges: List[Tuple[int, int]] = None, colors: int = 3, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o instanță pentru graph coloring"""
    if seed is not None:
        random.seed(seed)
    
    if edges is None:
        # Generează un graf simplu
        edges = []
        for i in range(vertices):
            for j in range(i + 1, min(i + 3, vertices)):
                if random.random() > 0.3:  # 70% probabilitate de muchie
                    edges.append((i, j))
    
    num_edges = len(edges)
    edge_density = num_edges / (vertices * (vertices - 1) / 2) if vertices > 1 else 0
    
    # Alege strategia corectă în funcție de dimensiunea și densitatea grafului
    if vertices <= 5 and edge_density > 0.5:
        # Grafuri mici și dense: Backtracking garantează soluția optimă
        correct_strategy = "Backtracking"
    elif vertices <= 5:
        # Grafuri mici și rare: Constraint Satisfaction este eficient
        correct_strategy = "Constraint Satisfaction"
    elif edge_density < 0.4:
        # Grafuri mari și rare: Greedy Coloring este rapid și eficient
        correct_strategy = "Greedy Coloring"
    else:
        # Grafuri mari și dense: Welsh-Powell oferă un compromis bun
        correct_strategy = "Welsh-Powell"
    
    return {
        "problem_type": "graph_coloring",
        "instance": {
            "vertices": vertices,
            "edges": edges,
            "colors": colors,
            "description": f"Colorează un graf cu {vertices} noduri și {num_edges} muchii folosind cel mult {colors} culori, astfel încât nodurile adiacente să aibă culori diferite."
        },
        "correct_strategy": correct_strategy
    }

def generate_knight_tour_instance(size: int = 5, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o instanță pentru knight's tour"""
    if seed is not None:
        random.seed(seed)
    
    start_pos = (random.randint(0, size-1), random.randint(0, size-1))
    
    # Alege strategia corectă în funcție de dimensiunea tablei
    if size == 5:
        # Pentru table mici, Backtracking găsește soluția completă eficient
        correct_strategy = "Backtracking"
    elif size == 6:
        # Pentru table medii, Warnsdorff's Heuristic este foarte eficient și rapid
        correct_strategy = "Warnsdorff's Heuristic"
    else:  # size >= 7
        # Pentru table mari, Warnsdorff's Heuristic rămâne cea mai bună alegere
        correct_strategy = "Warnsdorff's Heuristic"
    
    return {
        "problem_type": "knight_tour",
        "instance": {
            "board_size": size,
            "start_position": start_pos,
            "description": f"Găsește un tur complet al calului pe o tablă de {size}x{size}, începând din poziția {start_pos}."
        },
        "correct_strategy": correct_strategy
    }

# ---------- generare întrebare ----------

def generate_problem_question(problem_type: Optional[str] = None, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generează o întrebare despre o problemă și strategia sa"""
    if seed is not None:
        random.seed(seed)
    
    if problem_type is None:
        problem_type = random.choice(list(PROBLEMS.keys()))
    
    problem_info = PROBLEMS[problem_type]
    
    # Generează instanța
    if problem_type == "n-queens":
        instance_data = generate_n_queens_instance(n=random.randint(4, 8), seed=seed)
    elif problem_type == "hanoi":
        instance_data = generate_hanoi_instance(disks=random.randint(3, 5), pegs=3, seed=seed)
    elif problem_type == "graph_coloring":
        instance_data = generate_graph_coloring_instance(
            vertices=random.randint(4, 6),
            colors=random.randint(3, 4),
            seed=seed
        )
    elif problem_type == "knight_tour":
        instance_data = generate_knight_tour_instance(size=random.randint(5, 6), seed=seed)
    else:
        raise ValueError(f"Problem type {problem_type} not supported")
    
    correct_strategy = instance_data["correct_strategy"]
    
    # Generează opțiuni (corectă + 3 greșite)
    all_strategies = problem_info["strategies"]
    wrong_strategies = [s for s in all_strategies if s != correct_strategy]
    options = [correct_strategy] + random.sample(wrong_strategies, min(3, len(wrong_strategies)))
    random.shuffle(options)
    
    return {
        "problem_type": problem_type,
        "problem_name": problem_info["name"],
        "instance": instance_data["instance"],
        "correct_strategy": correct_strategy,
        "options": options,
        "all_strategies": all_strategies
    }

# ---------- formatare text întrebare ----------

def format_question_text(problem_data: Dict[str, Any]) -> str:
    """Formatează textul întrebării"""
    problem_name = problem_data["problem_name"]
    instance_desc = problem_data["instance"]["description"]
    
    text = f"Pentru problema {problem_name} și instanța dată:\n"
    text += f"{instance_desc}\n\n"
    text += "Care este cea mai potrivită strategie de rezolvare dintre următoarele?\n"
    
    for i, option in enumerate(problem_data["options"], 1):
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
    
    # Strategia 2: Caută nume strategie direct - matching flexibil
    # Normalizează opțiunile pentru comparație
    normalized_options = {normalize_text(opt.lower()): opt for opt in options}
    
    for strategy in options:
        strategy_lower = strategy.lower()
        strategy_normalized = normalize_text(strategy_lower)
        
        # Verifică potrivire exactă (case-insensitive, fără diacritice)
        if strategy_normalized == s_normalized:
            return strategy
        
        # Verifică dacă strategia e conținută complet în răspuns
        if strategy_normalized in s_normalized:
            # Verifică că nu e doar o parte dintr-un cuvânt
            pattern = r'\b' + re.escape(strategy_normalized) + r'\b'
            if re.search(pattern, s_normalized):
                return strategy
        
        # Verifică dacă răspunsul e conținut în strategie (pentru răspunsuri parțiale)
        if s_normalized in strategy_normalized and len(s_normalized) >= 3:
            return strategy
    
    # Strategia 3: Caută cuvinte cheie și abrevieri extinse
    keywords = {
        "backtracking": ["backtracking", "backtrack", "bt"],
        "genetic": ["genetic", "genetic algorithm", "ga", "genetic algo"],
        "simulated": ["simulated annealing", "simulated", "annealing", "sa", "simulated anneal"],
        "greedy": ["greedy", "greedy coloring", "greedy col"],
        "welsh": ["welsh-powell", "welsh", "powell", "welsh powell", "wp"],
        "warnsdorff": ["warnsdorff", "warnsdorff's", "warnsdorffs", "warnsdorff heuristic"],
        "recursive": ["recursive", "recursive backtracking", "recursive bt", "rec bt"],
        "iterative": ["iterative deepening", "iterative", "iterative deep", "id", "ids"],
        "a*": ["a*", "a star", "astar", "a-star", "a star search"],
        "dynamic": ["dynamic programming", "dp", "dynamic prog", "memoization"],
        "constraint": ["constraint satisfaction", "csp", "constraint", "constraint sat"],
        "divide": ["divide and conquer", "divide", "divide conquer", "d&c", "d and c"],
        "neural": ["neural network", "neural", "nn", "neural net", "deep learning"]
    }
    
    # Caută potriviri bazate pe cuvinte cheie
    for strategy in options:
        strategy_lower = strategy.lower()
        strategy_normalized = normalize_text(strategy_lower)
        
        for key, key_list in keywords.items():
            if key in strategy_normalized:
                for keyword in key_list:
                    keyword_normalized = normalize_text(keyword.lower())
                    # Verifică dacă keyword-ul e în răspuns
                    if keyword_normalized in s_normalized:
                        # Verifică că nu e doar o parte dintr-un cuvânt
                        pattern = r'\b' + re.escape(keyword_normalized) + r'\b'
                        if re.search(pattern, s_normalized):
                            return strategy
    
    # Strategia 4: Matching parțial bazat pe cuvinte importante
    # Extrage cuvintele importante din fiecare strategie
    strategy_words = {}
    for strategy in options:
        strategy_normalized = normalize_text(strategy.lower())
        # Elimină cuvinte comune
        common_words = {'the', 'and', 'or', 'of', 'for', 'with', 'algorithm', 'method', 'search'}
        words = [w for w in re.findall(r'\b\w+\b', strategy_normalized) 
                if w not in common_words and len(w) >= 3]
        strategy_words[strategy] = words
    
    # Verifică dacă majoritatea cuvintelor importante dintr-o strategie sunt în răspuns
    best_match = None
    best_score = 0
    
    for strategy, words in strategy_words.items():
        if not words:
            continue
        matches = sum(1 for word in words if word in s_normalized)
        score = matches / len(words) if words else 0
        if score > best_score and score >= 0.5:  # Cel puțin 50% din cuvinte
            best_score = score
            best_match = strategy
    
    if best_match:
        return best_match
    
    return None

# ---------- evaluare răspuns ----------

def grade_answer(answer: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluează răspunsul utilizatorului"""
    correct_strategy = payload["correct_strategy"]
    options = payload["options"]
    
    parsed = _parse_answer(answer, options)
    
    if parsed is None:
        return {
            "score": 0,
            "feedback": "Nu am putut identifica strategia din răspunsul tău. Te rog indică numărul opțiunii (1-4) sau numele strategiei."
        }
    
    if parsed == correct_strategy:
        return {
            "score": 100,
            "feedback": f"Corect! Strategia '{correct_strategy}' este cea mai potrivită pentru această problemă."
        }
    else:
        return {
            "score": 0,
            "feedback": f"Greșit. Ai selectat '{parsed}', dar răspunsul corect este '{correct_strategy}'."
        }

# ---------- explicație soluție ----------

def build_explanation(problem_data: Dict[str, Any]) -> str:
    """Construiește explicația soluției"""
    problem_type = problem_data["problem_type"]
    correct_strategy = problem_data["correct_strategy"]
    instance = problem_data["instance"]
    
    explanations = {
        "n-queens": {
            "Backtracking": "Backtracking este ideal pentru n-queens deoarece permite explorarea sistematică a tuturor configurațiilor posibile, eliminând ramurile care nu pot conduce la soluție. Este eficient pentru probleme cu constrângeri puternice.",
            "Genetic Algorithm": "Genetic Algorithm este potrivit pentru n-queens deoarece poate explora spațiul de soluții folosind operații de crossover și mutație. Este util pentru probleme mari unde backtracking-ul ar fi prea lent, oferind soluții aproximative bune.",
            "Simulated Annealing": "Simulated Annealing este eficient pentru n-queens deoarece permite explorarea spațiul de soluții evitând minimul local. Prin reducerea treptată a 'temperaturii', converge către o soluție bună, fiind util pentru instanțe mari.",
            "Constraint Satisfaction": "Constraint Satisfaction este potrivit pentru n-queens deoarece problema poate fi modelată ca un CSP cu constrângeri clare (reginele nu se atacă). Algoritmii CSP pot folosi propagarea constrângerilor pentru a reduce spațiul de căutare."
        },
        "hanoi": {
            "Recursive Backtracking": "Recursive Backtracking este potrivit pentru Hanoi deoarece problema are o structură recursivă naturală. Fiecare mutare poate fi văzută ca o subproblemă mai mică, iar backtracking-ul permite explorarea tuturor secvențelor posibile de mutări.",
            "Iterative Deepening": "Iterative Deepening este eficient pentru Hanoi deoarece combină avantajele BFS și DFS. Explorează progresiv adâncimi mai mari, garantând găsirea soluției optime în timp liniar cu adâncimea soluției.",
            "A* Search": "A* Search este potrivit pentru Hanoi când există o euristică bună (ex: distanța până la starea țintă). Folosește o funcție de evaluare f(n) = g(n) + h(n) pentru a găsi soluția optimă eficient.",
            "Dynamic Programming": "Dynamic Programming este util pentru Hanoi când trebuie să rezolvi multiple instanțe similare. Memoizează soluțiile pentru subprobleme, evitând recalcularea, fiind eficient pentru probleme cu suprapuneri de subprobleme."
        },
        "graph_coloring": {
            "Backtracking": "Backtracking este eficient pentru graph coloring deoarece permite explorarea sistematică a tuturor atribuirilor de culori, eliminând ramurile care violează constrângerile. Este deosebit de util când numărul de culori este limitat.",
            "Greedy Coloring": "Greedy Coloring este rapid și simplu pentru graph coloring. Colorează nodurile secvențial, alocând prima culoare disponibilă. Deși nu garantează numărul minim de culori, este foarte eficient pentru grafuri mari.",
            "Welsh-Powell": "Welsh-Powell este o variantă greedy optimizată pentru graph coloring. Ordonează nodurile descrescător după grad, apoi colorează greedy. Această ordonare îmbunătățește calitatea soluției comparativ cu greedy standard.",
            "Constraint Satisfaction": "Constraint Satisfaction este ideal pentru graph coloring deoarece problema poate fi modelată direct ca CSP. Algoritmii CSP pot folosi forward checking, arc consistency și alte tehnici pentru a reduce eficient spațiul de căutare."
        },
        "knight_tour": {
            "Backtracking": "Backtracking este potrivit pentru knight's tour deoarece permite explorarea tuturor căilor posibile ale calului, revenind la poziții anterioare când o cale nu mai poate continua. Este eficient pentru găsirea unei soluții complete.",
            "Warnsdorff's Heuristic": "Warnsdorff's Heuristic este foarte eficient pentru knight's tour. La fiecare pas, alege mutarea către pătratul cu cel mai mic număr de mutări posibile viitoare. Această euristică reduce dramatic spațiul de căutare și găsește soluții rapid.",
            "Divide and Conquer": "Divide and Conquer poate fi aplicat pentru knight's tour prin împărțirea tablei în regiuni mai mici, rezolvarea turului pentru fiecare regiune, apoi conectarea soluțiilor. Este util pentru table mari unde backtracking-ul ar fi prea lent.",
            "Neural Network": "Neural Network poate fi folosit pentru knight's tour ca o abordare de învățare. Poate învăța pattern-uri din soluții existente și generaliza pentru table de dimensiuni diferite. Este util pentru probleme complexe cu multe variabile."
        }
    }
    
    base_explanation = f"Strategia corectă este '{correct_strategy}'.\n\n"
    
    if problem_type in explanations and correct_strategy in explanations[problem_type]:
        base_explanation += explanations[problem_type][correct_strategy]
    else:
        base_explanation += f"'{correct_strategy}' este cea mai potrivită strategie pentru această instanță a problemei {problem_data['problem_name']}."
    
    return base_explanation

# ---------- pachet complet întrebare ----------

def build_question_payload(problem_type: Optional[str] = None, seed: Optional[int] = None) -> Dict[str, Any]:
    """Construiește pachetul complet de întrebare"""
    problem_data = generate_problem_question(problem_type=problem_type, seed=seed)
    qtext = format_question_text(problem_data)
    expl = build_explanation(problem_data)
    
    return {
        "id": f"PROB1-{random.randint(100000, 999999)}",
        "problem_type": problem_data["problem_type"],
        "problem_name": problem_data["problem_name"],
        "instance": problem_data["instance"],
        "question_text": qtext,
        "options": problem_data["options"],
        "correct_strategy": problem_data["correct_strategy"],
        "solution": {
            "strategy": problem_data["correct_strategy"],
            "explanation": expl
        }
    }


