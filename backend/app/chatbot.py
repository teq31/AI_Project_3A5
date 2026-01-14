"""
Simple AI-like chatbot for answering student questions based on theory JSON.
Uses semantic similarity (if available) to retrieve relevant chunks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

import app.smartest_nash as nash
import app.smartest_minmax as minmax
from app.nlp_utils import semantic_similarity, SEMANTIC_SIMILARITY_AVAILABLE, NLP_AVAILABLE


THEORY_DATA_PATH = Path(__file__).parent.parent / "data" / "theory"
_CACHED_DATA: Dict[str, Any] | None = None
_CACHED_FILE: str | None = None
_CACHED_CHUNKS: List[Dict[str, Any]] | None = None
_LAST_PROBLEM: Dict[str, Any] | None = None


def _set_last_problem(problem_type: str, payload: Dict[str, Any]) -> None:
    global _LAST_PROBLEM
    _LAST_PROBLEM = {"type": problem_type, "payload": payload}


def _get_last_problem() -> Optional[Dict[str, Any]]:
    return _LAST_PROBLEM


def _load_theory_data(theory_file: str) -> Dict[str, Any]:
    global _CACHED_DATA, _CACHED_FILE
    if _CACHED_DATA is not None and _CACHED_FILE == theory_file:
        return _CACHED_DATA
    theory_path = THEORY_DATA_PATH / theory_file
    if not theory_path.exists():
        raise FileNotFoundError(f"Theory file not found: {theory_path}")
    with open(theory_path, "r", encoding="utf-8") as f:
        _CACHED_DATA = json.load(f)
    _CACHED_FILE = theory_file
    return _CACHED_DATA


def _add_chunk(chunks: List[Dict[str, Any]], text: str, topic: Dict[str, Any], chunk_type: str, title: str | None = None):
    cleaned = " ".join(str(text).split())
    if len(cleaned) < 20:
        return
    chunks.append({
        "text": cleaned,
        "topic_id": topic.get("topic_id"),
        "topic_name": topic.get("topic_name"),
        "type": chunk_type,
        "title": title or topic.get("topic_name") or chunk_type
    })


def _build_chunks(theory_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    for topic in theory_data.get("topics", []):
        theory = topic.get("theory", {})
        if not isinstance(theory, dict):
            continue

        # Definition
        definition = theory.get("definition")
        if definition:
            _add_chunk(chunks, definition, topic, "definition")

        # Key concepts
        for item in theory.get("key_concepts", []) or []:
            if isinstance(item, dict):
                concept = item.get("concept") or item.get("name")
                parts = [
                    f"Concept: {item.get('concept')}" if item.get("concept") else None,
                    f"Definition: {item.get('definition')}" if item.get("definition") else None,
                    f"Formula: {item.get('formula')}" if item.get("formula") else None,
                    f"Example: {item.get('example')}" if item.get("example") else None,
                ]
                text = " | ".join([p for p in parts if p])
                _add_chunk(chunks, text, topic, "key_concept", title=concept)
            elif isinstance(item, str):
                _add_chunk(chunks, item, topic, "key_concept")

        # Theorems
        for item in theory.get("theorems", []) or []:
            if isinstance(item, dict):
                parts = [
                    f"Theorem: {item.get('name')}" if item.get("name") else None,
                    f"Statement: {item.get('statement')}" if item.get("statement") else None,
                    f"Importance: {item.get('importance')}" if item.get("importance") else None,
                ]
                text = " | ".join([p for p in parts if p])
                _add_chunk(chunks, text, topic, "theorem", title=item.get("name"))

        # Examples
        for item in theory.get("examples", []) or []:
            if isinstance(item, dict):
                parts = [
                    f"Example: {item.get('name')}" if item.get("name") else None,
                    f"Description: {item.get('description')}" if item.get("description") else None,
                    f"Lesson: {item.get('lesson')}" if item.get("lesson") else None,
                ]
                text = " | ".join([p for p in parts if p])
                _add_chunk(chunks, text, topic, "example", title=item.get("name"))

        # Algorithms / steps / tips / mistakes
        for key in ["algorithms", "steps", "optimization_tips", "common_mistakes", "applications", "formulas"]:
            items = theory.get(key, []) or []
            if isinstance(items, list):
                for entry in items:
                    if isinstance(entry, dict):
                        name = entry.get("name") or entry.get("title") or entry.get("concept")
                        parts = [f"{key.replace('_', ' ').title()}: {name}" if name else None]
                        for k, v in entry.items():
                            if k in ["name", "title", "concept"]:
                                continue
                            if isinstance(v, (str, int, float)) and v:
                                parts.append(f"{k.title()}: {v}")
                        text = " | ".join([p for p in parts if p])
                        _add_chunk(chunks, text, topic, key, title=name)
                    elif isinstance(entry, str):
                        _add_chunk(chunks, entry, topic, key)
            elif isinstance(items, str):
                _add_chunk(chunks, items, topic, key)

    return chunks


def _get_chunks(theory_file: str) -> List[Dict[str, Any]]:
    global _CACHED_CHUNKS, _CACHED_FILE
    if _CACHED_CHUNKS is not None and _CACHED_FILE == theory_file:
        return _CACHED_CHUNKS
    data = _load_theory_data(theory_file)
    _CACHED_CHUNKS = _build_chunks(data)
    return _CACHED_CHUNKS


def _parse_nash_matrix(text: str) -> Optional[Dict[str, Any]]:
    pairs = re.findall(r"\(\s*([-+]?\d+)\s*,\s*([-+]?\d+)\s*\)", text)
    if not pairs:
        return None

    dims = re.search(r"(\d+)\s*x\s*(\d+)", text.lower())
    rows = cols = None
    if dims:
        rows = int(dims.group(1))
        cols = int(dims.group(2))

    if rows and cols and rows * cols == len(pairs):
        A = []
        B = []
        idx = 0
        for _ in range(rows):
            row_a = []
            row_b = []
            for _ in range(cols):
                a, b = pairs[idx]
                row_a.append(int(a))
                row_b.append(int(b))
                idx += 1
            A.append(row_a)
            B.append(row_b)
        return {"A": A, "B": B, "rows": rows, "cols": cols}

    # Fallback: infer rows from brackets
    row_splits = re.split(r"\]\s*,\s*\[", text)
    rows_list = []
    for part in row_splits:
        row_pairs = re.findall(r"\(\s*([-+]?\d+)\s*,\s*([-+]?\d+)\s*\)", part)
        if row_pairs:
            rows_list.append(row_pairs)
    if not rows_list:
        return None

    cols = max(len(r) for r in rows_list)
    A = []
    B = []
    for row in rows_list:
        row_a = []
        row_b = []
        for a, b in row:
            row_a.append(int(a))
            row_b.append(int(b))
        if len(row_a) < cols:
            return None
        A.append(row_a)
        B.append(row_b)
    return {"A": A, "B": B, "rows": len(A), "cols": cols}


def _parse_alpha_beta_data(text: str) -> Optional[Dict[str, Any]]:
    lower = text.lower()
    if "alpha" not in lower and "beta" not in lower and "minmax" not in lower:
        return None

    depth_match = re.search(r"depth\s*[:=]\s*(\d+)", lower)
    branch_match = re.search(r"(branching|branch)\s*[:=]\s*(\d+)", lower)
    depth = int(depth_match.group(1)) if depth_match else None
    branching = int(branch_match.group(2)) if branch_match else None

    leaves = []
    bracket = re.search(r"leaves?\s*[:=]\s*\[([^\]]+)\]", lower)
    if bracket:
        nums = re.findall(r"-?\d+", bracket.group(1))
        leaves = [int(n) for n in nums]
    else:
        nums = re.findall(r"-?\d+", lower)
        # remove depth/branching if present
        if depth is not None:
            nums = [n for n in nums if int(n) != depth]
        if branching is not None:
            nums = [n for n in nums if int(n) != branching]
        if nums:
            leaves = [int(n) for n in nums]

    if depth is None or branching is None or not leaves:
        return None

    return {"depth": depth, "branching": branching, "leaves": leaves}


def _format_nash_question(payload: Dict[str, Any]) -> str:
    A = nash.np.array(payload["A"])
    B = nash.np.array(payload["B"])
    rl, cl = payload["row_labels"], payload["col_labels"]
    rows, cols = A.shape

    lines = []
    lines.append("Problema Nash (strategii pure)")
    lines.append("Matrice plăți (J1,J2):")
    lines.append("        " + "   ".join([f"{cl[j]:>4}" for j in range(cols)]))
    for i in range(rows):
        cells = "   ".join([f"({A[i,j]:>2},{B[i,j]:>2})" for j in range(cols)])
        lines.append(f"{rl[i]:>4}   " + cells)
    lines.append("")
    lines.append("Cerință: indică toate echilibrele Nash în strategii pure.")
    lines.append("Răspuns: ex. 'R1 C2' / '1 2' / 'none'")
    return "\n".join(lines)


def _format_minmax_question(question_text: str) -> str:
    if "Structura arborelui:" in question_text:
        question_text = question_text.split("Structura arborelui:")[0].rstrip()
    question_text = question_text.replace("```", "").strip()
    return question_text


def _format_minmax_table(payload: Dict[str, Any]) -> str:
    metadata = payload.get("metadata")
    if not metadata:
        return "Tabelul nu este disponibil pentru această problemă."
    return minmax.format_tree_table(metadata)


def _rule_based_response(question: str) -> Optional[Dict[str, Any]]:
    q = question.strip().lower()
    words = re.findall(r"\w+", q)

    greetings = {"salut", "buna", "bună", "hello", "hi", "hey", "ceau", "cSalut"}
    if len(words) <= 3 and any(w in greetings for w in words):
        return {
            "answer": "Salut! Sunt aici să te ajut cu întrebări despre teoria din curs. Întreabă-mă ceva din subiecte precum Nash, MinMax, CSP sau euristici.",
            "confidence": 1.0,
            "sources": [],
            "method": "Rule-based"
        }

    if "ce faci" in q or "cum esti" in q or "cum ești" in q:
        return {
            "answer": "Sunt bine, mulțumesc! Spune-mi cu ce te pot ajuta din teoria AI.",
            "confidence": 1.0,
            "sources": [],
            "method": "Rule-based"
        }

    if "scopul tau" in q or "scopul tău" in q or "care e scopul" in q:
        return {
            "answer": "Scopul meu este să explic concepte din teoria AI și să te ajut la întrebări despre Nash, MinMax, CSP, euristici și altele, folosind doar teoria proiectului.",
            "confidence": 1.0,
            "sources": [],
            "method": "Rule-based"
        }

    if "multumesc" in q or "mulțumesc" in q or "mersi" in q:
        return {
            "answer": "Cu plăcere! Dacă mai ai întrebări, sunt aici.",
            "confidence": 1.0,
            "sources": [],
            "method": "Rule-based"
        }

    if "arata tabelul" in q or "arată tabelul" in q or "detalii arbore" in q or "detalii arbore" in q or "tabel minmax" in q:
        last_problem = _get_last_problem()
        if last_problem and last_problem["type"] == "minmax":
            table = _format_minmax_table(last_problem["payload"])
            return {
                "answer": "Detalii arbore (tabel):\n" + table,
                "confidence": 1.0,
                "sources": [],
                "method": "Rule-based"
            }
        return {
            "answer": "Nu am o problemă MinMax activă. Cere mai întâi o problemă Alpha-Beta/MinMax.",
            "confidence": 0.7,
            "sources": [],
            "method": "Rule-based"
        }

    if "matricea payoff nash" in q or "payoff nash" in q or "matricea nash" in q:
        parsed = _parse_nash_matrix(question)
        if not parsed:
            return {
                "answer": "Am înțeles că vrei Nash. Te rog trimite matricea în format: [(a,b)] pe fiecare celulă.",
                "confidence": 0.7,
                "sources": [],
                "method": "Rule-based"
            }

        A = parsed["A"]
        B = parsed["B"]
        eq = nash.find_pure_nash(nash.np.array(A), nash.np.array(B))
        if eq:
            eq_text = ", ".join([f"({i+1},{j+1})" for i, j in eq])
            answer = f"Echilibre Nash (strategii pure): {eq_text}."
        else:
            answer = "Nu există echilibru Nash în strategii pure."

        explanation = nash.build_explanation(nash.np.array(A), nash.np.array(B),
                                             [f"R{i+1}" for i in range(parsed['rows'])],
                                             [f"C{j+1}" for j in range(parsed['cols'])])
        if len(explanation) > 700:
            explanation = explanation[:700].rstrip() + "..."

        return {
            "answer": answer + "\n\n" + explanation,
            "confidence": 0.9,
            "sources": [],
            "method": "Rule-based"
        }

    if "matrice numerică" in q or "matrice numerica" in q:
        return {
            "answer": "Am primit matricea numerică. Spune ce problemă vrei să rezolv (Nash, MinMax/Alpha-Beta, CSP etc.).",
            "confidence": 0.7,
            "sources": [],
            "method": "Rule-based"
        }

    ab_data = _parse_alpha_beta_data(question)
    if ab_data:
        depth = ab_data["depth"]
        branching = ab_data["branching"]
        leaves = ab_data["leaves"]
        expected = branching ** depth
        if len(leaves) != expected:
            return {
                "answer": f"Pentru depth={depth} și branching={branching} sunt necesare {expected} frunze. Ai trimis {len(leaves)}.",
                "confidence": 0.7,
                "sources": [],
                "method": "Rule-based"
            }

        root, metadata = minmax.generate_game_tree(depth=depth, branching_factor=branching, value_range=(0, 0))

        leaf_nodes = []
        def collect_leaves(node):
            if node.type == "LEAF":
                leaf_nodes.append(node)
                return
            for child in node.children:
                collect_leaves(child)
        collect_leaves(root)

        for node, value in zip(leaf_nodes, leaves):
            node.value = value
        for node in metadata["nodes"]:
            if node["type"] == "LEAF":
                idx = next((i for i, leaf in enumerate(leaf_nodes) if leaf.id == node["id"]), None)
                if idx is not None:
                    node["value"] = leaves[idx]

        solution = minmax.solve_tree(root)
        explanation = minmax.build_explanation(root, metadata, solution)
        if len(explanation) > 700:
            explanation = explanation[:700].rstrip() + "..."

        return {
            "answer": f"Valoare rădăcină: {solution['root_value']} | Frunze vizitate: {solution['visited_count']}\n\n{explanation}",
            "confidence": 0.9,
            "sources": [],
            "method": "Rule-based"
        }

    if "da-mi" in q or "genereaza" in q or "generează" in q:
        if "nash" in q:
            payload = nash.build_question_payload(rows=2, cols=2, ensure="unique")
            _set_last_problem("nash", payload)
            return {
                "answer": _format_nash_question(payload) + "\n\nTrimite răspunsul tău.",
                "confidence": 1.0,
                "sources": [],
                "method": "Rule-based"
            }
        if "alpha beta" in q or "alpha-beta" in q or "minmax" in q or "min max" in q:
            payload = minmax.build_question_payload(depth=3, branching_factor=2)
            _set_last_problem("minmax", payload)
            return {
                "answer": _format_minmax_question(payload["question_text"]) + "\n\nTrimite răspunsul tău (ex: '5 4' sau 'valoare=5, frunze=4').",
                "confidence": 1.0,
                "sources": [],
                "method": "Rule-based"
            }

    verbs = ["calculeaza", "calculează", "determina", "determină", "rezolva", "rezolvă", "gaseste", "găsește", "afla", "află", "da-mi", "dă-mi", "problema", "exercitiu", "exercițiu"]

    if any(v in q for v in verbs):
        if "nash" in q or "echilibru nash" in q:
            return {
                "answer": (
                    "Pentru a calcula un echilibru Nash, am nevoie de matricea de payoff "
                    "(strategiile și valorile pentru ambii jucători). Trimite matricea.\n"
                    "Pași minimi după ce o am:\n"
                    "1) Identific best responses pentru fiecare jucător.\n"
                    "2) Găsesc intersecțiile best responses.\n"
                    "3) Verific dacă există echilibre Nash pure."
                ),
                "confidence": 0.8,
                "sources": [],
                "method": "Rule-based"
            }
        if "alpha beta" in q or "alpha-beta" in q or "minmax" in q or "min max" in q:
            return {
                "answer": (
                    "Pentru Alpha-Beta/MinMax am nevoie de arborele de joc: valorile frunzelor, "
                    "ordinea copiilor și cine maximizează/minimizează la fiecare nivel.\n"
                    "Pași minimi după ce le am:\n"
                    "1) Aplic MinMax pe frunze urcând la rădăcină.\n"
                    "2) Aplic tăieri Alpha-Beta când e posibil.\n"
                    "3) Dau valoarea finală și mutarea optimă."
                ),
                "confidence": 0.8,
                "sources": [],
                "method": "Rule-based"
            }
        if "csp" in q or "backtracking" in q:
            return {
                "answer": (
                    "Pentru o problemă CSP am nevoie de: variabile, domeniile lor și constrângerile dintre ele. "
                    "Trimite aceste date.\n"
                    "Pași minimi după ce le am:\n"
                    "1) Aleg variabila (ex: MRV).\n"
                    "2) Aplic backtracking cu verificare (ex: Forward Checking / AC-3).\n"
                    "3) Construiesc soluția sau declar imposibil."
                ),
                "confidence": 0.8,
                "sources": [],
                "method": "Rule-based"
            }
        if "strategie" in q or "strategia" in q or "problema 1" in q:
            return {
                "answer": (
                    "Pentru identificarea strategiei (problema 1) am nevoie de matricea jocului "
                    "sau descrierea strategiilor și payoff-urilor.\n"
                    "Pași minimi după ce le am:\n"
                    "1) Analizez opțiunile pentru fiecare jucător.\n"
                    "2) Identific strategii dominante (dacă există).\n"
                    "3) Concluzionez strategia recomandată."
                ),
                "confidence": 0.8,
                "sources": [],
                "method": "Rule-based"
            }

    return None


def answer_question(question: str, topic_id: Optional[str] = None, theory_file: str = "example_theory.json", max_sources: int = 3) -> Dict[str, Any]:
    if not question or not question.strip():
        return {
            "answer": "Te rog scrie o întrebare.",
            "confidence": 0.0,
            "sources": [],
            "method": "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")
        }

    rule_based = _rule_based_response(question)
    if rule_based:
        return rule_based

    last_problem = _get_last_problem()
    if last_problem:
        answer_text = question.strip().lower()
        is_answer_like = any(ch.isdigit() for ch in answer_text) or "none" in answer_text or "nu există" in answer_text or "nu exista" in answer_text
        if is_answer_like:
            if last_problem["type"] == "nash":
                result = nash.grade_answer(question, last_problem["payload"])
                return {
                    "answer": f"Evaluare Nash: {result.get('feedback', '')}\nScor: {result.get('score', 0)}%",
                    "confidence": result.get("score", 0) / 100.0,
                    "sources": [],
                    "method": "Rule-based"
                }
            if last_problem["type"] == "minmax":
                result = minmax.grade_answer(question, last_problem["payload"])
                return {
                    "answer": f"Evaluare MinMax: {result.get('feedback', '')}\nScor: {result.get('score', 0)}%",
                    "confidence": result.get("score", 0) / 100.0,
                    "sources": [],
                    "method": "Rule-based"
                }

    chunks = _get_chunks(theory_file)
    if topic_id:
        chunks = [c for c in chunks if c.get("topic_id") == topic_id]

    scored: List[Dict[str, Any]] = []
    for chunk in chunks:
        score = semantic_similarity(question, chunk["text"])
        scored.append({**chunk, "score": float(score)})

    scored.sort(key=lambda c: c["score"], reverse=True)
    top = scored[:max_sources]
    best_score = top[0]["score"] if top else 0.0

    method = "NLP Semantic Similarity" if SEMANTIC_SIMILARITY_AVAILABLE else ("Fuzzy Matching" if NLP_AVAILABLE else "Fallback")

    if best_score < 0.35:
        suggestions = []
        for item in top:
            label = item.get("topic_name") or item.get("topic_id") or "topic"
            if label not in suggestions:
                suggestions.append(label)
        suggestion_text = ""
        if suggestions:
            suggestion_text = " Sugestii: " + ", ".join(suggestions[:3]) + "."
        return {
            "answer": "Nu sunt sigur. Încearcă să reformulezi întrebarea sau să alegi un topic specific." + suggestion_text,
            "confidence": best_score,
            "sources": top,
            "method": method
        }

    # Build a concise answer from the best chunk
    best = top[0]
    answer_text = best["text"]
    if len(answer_text) > 600:
        answer_text = answer_text[:600].rstrip() + "..."

    return {
        "answer": answer_text,
        "confidence": best_score,
        "sources": top,
        "method": method
    }

