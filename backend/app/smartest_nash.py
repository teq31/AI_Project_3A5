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
    s = (answer or "").strip().lower()
    if s in {"none","no","no ne","no nash","no pure ne","nu","nu exista","nu există"}:
        return None
    for sep in [";", "\n"]:
        s = s.replace(sep, ",")
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return []

    rl_map = {x.lower(): i for i, x in enumerate(rl)}
    cl_map = {x.lower(): j for j, x in enumerate(cl)}

    out = []
    import re
    for token in parts:
        t = token.replace("(", "").replace(")", "").replace("-", " ")
        m = re.search(r"r\s*(\d+)\s*c\s*(\d+)", t)  # r#c#
        if m:
            out.append((int(m.group(1))-1, int(m.group(2))-1)); continue
        m2 = re.findall(r"\d+", t)
        if len(m2) >= 2:
            out.append((int(m2[0])-1, int(m2[1])-1)); continue
        toks = t.split()
        if len(toks) == 2 and toks[0] in rl_map and toks[1] in cl_map:
            out.append((rl_map[toks[0]], cl_map[toks[1]]))
    return out

def grade_answer(answer: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    A = np.array(payload["A"]); B = np.array(payload["B"])
    rl, cl = payload["row_labels"], payload["col_labels"]
    gold = set(find_pure_nash(A,B))
    parsed = _parse_pairs(answer, rl, cl)

    if parsed is None:  # user a zis "none"
        if len(gold) == 0:
            return {"score": 100, "feedback": "Corect: nu există echilibru Nash pur."}
        return {"score": 0, "feedback": f"Greșit: există {len(gold)} echilibru(rî) Nash pur."}

    user = set(parsed)
    if len(gold) == 0:
        if len(user) == 0:
            return {"score": 100, "feedback": "Corect: nu există echilibru Nash pur."}
        return {"score": 0, "feedback": "Greșit: ai indicat perechi, dar nu există niciun NE pur."}

    correct = len(user & gold)
    wrong = len(user - gold)
    need = len(gold)
    if correct == need and wrong == 0:
        return {"score": 100, "feedback": "Corect. Ai identificat toate echilibrele Nash."}
    partial = max(0.0, (correct/need)*100.0 - 10.0*wrong)
    miss = need - correct
    fb = f"Parțial: {correct}/{need} corecte"
    if wrong: fb += f", {wrong} greșite"
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
