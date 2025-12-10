"""
SmarTest — MinMax cu Alpha-Beta: generator + evaluator
Generează arbori de joc și evaluează răspunsuri despre valoarea rădăcinii și nodurile frunze vizitate
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
import random

# ---------- structură arbore ----------

class Node:
    """Nod într-un arbore de joc"""
    def __init__(self, node_id: str, node_type: str, value: Optional[int] = None):
        self.id = node_id
        self.type = node_type  # "MAX", "MIN", sau "LEAF"
        self.value = value  # pentru frunze
        self.children: List[Node] = []
        self.parent: Optional[Node] = None

# ---------- generare arbore ----------

def generate_game_tree(depth: int = 3, branching_factor: int = 2, 
                       value_range: Tuple[int, int] = (-10, 10),
                       seed: Optional[int] = None) -> Tuple[Node, Dict[str, Any]]:
    """
    Generează un arbore de joc binar sau cu branching_factor.
    Returnează rădăcina și metadata despre arbore.
    """
    if seed is not None:
        random.seed(seed)
    
    node_counter = [0]  # pentru ID-uri unice
    
    def create_node(node_type: str, current_depth: int) -> Node:
        node_id = f"N{node_counter[0]}"
        node_counter[0] += 1
        
        if current_depth >= depth:
            # frunză
            value = random.randint(value_range[0], value_range[1])
            node = Node(node_id, "LEAF", value)
        else:
            # nod intern
            node = Node(node_id, node_type, None)
            next_type = "MIN" if node_type == "MAX" else "MAX"
            for _ in range(branching_factor):
                child = create_node(next_type, current_depth + 1)
                child.parent = node
                node.children.append(child)
        
        return node
    
    root = create_node("MAX", 0)
    
    # colectează toate nodurile pentru reprezentare
    all_nodes = []
    leaf_nodes = []
    
    def collect_nodes(node: Node, level: int = 0):
        all_nodes.append({
            "id": node.id,
            "type": node.type,
            "value": node.value,
            "level": level,
            "children_ids": [c.id for c in node.children]
        })
        if node.type == "LEAF":
            leaf_nodes.append(node.id)
        for child in node.children:
            collect_nodes(child, level + 1)
    
    collect_nodes(root)
    
    return root, {
        "depth": depth,
        "branching_factor": branching_factor,
        "nodes": all_nodes,
        "leaf_ids": leaf_nodes,
        "root_id": root.id
    }

# ---------- algoritm MinMax cu Alpha-Beta ----------

def minmax_alpha_beta(node: Node, alpha: float, beta: float, visited_leaves: List[str]) -> int:
    """
    Algoritm MinMax cu optimizare Alpha-Beta.
    Returnează valoarea nodului și actualizează lista de frunze vizitate.
    """
    if node.type == "LEAF":
        visited_leaves.append(node.id)
        return node.value
    
    if node.type == "MAX":
        value = float('-inf')
        for child in node.children:
            child_value = minmax_alpha_beta(child, alpha, beta, visited_leaves)
            value = max(value, child_value)
            alpha = max(alpha, value)
            if beta <= alpha:
                break  # Alpha-Beta pruning
        return int(value)
    
    else:  # MIN
        value = float('inf')
        for child in node.children:
            child_value = minmax_alpha_beta(child, alpha, beta, visited_leaves)
            value = min(value, child_value)
            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha-Beta pruning
        return int(value)

def solve_tree(root: Node) -> Dict[str, Any]:
    """Rezolvă arborele și returnează valoarea rădăcinii și frunzele vizitate"""
    visited_leaves = []
    root_value = minmax_alpha_beta(root, float('-inf'), float('inf'), visited_leaves)
    return {
        "root_value": root_value,
        "visited_leaves": visited_leaves,
        "visited_count": len(visited_leaves)
    }

# ---------- formatare arbore pentru afișare ----------

def format_tree_ascii(root: Node, metadata: Dict[str, Any]) -> str:
    """Formatează arborele ca text ASCII pentru afișare"""
    lines = []
    lines.append("Arbore de joc:")
    
    def format_node(node: Node, prefix: str = "", is_last: bool = True):
        if node.type == "LEAF":
            marker = "└── " if is_last else "├── "
            lines.append(f"{prefix}{marker}{node.id} ({node.type}): {node.value}")
        else:
            marker = "└── " if is_last else "├── "
            lines.append(f"{prefix}{marker}{node.id} ({node.type})")
            new_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(node.children):
                format_node(child, new_prefix, i == len(node.children) - 1)
    
    format_node(root)
    return "\n".join(lines)

def format_tree_table(metadata: Dict[str, Any]) -> str:
    """Formatează arborele ca tabel pentru afișare mai clară"""
    lines = []
    lines.append("Structura arborelui:")
    lines.append("ID    | Tip  | Valoare | Părinte | Copii")
    lines.append("-" * 50)
    
    nodes_dict = {n["id"]: n for n in metadata["nodes"]}
    
    for node in metadata["nodes"]:
        node_id = node["id"]
        node_type = node["type"]
        value = str(node["value"]) if node["value"] is not None else "-"
        parent_id = "-"
        for n in metadata["nodes"]:
            if node_id in n["children_ids"]:
                parent_id = n["id"]
                break
        children = ", ".join(node["children_ids"]) if node["children_ids"] else "-"
        lines.append(f"{node_id:5} | {node_type:4} | {value:7} | {parent_id:7} | {children}")
    
    return "\n".join(lines)

# ---------- formatare întrebare ----------

def format_question_text(root: Node, metadata: Dict[str, Any]) -> str:
    """Formatează textul întrebării"""
    tree_ascii = format_tree_ascii(root, metadata)
    tree_table = format_tree_table(metadata)
    
    question = [
        "Întrebare (MinMax cu optimizare Alpha-Beta)",
        "",
        "Pentru arborele dat, care va fi valoarea din rădăcină și câte noduri frunze vor fi vizitate",
        "în cazul aplicării strategiei MinMax cu optimizarea Alpha-Beta?",
        "",
        tree_ascii,
        "",
        tree_table,
        "",
        "Cerință:",
        "1. Care va fi valoarea din rădăcină?",
        "2. Câte noduri frunze vor fi vizitate?",
        "",
        "Răspuns: Format 'valoare număr_frunze' (ex: '5 4' sau 'valoare=5, frunze=4')"
    ]
    return "\n".join(question)

# ---------- grading ----------

def _parse_answer(answer: str) -> Dict[str, Optional[int]]:
    """
    Parsează răspunsul utilizatorului - versiune flexibilă care acceptă propoziții naturale.
    Extrage valoarea din rădăcină și numărul de frunze vizitate din text.
    Returnează dict cu 'value' și 'leaves' (poate fi None dacă nu e găsit).
    """
    if not answer:
        return {"value": None, "leaves": None}
    
    import re
    s = answer.strip()
    s_lower = s.lower()
    
    # Strategia 1: Căutare după cuvinte cheie specifice pentru valoare (prioritară)
    value_patterns = [
        r'(?:valoare|value|rădăcină|root|rezultat)\s*(?:din\s*)?(?:rădăcină|root)?\s*[=:]\s*(-?\d+)',
        r'(?:valoare|value)\s*(?:este|e|are|în\s*numar|in\s*numar)\s*(?:de|este|e)?\s*(-?\d+)',
        r'(?:rădăcină|root|radacina|radăcina)\s*(?:are|este|e|va\s*fi)\s*(-?\d+)',
        r'(?:valoarea|value)\s*(?:din\s*)?(?:rădăcină|root)\s*(?:este|e|are|va\s*fi)\s*(-?\d+)',
        r'(?:valoarea|value)\s*(?:este|e|are)\s*(?:în\s*numar|in\s*numar|egală|egala)\s*(?:de|cu)?\s*(-?\d+)',
        r'(?:iar\s*)?(?:rădăcină|root|radacina|radăcina)\s*(?:este|e|are|va\s*fi)\s*(-?\d+)',  # "iar radacina este -1"
        r'(?:iar\s*)?(?:valoarea|value)\s*(?:este|e|are)\s*(-?\d+)',  # "iar valoarea este -1"
    ]
    
    # Strategia 2: Căutare după cuvinte cheie specifice pentru frunze (prioritară)
    # IMPORTANT: Acceptă și numere negative pentru a detecta erorile utilizatorului
    leaves_patterns = [
        r'(?:număr|number|numar|count)\s*(?:de\s*)?(?:noduri\s*)?(?:frunze|leaves|noduri\s*frunze|leaf\s*nodes)\s*(?:vizitate|visited)?\s*(?:este|e|are|sunt|au\s*fost|vor\s*fi)\s*(-?\d+)',  # "Numarul de noduri frunze vizitate este 4" sau "este -8"
        r'(?:frunze|leaves|noduri\s*frunze|leaf\s*nodes)\s*(?:frunze|vizitate|visited)?\s*[=:]\s*(-?\d+)',
        r'(?:frunze|leaves|noduri)\s*(?:vizitate|visited|au\s*fost|sunt|vor\s*fi)\s*(?:vizitate|visited)?\s*[=:]\s*(-?\d+)',
        r'(?:număr|number|numar|count)\s*(?:de\s*)?(?:frunze|leaves|noduri\s*frunze)\s*(?:vizitate|visited)?\s*[=:]\s*(-?\d+)',
        r'(-?\d+)\s*(?:frunze|leaves|noduri\s*frunze)\s*(?:vizitate|visited|au\s*fost|sunt)',
        r'(?:vizitate|visited)\s*(?:au\s*fost|sunt|vor\s*fi)?\s*(-?\d+)\s*(?:frunze|leaves|noduri)',
        r'(?:frunze|leaves)\s*(?:sunt|au\s*fost|vor\s*fi)\s*(?:în\s*numar|in\s*numar)\s*(?:de|egal)?\s*(-?\d+)',
        r'(?:câte|cate|how\s*many)\s*(?:frunze|leaves|noduri)\s*(?:frunze|vizitate)?\s*(?:au\s*fost|sunt|vor\s*fi)?\s*(-?\d+)',
        r'(?:iar\s*)?(?:număr|number|numar)\s*(?:de\s*)?(?:frunze|leaves|noduri)\s*(?:frunze|vizitate)?\s*(?:este|e|sunt)\s*(-?\d+)',  # "iar numarul de frunze este 4"
    ]
    
    value = None
    leaves = None
    
    # Caută valoarea (prioritară - căutăm după cuvinte cheie specifice)
    # Folosim findall pentru a găsi toate potrivirile și să le procesăm în ordine
    for pattern in value_patterns:
        matches = re.finditer(pattern, s_lower)
        for match in matches:
            try:
                candidate_value = int(match.group(1))
                # Verifică dacă numărul nu e deja folosit ca frunze
                # IMPORTANT: Nu suprascrie dacă deja am găsit o valoare prin pattern specific
                if (leaves is None or candidate_value != leaves) and value is None:
                    value = candidate_value
                    break
            except:
                continue
        if value is not None:
            break
    
    # Caută numărul de frunze (prioritară - căutăm după cuvinte cheie specifice)
    # Folosim findall pentru a găsi toate potrivirile și să le procesăm în ordine
    for pattern in leaves_patterns:
        matches = re.finditer(pattern, s_lower)
        for match in matches:
            try:
                candidate_leaves = int(match.group(1))
                # Verifică dacă numărul nu e deja folosit ca valoare
                # IMPORTANT: Nu suprascrie dacă deja am găsit frunze prin pattern specific
                if (value is None or candidate_leaves != value) and leaves is None:
                    leaves = candidate_leaves
                    break
            except:
                continue
        if leaves is not None:
            break
    
    # Strategia 3: Dacă nu am găsit prin cuvinte cheie, încercăm să extragem numerele
    # dar doar dacă nu sunt în context de "noduri vizitate" sau alte informații
    if value is None or leaves is None:
        # Extragem toate numerele din text
        all_numbers = re.findall(r'-?\d+', s)
        
        # Filtrăm numerele care sunt în context de "noduri vizitate" sau "nod N"
        # (acestea nu sunt răspunsurile căutate)
        filtered_numbers = []
        for num_str in all_numbers:
            num = int(num_str)
            # Verifică contextul în jurul numărului
            num_pos = s.find(num_str)
            if num_pos != -1:
                # Extrage contextul (30 caractere înainte și după pentru mai multă precizie)
                start = max(0, num_pos - 30)
                end = min(len(s), num_pos + len(num_str) + 30)
                context = s_lower[start:end]
                
                # Dacă numărul e în context de "nod N", "N0", "N1", etc., îl ignorăm
                if re.search(r'\bn\s*\d+|\bnod\s*\d+|\bnode\s*\d+', context):
                    continue
                
                # Dacă numărul e în context de "noduri vizitate" fără "frunze", îl ignorăm
                # (dacă e doar "noduri vizitate" fără "frunze", probabil se referă la noduri interne)
                if re.search(r'noduri\s*vizitate|nodes\s*visited', context) and not re.search(r'frunze|leaves|număr|number|numar', context):
                    continue
                
                filtered_numbers.append(num)
            else:
                filtered_numbers.append(num)
        
        # Dacă am găsit numere filtrate, le folosim
        if len(filtered_numbers) >= 2:
            try:
                # Dacă avem 2 numere și unul e negativ, probabil negativul e valoarea
                # și pozitivul e frunze
                negative_nums = [n for n in filtered_numbers if n < 0]
                positive_nums = [n for n in filtered_numbers if n > 0]
                
                if negative_nums and positive_nums:
                    if value is None:
                        value = negative_nums[0]  # Primul negativ e probabil valoarea
                    if leaves is None:
                        leaves = positive_nums[0]  # Primul pozitiv e probabil frunze
                else:
                    # Dacă nu avem negativ, trebuie să verificăm contextul pentru fiecare număr
                    # pentru a le asocia corect bazat pe context, nu pe ordine
                    for num in filtered_numbers:
                        if value is not None and leaves is not None:
                            break
                        
                        num_str = str(num)
                        num_pos = s.find(num_str)
                        if num_pos != -1:
                            start = max(0, num_pos - 40)
                            end = min(len(s), num_pos + len(num_str) + 40)
                            context = s_lower[start:end]
                            
                            # Dacă numărul e în context de "radacina" sau "valoare", e valoare
                            if value is None and re.search(r'radacina|radăcina|rădăcină|root|valoare|value', context):
                                value = num
                                continue
                            
                            # Dacă numărul e în context de "frunze" sau "noduri frunze", e frunze
                            if leaves is None and re.search(r'frunze|leaves|noduri\s*frunze|număr|number|numar', context):
                                leaves = num
                                continue
                    
                    # Dacă încă nu am asociat, folosim prima logică (primul = valoare, al doilea = frunze)
                    # dar doar dacă nu am găsit prin context
                    if value is None and len(filtered_numbers) > 0:
                        value = filtered_numbers[0]
                    if leaves is None and len(filtered_numbers) > 1:
                        # Evită să folosim același număr pentru ambele
                        for num in filtered_numbers[1:]:
                            if num != value:
                                leaves = num
                                break
            except:
                pass
        elif len(filtered_numbers) == 1:
            # Dacă avem un singur număr, încercăm să-l asociem
            # IMPORTANT: Nu suprascrie valorile deja găsite prin pattern-uri specifice
            num = filtered_numbers[0]
            if value is None and leaves is None:
                # Verifică contextul pentru a decide
                num_pos = s.find(str(num))
                if num_pos != -1:
                    start = max(0, num_pos - 40)
                    end = min(len(s), num_pos + len(str(num)) + 40)
                    context = s_lower[start:end]
                    
                    # Dacă e în context de "frunze" sau "noduri frunze", e frunze
                    if re.search(r'frunze|leaves|noduri\s*frunze|număr|number|numar', context):
                        leaves = num
                    # Dacă e în context de "radacina" sau "valoare", e valoare
                    elif re.search(r'radacina|radăcina|rădăcină|root|valoare|value', context):
                        value = num
                    # Dacă numărul e negativ și nu am găsit context clar, probabil e valoare
                    elif num < 0:
                        value = num
                    # Dacă e pozitiv și mic (< 20), default e valoare
                    elif num < 20:
                        value = num
                    else:
                        # Număr mare pozitiv, probabil e frunze (deși rare)
                        leaves = num
                else:
                    # Default: dacă e negativ, e valoare; altfel, e valoare dacă e mic
                    if num < 0:
                        value = num
                    elif num < 20:
                        value = num
                    else:
                        leaves = num
    
    # Strategia 4: Format explicit "valoare=5, frunze=4" sau "5 4"
    if value is None or leaves is None:
        # Format: "valoare=5, frunze=4" sau "value=5, leaves=4"
        value_match = re.search(r'(?:valoare|value)\s*[=:]\s*(-?\d+)', s_lower)
        leaves_match = re.search(r'(?:frunze|leaves|noduri\s*frunze)\s*[=:]\s*(\d+)', s_lower)
        
        if value_match:
            try:
                value = int(value_match.group(1))
            except:
                pass
        if leaves_match:
            try:
                leaves = int(leaves_match.group(1))
            except:
                pass
    
    # Returnează dict cu valorile găsite (poate fi None)
    return {"value": value, "leaves": leaves}

def _extract_mentioned_nodes(answer: str) -> List[str]:
    """
    Extrage nodurile menționate în răspuns (ex: N2, N3, N5, N6).
    Returnează lista de ID-uri de noduri găsite.
    """
    if not answer:
        return []
    
    import re
    # Caută pattern-uri de tipul "N0", "N1", "N2", etc. (case insensitive)
    # Poate fi "N2", "n2", "nod N2", "node N2", etc.
    node_patterns = [
        r'\bN\s*(\d+)',  # N2, N3, etc.
        r'\bnod\s*N\s*(\d+)',  # nod N2
        r'\bnode\s*N\s*(\d+)',  # node N2
    ]
    
    found_nodes = []
    for pattern in node_patterns:
        matches = re.findall(pattern, answer, re.IGNORECASE)
        for match in matches:
            node_id = f"N{match}"
            if node_id not in found_nodes:
                found_nodes.append(node_id)
    
    return found_nodes

def grade_answer(answer: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluează răspunsul utilizatorului.
    Acceptă răspunsuri parțiale - acordă 50% pentru fiecare parte corectă.
    Caz special: dacă utilizatorul enumeră nodurile frunze vizitate corect (chiar dacă nu dă numărul exact),
    acordă 75% (50% valoare + 25% pentru identificarea corectă a nodurilor).
    """
    gold_value = payload["solution"]["root_value"]
    gold_leaves = payload["solution"]["visited_count"]
    gold_visited_leaves = set(payload["solution"]["visited_leaves"])  # Set pentru comparație ușoară
    
    parsed = _parse_answer(answer)
    
    # Extrage nodurile menționate în răspuns
    mentioned_nodes = _extract_mentioned_nodes(answer)
    
    # Verifică dacă am găsit cel puțin o valoare sau noduri menționate
    if parsed["value"] is None and parsed["leaves"] is None and not mentioned_nodes:
        return {
            "score": 0,
            "feedback": "Nu am putut extrage răspunsul din textul tău. Te rog menționează valoarea din rădăcină și/sau numărul de frunze vizitate. Exemple: 'Valoarea este 5 și au fost vizitate 4 frunze', 'Frunzele sunt 4, valoarea este 5', '5 4', etc."
        }
    
    user_value = parsed["value"]
    user_leaves = parsed["leaves"]
    
    # Verifică corectitudinea fiecărei părți (dacă a fost furnizată)
    value_correct = False
    leaves_correct = False
    nodes_correct = False
    
    if user_value is not None:
        value_correct = (user_value == gold_value)
    if user_leaves is not None:
        leaves_correct = (user_leaves == gold_leaves)
    
    # Verifică dacă nodurile enumerate corespund cu soluția
    if mentioned_nodes:
        user_nodes_set = set(mentioned_nodes)
        # Verifică dacă toate nodurile enumerate sunt corecte și dacă sunt toate nodurile corecte
        if user_nodes_set == gold_visited_leaves:
            nodes_correct = True
    
    # Calculează scorul
    score = 0.0
    feedback_parts = []
    
    if user_value is not None:
        if value_correct:
            score += 50.0
            feedback_parts.append(f"Valoarea rădăcinii este corectă ({gold_value})")
        else:
            feedback_parts.append(f"Valoarea rădăcinii este greșită. Ai răspuns {user_value}, dar corect este {gold_value}")
    else:
        feedback_parts.append(f"Nu ai furnizat valoarea rădăcinii. Corect este {gold_value}")
    
    # Caz special: dacă valoarea e corectă și nodurile sunt enumerate corect, dar nu a dat numărul exact
    # IMPORTANT: Verifică înainte de a procesa numărul de frunze pentru a putea returna direct 75%
    if value_correct and nodes_correct and user_leaves is None and mentioned_nodes:
        score = 75.0
        feedback_parts.append(f"Ai identificat corect nodurile frunze vizitate ({', '.join(sorted(mentioned_nodes))}), dar nu ai furnizat numărul exact de frunze. Corect este {gold_leaves} frunze vizitate")
        return {
            "score": round(score, 2),
            "feedback": ". ".join(feedback_parts) + "."
        }
    
    # Verificare normală pentru numărul de frunze
    if user_leaves is not None:
        # Verifică dacă numărul de frunze este negativ (nu are sens logic)
        if user_leaves < 0:
            feedback_parts.append(f"Numărul de frunze vizitate nu poate fi negativ. Ai răspuns {user_leaves}, dar corect este {gold_leaves} (numărul de frunze trebuie să fie pozitiv)")
        elif leaves_correct:
            score += 50.0
            feedback_parts.append(f"Numărul de frunze vizitate este corect ({gold_leaves})")
        else:
            feedback_parts.append(f"Numărul de frunze vizitate este greșit. Ai răspuns {user_leaves}, dar corect este {gold_leaves}")
    else:
        if mentioned_nodes:
            # Dacă a enumerat noduri dar nu sunt corecte
            if not nodes_correct:
                feedback_parts.append(f"Nodurile frunze enumerate nu sunt corecte. Corecte sunt: {', '.join(sorted(gold_visited_leaves))}")
            # Dacă a enumerat noduri corecte dar nu a dat numărul (deja tratat mai sus)
        else:
            feedback_parts.append(f"Nu ai furnizat numărul de frunze vizitate. Corect este {gold_leaves}")
    
    # Mesaj special pentru răspuns complet corect
    if value_correct and leaves_correct:
        return {
            "score": 100,
            "feedback": f"Corect! Valoarea rădăcinii este {gold_value} și {gold_leaves} noduri frunze au fost vizitate."
        }
    
    return {
        "score": round(score, 2),
        "feedback": ". ".join(feedback_parts) + "."
    }

