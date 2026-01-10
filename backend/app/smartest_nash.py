"""
SmarTest — Nash (strategii pure): generator + evaluator
Dep: numpy
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import random

# ---------- utilități best-responses ----------

def _best_responses_for_player1(A: np.ndarray) -> List[List[int]]:
    rows, cols = A.shape
    br = [[] for _ in range(cols)]
    for j in range(cols):
        col = A[:, j]
        m = col.max()
        br[j] = [i for i in range(rows) if col[i] == m]
    return br

def _best_responses_for_player2(B: np.ndarray) -> List[List[int]]:
    rows, cols = B.shape
    br = [[] for _ in range(rows)]
    for i in range(rows):
        row = B[i, :]
        m = row.max()
        br[i] = [j for j in range(cols) if row[j] == m]
    return br

def find_pure_nash(A: np.ndarray, B: np.ndarray) -> List[Tuple[int,int]]:
    """Returnează liste (i,j) 0-based care sunt răspunsuri mutual-optime."""
    br1 = _best_responses_for_player1(A)
    br2 = _best_responses_for_player2(B)
    rows, cols = A.shape
    out = []
    for i in range(rows):
        for j in range(cols):
            if (i in br1[j]) and (j in br2[i]):
                out.append((i,j))
    return out

# ---------- generare joc ----------

def _rand_labels(prefix: str, n: int) -> List[str]:
    ABC = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if n <= len(ABC):
        return [f"{prefix}{ABC[k]}" for k in range(n)]
    return [f"{prefix}{k+1}" for k in range(n)]

def generate_game(rows: int = 2, cols: int = 2,
                  payoff_min: int = -5, payoff_max: int = 9,
                  ensure: str = "any",
                  seed: Optional[int] = None) -> Dict[str, Any]:
    """
    ensure ∈ {"any","atleast_one","unique","none"}
    """
    assert rows >= 2 and cols >= 2
    if seed is not None:
        random.seed(seed); np.random.seed(seed)

    attempts = 0
    while True:
        attempts += 1
        A = np.random.randint(payoff_min, payoff_max+1, size=(rows, cols))
        B = np.random.randint(payoff_min, payoff_max+1, size=(rows, cols))
        eq = find_pure_nash(A, B)
        ok = (
            (ensure == "any") or
            (ensure == "atleast_one" and len(eq) >= 1) or
            (ensure == "unique" and len(eq) == 1) or
            (ensure == "none" and len(eq) == 0)
        )
        if ok or attempts > 5000:
            break

    return {
        "rows": rows, "cols": cols,
        "row_labels": _rand_labels("R", rows),
        "col_labels": _rand_labels("C", cols),
        "A": A.tolist(), "B": B.tolist()
    }

# ---------- explicație + text întrebare ----------

def _mark_best_responses(A: np.ndarray, B: np.ndarray):
    rows, cols = A.shape
    br1_cols = _best_responses_for_player1(A)  # pe coloane: rândurile maxime pentru J1
    br2_rows = _best_responses_for_player2(B)  # pe rânduri: coloanele maxime pentru J2
    br1_mask = [[False]*cols for _ in range(rows)]
    br2_mask = [[False]*cols for _ in range(rows)]
    for j in range(cols):
        for i in br1_cols[j]:
            br1_mask[i][j] = True
    for i in range(rows):
        for j in br2_rows[i]:
            br2_mask[i][j] = True
    return br1_mask, br2_mask

def build_explanation(A: np.ndarray, B: np.ndarray, rl: List[str], cl: List[str]) -> str:
    eq = find_pure_nash(A,B)
    br1_mask, br2_mask = _mark_best_responses(A,B)
    rows, cols = A.shape
    lines = []
    lines.append("Pași: (1) Marchează BR J1 pe coloane (max în A), (2) Marchează BR J2 pe rânduri (max în B), (3) Intersecțiile sunt NE.")
    lines.append("Marcaje: BR1='*', BR2='^', ambele='*^'\n")
    for i in range(rows):
        row = []
        for j in range(cols):
            mark = "*^" if (br1_mask[i][j] and br2_mask[i][j]) else "*" if br1_mask[i][j] else "^" if br2_mask[i][j] else ""
            row.append(f"{rl[i]}-{cl[j]}: ({A[i,j]},{B[i,j]}){mark}")
        lines.append("  " + " | ".join(row))
    if eq:
        lst = [f"{rl[i]} cu {cl[j]} (adică {i+1},{j+1})" for (i,j) in eq]
        lines.append("\nEchilibre: " + "; ".join(lst) + ".")
    else:
        lines.append("\nNu există echilibru Nash în strategii pure.")
    return "\n".join(lines)

def format_question_text(payload: Dict[str, Any]) -> str:
    A = np.array(payload["A"]); B = np.array(payload["B"])
    rl, cl = payload["row_labels"], payload["col_labels"]
    rows, cols = A.shape
    lines = []
    lines.append("           " + "   ".join([f"{cl[j]:>6}" for j in range(cols)]))
    for i in range(rows):
        cells = "   ".join([f"({A[i,j]:>2},{B[i,j]:>2})" for j in range(cols)])
        lines.append(f"{rl[i]:>6}   " + cells)
    question = [
        "Întrebare (Echilibru Nash în strategii pure)",
        "Jocul (plăți (J1,J2)):",
        "```",
        *lines,
        "```",
        "Cerință: Există un echilibru Nash în strategii pure?",
        " - Dacă DA, indică toate perechile (rând, coloană): ex. 'R1 C2' sau '1 2' sau 'RA, CB'.",
        " - Dacă NU, răspunde 'none'."
    ]
    return "\n".join(question)

# ---------- grading ----------

def _parse_pairs(answer: str, rl: List[str], cl: List[str]):
    """
    Parsează răspunsul utilizatorului pentru echilibru Nash - versiune flexibilă îmbunătățită.
    Acceptă multiple formate: "R1C1", "1,1", "A B", "(1,1)", "r1 c1", "rând 1 coloană 2", etc.
    Acceptă și numere în format text: "unu, doi", "primul, al doilea", etc.
    """
    if not answer:
        return []
    
    s = answer.strip()
    s_lower = s.lower()
    
    # Funcție helper pentru conversia numerelor în text la numere
    def text_to_number(text: str) -> Optional[int]:
        """Convertește numere în format text la numere întregi"""
        text = text.strip().lower()
        number_map = {
            # Română
            "unu": 1, "una": 1, "primul": 1, "prima": 1, "intai": 1, "întâi": 1, "intâi": 1,
            "doi": 2, "doua": 2, "două": 2, "al doilea": 2, "a doua": 2, "doilea": 2,
            "trei": 3, "treia": 3, "al treilea": 3, "a treia": 3, "treilea": 3,
            "patru": 4, "patra": 4, "al patrulea": 4, "a patra": 4, "patrulea": 4,
            "cinci": 5, "cincea": 5, "a cincea": 5, "al cincilea": 5, "cincilea": 5,
            "sase": 6, "șase": 6, "sasea": 6, "șasea": 6, "a șasea": 6, "al șaselea": 6,
            "sapte": 7, "șapte": 7, "saptea": 7, "șaptea": 7, "a șaptea": 7, "al șaptelea": 7,
            "opt": 8, "opta": 8, "a opta": 8, "al optulea": 8, "optulea": 8,
            "noua": 9, "nouă": 9, "a noua": 9, "al nouălea": 9, "nouălea": 9,
            "zece": 10, "zecea": 10, "a zecea": 10, "al zecelea": 10,
            # Engleză
            "one": 1, "first": 1,
            "two": 2, "second": 2,
            "three": 3, "third": 3,
            "four": 4, "fourth": 4,
            "five": 5, "fifth": 5,
            "six": 6, "sixth": 6,
            "seven": 7, "seventh": 7,
            "eight": 8, "eighth": 8,
            "nine": 9, "ninth": 9,
            "ten": 10, "tenth": 10
        }
        return number_map.get(text)
    
    # Verifică dacă utilizatorul spune că nu există echilibru Nash
    
    # Verifică dacă utilizatorul spune că nu există echilibru Nash
    # Versiune extinsă cu mai multe variante
    none_patterns = [
        "none", "no", "no ne", "no nash", "no pure ne", "nu", "nu exista", 
        "nu există", "nu sunt", "nu avem", "lipsă", "lipsa", "niciun", 
        "nici un", "zero", "0", "nimic", "fără", "fara", "nu există echilibru",
        "nu exista echilibru", "nu sunt echilibre", "nu avem echilibru",
        "nu exista nash", "nu există nash", "nu exista echilibre", "nu există echilibre",
        "nu exista echilibru nash", "nu există echilibru nash", "nu exista ne",
        "nu există ne", "nu exista nash pur", "nu există nash pur",
        "lipsa echilibrelor", "lipsă echilibrelor", "fara echilibru", "fără echilibru",
        "nu se gaseste", "nu se găsește", "nu se gasesc", "nu se găsesc",
        "nu gasim", "nu găsim", "nu gasim echilibru", "nu găsim echilibru",
        "absent", "lipseste", "lipsește", "nu e", "nu este", "nu sunt echilibre nash"
    ]
    
    # Verifică potrivire exactă
    if s_lower in none_patterns:
        return None
    
    # Verifică pattern-uri în text
    none_phrases = [
        "nu există", "nu exista", "nu sunt", "niciun echilibru", "nu avem echilibru",
        "nu există nash", "nu exista nash", "nu există ne", "nu exista ne",
        "nu există echilibru", "nu exista echilibru", "nu sunt echilibre",
        "lipsă echilibru", "lipsa echilibru", "fără echilibru", "fara echilibru"
    ]
    if any(phrase in s_lower for phrase in none_phrases):
        return None
    
    import re
    
    # Extrage perechi din formate complexe: "perechile (1,2) și (2,3)" sau "echilibrele R1C1, R2C2"
    # Caută pattern-uri de tipul "(1,2)" sau "[1,2]" sau "R1C1" în întregul text
    complex_pairs = []
    
    # Pattern pentru perechi în paranteze: (1,2), [1,2], {1,2}
    # IMPORTANT: Caută în textul original, înainte de normalizare
    paren_pairs = re.findall(r'[\(\[\{]\s*(\d+)\s*[,:]\s*(\d+)\s*[\)\]\}]', s)
    for pair in paren_pairs:
        try:
            complex_pairs.append((int(pair[0])-1, int(pair[1])-1))
        except:
            pass
    
    # Pattern pentru perechi cu etichete în paranteze: (RA,CB), (RA CB), [RA,CB], etc.
    # Caută pattern-uri precum (RA,CB) sau (RA CB) - etichete de rând și coloană
    rl_map = {x.lower(): i for i, x in enumerate(rl)}
    cl_map = {x.lower(): j for j, x in enumerate(cl)}
    
    # Pattern pentru (RA,CB) sau (RA CB) - etichete separate prin virgulă sau spațiu
    label_paren_pattern = r'[\(\[\{]\s*([A-Za-z]+)\s*[,:\s]+\s*([A-Za-z]+)\s*[\)\]\}]'
    label_paren_matches = re.findall(label_paren_pattern, s)
    for match in label_paren_matches:
        tok1 = match[0].strip().upper()
        tok2 = match[1].strip().upper()
        # Verifică dacă sunt etichete valide (rând și coloană)
        if tok1.lower() in rl_map and tok2.lower() in cl_map:
            complex_pairs.append((rl_map[tok1.lower()], cl_map[tok2.lower()]))
        # Dacă sunt ambele rânduri sau ambele coloane, le ignorăm (vor fi detectate ca invalide mai târziu)
    
    # Pattern pentru R1C1 sau R1 C1
    rc_pairs = re.findall(r'r\s*(\d+)\s*c\s*(\d+)', s_lower)
    for pair in rc_pairs:
        try:
            complex_pairs.append((int(pair[0])-1, int(pair[1])-1))
        except:
            pass
    
    # Elimină duplicate din complex_pairs
    seen = set()
    unique_complex_pairs = []
    for pair in complex_pairs:
        if pair not in seen:
            seen.add(pair)
            unique_complex_pairs.append(pair)
    complex_pairs = unique_complex_pairs
    
    # Dacă am găsit perechi în paranteze (numere sau etichete), le folosim direct
    # și nu mai procesăm prin split(",") pentru a evita probleme când nu există virgulă între perechi
    if complex_pairs:
        return complex_pairs
    
    # Normalizează separatori - extinde lista (doar dacă nu am găsit perechi complexe)
    for sep in [";", "\n", "și", "and", "&", "si", "sau", "or", "|"]:
        s = s.replace(sep, ",")
    
    # IMPORTANT: Înainte de split(","), încercăm să extragem perechi separate doar prin spațiu
    # Pattern pentru perechi în paranteze separate prin spațiu: (1,3) (2,3)
    spaced_paren_pairs = re.findall(r'[\(\[\{]\s*(\d+)\s*[,:]\s*(\d+)\s*[\)\]\}]', s)
    if spaced_paren_pairs and len(spaced_paren_pairs) > 1:
        # Dacă am găsit multiple perechi în paranteze, le procesăm direct
        result = []
        for pair in spaced_paren_pairs:
            try:
                result.append((int(pair[0])-1, int(pair[1])-1))
            except:
                pass
        if result:
            return result
    
    # Împarte în părți pentru procesare ulterioară
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return []

    rl_map = {x.lower(): i for i, x in enumerate(rl)}
    cl_map = {x.lower(): j for j, x in enumerate(cl)}

    out = list(complex_pairs)  # Pornește cu perechile găsite din pattern-uri complexe
    
    for token in parts:
        t = token.strip()
        t_clean = t.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace("-", " ").replace("_", " ").replace(":", " ")
        
        # Skip dacă token-ul a fost deja procesat în complex_pairs
        # Verifică dacă token-ul conține o pereche care a fost deja găsită
        nums_in_token = re.findall(r'\d+', t_clean)
        if len(nums_in_token) >= 2:
            try:
                token_pair = (int(nums_in_token[0])-1, int(nums_in_token[1])-1)
                if token_pair in complex_pairs:
                    continue
            except:
                pass
        
        # Format: "rând 1 coloană 2" sau "rand 1 coloana 2" sau "rândul 1, coloana 2"
        m_rand_col = re.search(r'(?:rând|rand|rândul|randul|row)\s*(\d+).*?(?:coloană|coloană|coloana|col|column)\s*(\d+)', t_clean, re.IGNORECASE)
        if m_rand_col:
            try:
                pair = (int(m_rand_col.group(1))-1, int(m_rand_col.group(2))-1)
                if pair not in out:
                    out.append(pair)
                continue
            except:
                pass
        
        # Format invers: "coloană 2 rând 1"
        m_col_rand = re.search(r'(?:coloană|coloană|coloana|col|column)\s*(\d+).*?(?:rând|rand|rândul|randul|row)\s*(\d+)', t_clean, re.IGNORECASE)
        if m_col_rand:
            try:
                pair = (int(m_col_rand.group(2))-1, int(m_col_rand.group(1))-1)
                if pair not in out:
                    out.append(pair)
                continue
            except:
                pass
        
        # Format: "r1c1" sau "r 1 c 1" sau "R1 C1"
        m = re.search(r"r\s*(\d+)\s*c\s*(\d+)", t_clean, re.IGNORECASE)
        if m:
            try:
                pair = (int(m.group(1))-1, int(m.group(2))-1)
                if pair not in out:
                    out.append(pair)
                continue
            except:
                pass
        
        # Format: "1,1" sau "1 1" sau "1:1" - două numere consecutive
        m2 = re.findall(r"\d+", t_clean)
        if len(m2) >= 2:
            try:
                pair = (int(m2[0])-1, int(m2[1])-1)
                if pair not in out:
                    out.append(pair)
                continue
            except:
                pass
        
        # Format: numere în format text - "unu, doi" sau "primul, al doilea"
        text_number_pattern = r'\b(unu|una|primul|prima|intai|întâi|intâi|doi|doua|două|al doilea|a doua|doilea|trei|treia|al treilea|a treia|treilea|patru|patra|al patrulea|a patra|patrulea|cinci|cincea|a cincea|al cincilea|cincilea|sase|șase|sasea|șasea|a șasea|al șaselea|sapte|șapte|saptea|șaptea|a șaptea|al șaptelea|opt|opta|a opta|al optulea|optulea|noua|nouă|a noua|al nouălea|nouălea|zece|zecea|a zecea|al zecelea|one|first|two|second|three|third|four|fourth|five|fifth|six|sixth|seven|seventh|eight|eighth|nine|ninth|ten|tenth)\b'
        text_numbers = re.findall(text_number_pattern, t_clean, re.IGNORECASE)
        if len(text_numbers) >= 2:
            try:
                num1 = text_to_number(text_numbers[0])
                num2 = text_to_number(text_numbers[1])
                if num1 is not None and num2 is not None:
                    pair = (num1-1, num2-1)
                    if pair not in out:
                        out.append(pair)
                    continue
            except:
                pass
        
        # Format: "A B" sau "A, B" sau "A și B" - etichete de rând și coloană
        toks = t_clean.split()
        if len(toks) >= 2:
            tok1 = toks[0].lower()
            tok2 = toks[1].lower()
            # IMPORTANT: Verifică că primul e rând și al doilea e coloană
            # Dacă ambele sunt rânduri sau ambele sunt coloane, ignoră (e greșit)
            if tok1 in rl_map and tok2 in cl_map:
                pair = (rl_map[tok1], cl_map[tok2])
                if pair not in out:
                    out.append(pair)
                continue
            # Dacă ambele sunt rânduri sau ambele sunt coloane, ignoră (nu e o pereche validă)
            elif (tok1 in rl_map and tok2 in rl_map) or (tok1 in cl_map and tok2 in cl_map):
                # Ignoră - nu e o pereche validă (ex: "RB RB" sau "CA CB")
                continue
        
        # Format: "rând A coloană B" sau "A și B" - căutare în orice ordine
        if len(toks) >= 2:
            found_r = None
            found_c = None
            for tok in toks:
                if tok.lower() in rl_map and found_r is None:
                    found_r = rl_map[tok.lower()]
                if tok.lower() in cl_map and found_c is None:
                    found_c = cl_map[tok.lower()]
            # IMPORTANT: Trebuie să avem exact un rând și o coloană
            if found_r is not None and found_c is not None:
                pair = (found_r, found_c)
                if pair not in out:
                    out.append(pair)
                continue
            # Dacă avem doar rânduri sau doar coloane, ignoră (nu e o pereche validă)
            elif (found_r is not None and found_c is None) or (found_r is None and found_c is not None):
                # Ignoră - nu e o pereche completă validă
                continue
        
        # Format: "strategia R1 cu C2" sau "echilibru la R1 C2"
        m_strategie = re.search(r'(?:strategia|strategie|echilibru|ne|nash)\s*(?:la|la|cu|with)?\s*r\s*(\d+).*?c\s*(\d+)', t_clean, re.IGNORECASE)
        if m_strategie:
            try:
                pair = (int(m_strategie.group(1))-1, int(m_strategie.group(2))-1)
                if pair not in out:
                    out.append(pair)
                continue
            except:
                pass
    
    return out

def grade_answer(answer: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    A = np.array(payload["A"]); B = np.array(payload["B"])
    rl, cl = payload["row_labels"], payload["col_labels"]
    gold = set(find_pure_nash(A,B))
    
    # Verifică dacă există perechi invalide în răspuns (două rânduri sau două coloane)
    invalid_pairs = []
    import re
    s = answer.strip()
    s_lower = s.lower()
    
    # Normalizează separatori
    for sep in [";", "\n", "și", "and", "&", "si", "sau", "or", "|"]:
        s = s.replace(sep, ",")
    
    # IMPORTANT: Extrage perechi în paranteze înainte de split(",") pentru a detecta corect
    # perechile chiar și când nu există virgulă între ele: (1,3) (2,3)
    rl_map = {x.lower(): i for i, x in enumerate(rl)}
    cl_map = {x.lower(): j for j, x in enumerate(cl)}
    
    # Extrage toate perechile cu etichete în paranteze pentru detectarea perechilor invalide
    paren_label_matches = re.findall(r'[\(\[\{]\s*([A-Za-z]+)\s*[,:\s]+\s*([A-Za-z]+)\s*[\)\]\}]', s)
    for match in paren_label_matches:
        tok1 = match[0].strip().upper()
        tok2 = match[1].strip().upper()
        # Verifică dacă ambele sunt rânduri (invalid)
        if tok1.lower() in rl_map and tok2.lower() in rl_map:
            invalid_pairs.append(f"({tok1},{tok2})")
        # Verifică dacă ambele sunt coloane (invalid)
        elif tok1.lower() in cl_map and tok2.lower() in cl_map:
            invalid_pairs.append(f"({tok1},{tok2})")
    
    parts = [p.strip() for p in s.split(",") if p.strip()]
    
    for token in parts:
        t_original = token.strip()
        # Verifică dacă token-ul conține paranteze cu etichete (ex: (RA,CB) sau (CC,CC))
        paren_label_match = re.search(r'[\(\[\{]\s*([A-Za-z]+)\s*[,:\s]+\s*([A-Za-z]+)\s*[\)\]\}]', t_original)
        if paren_label_match:
            tok1 = paren_label_match.group(1).strip().upper()
            tok2 = paren_label_match.group(2).strip().upper()
            # Verifică dacă ambele sunt rânduri (invalid) - inclusiv cazul când sunt identice (RA RA)
            if tok1.lower() in rl_map and tok2.lower() in rl_map:
                invalid_pairs.append(f"({tok1},{tok2})")
            # Verifică dacă ambele sunt coloane (invalid) - inclusiv cazul când sunt identice (CC CC)
            elif tok1.lower() in cl_map and tok2.lower() in cl_map:
                invalid_pairs.append(f"({tok1},{tok2})")
        
        # Continuă cu verificarea normală (fără paranteze)
        t_clean = t_original.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("-", " ").replace("_", " ")
        toks = t_clean.split()
        if len(toks) >= 2:
            tok1 = toks[0].lower()
            tok2 = toks[1].lower()
            # Verifică dacă ambele sunt rânduri (invalid) - inclusiv cazul când sunt identice (RA RA)
            if tok1 in rl_map and tok2 in rl_map:
                invalid_pairs.append(f"{toks[0]} {toks[1]}")
            # Verifică dacă ambele sunt coloane (invalid) - inclusiv cazul când sunt identice (CC CC)
            elif tok1 in cl_map and tok2 in cl_map:
                invalid_pairs.append(f"{toks[0]} {toks[1]}")
    
    parsed = _parse_pairs(answer, rl, cl)

    if parsed is None:  # user a zis "none"
        if len(gold) == 0:
            return {"score": 100, "feedback": "Corect: nu există echilibru Nash pur."}
        return {"score": 0, "feedback": f"Greșit: există {len(gold)} echilibru(rî) Nash pur."}

    # Verifică dacă parsed este o listă validă (nu goală sau None)
    if not parsed or len(parsed) == 0:
        # Dacă nu s-au găsit perechi, dar există perechi invalide, le raportăm
        if invalid_pairs:
            return {"score": 0, "feedback": f"Nu am putut identifica perechi valide în răspunsul tău. Am detectat perechi invalide: '{', '.join(invalid_pairs)}' - trebuie rând-coloană, nu rând-rând sau coloană-coloană."}
        return {"score": 0, "feedback": "Nu am putut identifica perechi valide în răspunsul tău. Te rog folosește formatul: (1,2), R1C1, sau etichete de rând și coloană (ex: RA CB)."}

    user = set(parsed)
    if len(gold) == 0:
        if len(user) == 0:
            feedback = "Corect: nu există echilibru Nash pur."
            if invalid_pairs:
                feedback += f" Notă: '{', '.join(invalid_pairs)}' nu sunt perechi valide (trebuie rând-coloană, nu rând-rând sau coloană-coloană)."
            return {"score": 100, "feedback": feedback}
        feedback = "Greșit: ai indicat perechi, dar nu există niciun NE pur."
        if invalid_pairs:
            feedback += f" De asemenea, '{', '.join(invalid_pairs)}' nu sunt perechi valide (trebuie rând-coloană)."
        return {"score": 0, "feedback": feedback}

    correct = len(user & gold)
    wrong = len(user - gold)
    need = len(gold)
    
    # Dacă are perechi invalide, le tratăm ca perechi greșite
    if invalid_pairs:
        wrong += len(invalid_pairs)
        # Nu le adăugăm la user pentru că nu sunt perechi valide
    
    if correct == need and wrong == 0:
        return {"score": 100, "feedback": "Corect. Ai identificat toate echilibrele Nash."}
    
    partial = max(0.0, (correct/need)*100.0 - 10.0*wrong)
    miss = need - correct
    fb = f"Parțial: {correct}/{need} corecte"
    if wrong: 
        fb += f", {wrong} greșite"
        if invalid_pairs:
            fb += f" (inclusiv perechi invalide: '{', '.join(invalid_pairs)}' - trebuie rând-coloană, nu rând-rând sau coloană-coloană)"
    if miss: fb += f", lipsesc {miss}"
    return {"score": round(partial, 2), "feedback": fb + "."}

# ---------- pachet complet întrebare ----------

def build_question_payload(rows=2, cols=2, ensure="unique", seed=None) -> Dict[str, Any]:
    p = generate_game(rows=rows, cols=cols, ensure=ensure, seed=seed)
    A = np.array(p["A"]); B = np.array(p["B"])
    eq = find_pure_nash(A,B)
    qtext = format_question_text(p)
    expl = build_explanation(A,B,p["row_labels"],p["col_labels"])
    p_out = dict(p)
    p_out["id"] = f"NASH-{random.randint(100000,999999)}"
    p_out["question_text"] = qtext
    p_out["solution"] = {
        "equilibria": [[i+1,j+1] for (i,j) in eq],
        "explanation": expl
    }
    return p_out