# ---------- explicație ----------

def build_explanation(root: Node, metadata: Dict[str, Any], solution: Dict[str, Any]) -> str:
    """Construiește explicația soluției"""
    lines = []
    lines.append("Soluție:")
    lines.append("")
    lines.append(f"Valoarea din rădăcină: {solution['root_value']}")
    lines.append(f"Număr de noduri frunze vizitate: {solution['visited_count']}")
    lines.append("")
    lines.append("Noduri frunze vizitate:")
    for leaf_id in solution['visited_leaves']:
        # găsește valoarea frunzei
        for node in metadata["nodes"]:
            if node["id"] == leaf_id:
                lines.append(f"  - {leaf_id}: valoare {node['value']}")
                break
    lines.append("")
    lines.append("Notă: Algoritmul Alpha-Beta prună ramurile care nu pot îmbunătăți valoarea curentă, ")
    lines.append("reducând astfel numărul de noduri evaluate față de MinMax standard.")
    
    return "\n".join(lines)

# ---------- pachet complet întrebare ----------

def build_question_payload(depth: int = 3, branching_factor: int = 2,
                          value_range: Tuple[int, int] = (-10, 10),
                          seed: Optional[int] = None) -> Dict[str, Any]:
    """Construiește pachetul complet de întrebare"""
    root, metadata = generate_game_tree(
        depth=depth,
        branching_factor=branching_factor,
        value_range=value_range,
        seed=seed
    )
    
    solution = solve_tree(root)
    qtext = format_question_text(root, metadata)
    expl = build_explanation(root, metadata, solution)
    
    # Convertim arborele în format serializabil
    def node_to_dict(node: Node) -> Dict[str, Any]:
        return {
            "id": node.id,
            "type": node.type,
            "value": node.value,
            "children": [node_to_dict(c) for c in node.children]
        }
    
    return {
        "id": f"MINMAX-{random.randint(100000, 999999)}",
        "depth": depth,
        "branching_factor": branching_factor,
        "value_range": list(value_range),
        "tree": node_to_dict(root),
        "metadata": metadata,
        "question_text": qtext,
        "solution": {
            "root_value": solution["root_value"],
            "visited_leaves": solution["visited_leaves"],
            "visited_count": solution["visited_count"],
            "explanation": expl
        }
    }

