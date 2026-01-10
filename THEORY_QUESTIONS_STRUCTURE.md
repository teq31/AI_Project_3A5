# 📚 Structură pentru Teorie și Generare Întrebări din Cursuri

## 🎯 Concept General

Sistemul va permite:
1. **Stocarea teoriei** din cursuri într-un format structurat
2. **Generarea automată de întrebări** bazate pe teoria
3. **Integrare** cu sistemul existent de quiz

---

## 📋 Format Structură Teorie

### Opțiunea 1: JSON (Recomandat pentru flexibilitate)

```json
{
  "course": "Inteligenta Artificiala",
  "topics": [
    {
      "topic_id": "nash_equilibrium",
      "topic_name": "Echilibru Nash",
      "difficulty": "medium",
      "theory": {
        "definition": "Echilibru Nash este o situație în teoria jocurilor unde niciun jucător nu poate îmbunătăți rezultatul său prin schimbarea unilaterală a strategiei.",
        "key_concepts": [
          "strategie dominantă",
          "best response",
          "echilibru în strategii pure",
          "echilibru în strategii mixte"
        ],
        "formulas": [
          {
            "name": "Best Response pentru Jucător 1",
            "formula": "BR₁(s₂) = argmax_{s₁} u₁(s₁, s₂)",
            "description": "Cea mai bună răspuns pentru jucătorul 1 dată strategia jucătorului 2"
          }
        ],
        "examples": [
          {
            "title": "Dilema prizonierului",
            "description": "Clasic exemplu de joc cu echilibru Nash",
            "matrix": {
              "player1": ["Confesă", "Nu confesa"],
              "player2": ["Confesă", "Nu confesa"],
              "payoffs": [[[-5, -5], [0, -10]], [[-10, 0], [-1, -1]]]
            }
          }
        ],
        "common_mistakes": [
          "Confundarea echilibrului Nash cu optimul Pareto",
          "Căutarea doar a echilibrelor în strategii pure"
        ],
        "related_topics": ["game_theory", "dominant_strategy"]
      },
      "question_templates": [
        {
          "type": "multiple_choice",
          "template": "Care este definiția corectă a echilibrului Nash?",
          "correct_answer": "Situație în care niciun jucător nu poate îmbunătăți rezultatul prin schimbare unilaterală",
          "distractors": [
            "Situație în care ambii jucători obțin câștig maxim",
            "Situație în care un jucător domină complet",
            "Situație în care jocul se termină rapid"
          ],
          "explanation": "Echilibru Nash presupune stabilitate, nu optimizare globală."
        },
        {
          "type": "true_false",
          "template": "Echilibru Nash garantează optimul Pareto.",
          "correct_answer": false,
          "explanation": "Echilibru Nash nu garantează optimul Pareto. În dilema prizonierului, echilibru Nash este (Confesă, Confesă) dar nu este optim Pareto."
        },
        {
          "type": "fill_blank",
          "template": "Best Response pentru jucătorul 1 este: BR₁(s₂) = _____",
          "correct_answers": [
            "argmax_{s₁} u₁(s₁, s₂)",
            "argmax u1(s1, s2)",
            "maximul utilității jucătorului 1"
          ],
          "explanation": "Best Response este strategia care maximizează utilitatea jucătorului 1."
        },
        {
          "type": "short_answer",
          "template": "Explică diferența între echilibru Nash în strategii pure și strategii mixte.",
          "correct_answer_keywords": ["pure", "mixte", "probabilități", "determinist"],
          "explanation": "Strategii pure sunt deterministe, iar strategii mixte folosesc distribuții de probabilitate."
        }
      ]
    },
    {
      "topic_id": "minmax_algorithm",
      "topic_name": "Algoritm MinMax",
      "difficulty": "hard",
      "theory": {
        "definition": "Algoritm MinMax este o tehnică de decizie pentru jocuri cu doi jucători cu informație completă.",
        "key_concepts": [
          "noduri MAX și MIN",
          "valoare minimax",
          "alpha-beta pruning",
          "adâncime limitată"
        ],
        "algorithms": [
          {
            "name": "MinMax de bază",
            "pseudocode": "function minmax(node, depth, maximizing):\n  if depth == 0 or terminal(node):\n    return evaluate(node)\n  if maximizing:\n    value = -∞\n    for child in children(node):\n      value = max(value, minmax(child, depth-1, False))\n    return value\n  else:\n    value = +∞\n    for child in children(node):\n      value = min(value, minmax(child, depth-1, True))\n    return value",
            "complexity": "O(b^d) unde b = branching factor, d = depth"
          }
        ],
        "optimizations": [
          {
            "name": "Alpha-Beta Pruning",
            "description": "Elimină ramuri care nu pot influența decizia finală",
            "improvement": "Reduce complexitatea la O(b^(d/2)) în cel mai bun caz"
          }
        ]
      },
      "question_templates": [
        {
          "type": "multiple_choice",
          "template": "Care este complexitatea algoritmului MinMax pentru un arbore cu branching factor b și adâncime d?",
          "correct_answer": "O(b^d)",
          "distractors": ["O(b*d)", "O(b+d)", "O(log b * d)"],
          "explanation": "MinMax explorează toate nodurile până la adâncimea d."
        }
      ]
    }
  ]
}
```

---

## 🎲 Tipuri de Întrebări Suportate

### 1. **Multiple Choice** (cu 1 sau mai multe răspunsuri corecte)
```json
{
  "type": "multiple_choice",
  "single_answer": true,  // sau false pentru multiple
  "question": "Care dintre următoarele sunt caracteristici ale echilibrului Nash?",
  "options": [
    {"text": "Niciun jucător nu poate îmbunătăți rezultatul unilateral", "correct": true},
    {"text": "Garantează optimul Pareto", "correct": false},
    {"text": "Există întotdeauna", "correct": false},
    {"text": "Este unic", "correct": false}
  ],
  "explanation": "Echilibru Nash nu garantează optimul Pareto și nu există întotdeauna."
}
```

### 2. **True/False**
```json
{
  "type": "true_false",
  "question": "Alpha-Beta pruning reduce întotdeauna numărul de noduri evaluate.",
  "correct_answer": true,
  "explanation": "Alpha-Beta pruning elimină ramuri care nu pot influența decizia, reducând nodurile evaluate."
}
```

### 3. **Fill in the Blank / Completare**
```json
{
  "type": "fill_blank",
  "question": "Best Response pentru jucătorul 1 este: BR₁(s₂) = _____",
  "correct_answers": [
    "argmax_{s₁} u₁(s₁, s₂)",
    "argmax u1(s1, s2)",
    "maximul utilității jucătorului 1"
  ],
  "case_sensitive": false,
  "explanation": "Best Response maximizează utilitatea jucătorului 1."
}
```

### 4. **Short Answer / Răspuns scurt**
```json
{
  "type": "short_answer",
  "question": "Explică diferența între echilibru Nash în strategii pure și strategii mixte.",
  "correct_keywords": ["pure", "mixte", "probabilități", "determinist"],
  "min_keywords": 2,  // minim 2 cuvinte cheie trebuie să fie prezente
  "explanation": "Strategii pure sunt deterministe, iar strategii mixte folosesc distribuții de probabilitate."
}
```

### 5. **Matching / Potrivire**
```json
{
  "type": "matching",
  "question": "Potrivește conceptul cu definiția corectă:",
  "pairs": [
    {"left": "Echilibru Nash", "right": "Niciun jucător nu poate îmbunătăți rezultatul unilateral", "correct": true},
    {"left": "Strategie dominantă", "right": "Cea mai bună strategie indiferent de alegerea adversarului", "correct": true},
    {"left": "Optimum Pareto", "right": "Situație în care nu se poate îmbunătăți un jucător fără a înrăutăți altul", "correct": true}
  ],
  "distractors": [
    "Situație în care jocul se termină rapid",
    "Strategie care maximizează câștigul mediu"
  ]
}
```

### 6. **Ordering / Ordonare**
```json
{
  "type": "ordering",
  "question": "Ordonează pașii algoritmului MinMax:",
  "correct_order": [
    "Verifică dacă nodul este terminal",
    "Dacă e nod MAX, alege maximul valorilor copiilor",
    "Dacă e nod MIN, alege minimul valorilor copiilor",
    "Returnează valoarea calculată"
  ],
  "explanation": "Algoritmul MinMax verifică mai întâi dacă nodul este terminal, apoi calculează valoarea recursiv."
}
```

### 7. **Numerical / Calcul numeric**
```json
{
  "type": "numerical",
  "question": "Pentru un arbore cu branching factor 3 și adâncime 4, câte noduri frunze există?",
  "correct_answer": 81,
  "tolerance": 0,  // sau procent pentru răspunsuri aproape corecte
  "explanation": "Numărul de frunze = b^d = 3^4 = 81"
}
```

---

## 🏗️ Structură Modul Backend

### Fișier: `backend/app/theory_questions.py`

```python
"""
SmarTest — Întrebări bazate pe teorie din cursuri
"""

from typing import List, Dict, Any, Optional
import json
import random
from pathlib import Path

# Structură pentru teoria
THEORY_DATA_PATH = Path("backend/data/theory")

class TheoryQuestionGenerator:
    """Generează întrebări bazate pe teoria din cursuri"""
    
    def __init__(self, theory_file: str):
        """Încarcă teoria dintr-un fișier JSON"""
        with open(THEORY_DATA_PATH / theory_file, 'r', encoding='utf-8') as f:
            self.theory_data = json.load(f)
    
    def generate_question(self, topic_id: str, question_type: Optional[str] = None, 
                         seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generează o întrebare aleatorie pentru un topic.
        
        Args:
            topic_id: ID-ul topicului (ex: "nash_equilibrium")
            question_type: Tipul întrebării (opțional, altfel aleatoriu)
            seed: Seed pentru reproducibilitate
        """
        # Găsește topicul
        topic = next((t for t in self.theory_data["topics"] if t["topic_id"] == topic_id), None)
        if not topic:
            raise ValueError(f"Topic {topic_id} not found")
        
        # Alege template-ul
        templates = topic["question_templates"]
        if question_type:
            templates = [t for t in templates if t["type"] == question_type]
        
        if not templates:
            raise ValueError(f"No templates found for type {question_type}")
        
        template = random.choice(templates)
        
        # Generează întrebarea
        return self._build_question_from_template(template, topic, seed)
    
    def _build_question_from_template(self, template: Dict, topic: Dict, seed: Optional[int]) -> Dict[str, Any]:
        """Construiește întrebarea completă din template"""
        # Implementare specifică pentru fiecare tip
        question_type = template["type"]
        
        if question_type == "multiple_choice":
            return self._build_multiple_choice(template, topic)
        elif question_type == "true_false":
            return self._build_true_false(template, topic)
        elif question_type == "fill_blank":
            return self._build_fill_blank(template, topic)
        # ... etc pentru fiecare tip
        
    def _build_multiple_choice(self, template: Dict, topic: Dict) -> Dict[str, Any]:
        """Construiește întrebare multiple choice"""
        # Amestecă opțiunile
        options = [template["correct_answer"]] + template["distractors"]
        random.shuffle(options)
        
        correct_index = options.index(template["correct_answer"])
        
        return {
            "id": f"THEORY-{random.randint(100000, 999999)}",
            "type": "theory_multiple_choice",
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "difficulty": topic["difficulty"],
            "question_text": template["template"],
            "options": options,
            "correct_index": correct_index,
            "correct_answer": template["correct_answer"],
            "explanation": template.get("explanation", ""),
            "theory_reference": {
                "definition": topic["theory"]["definition"],
                "key_concepts": topic["theory"]["key_concepts"]
            }
        }
    
    # ... metode similare pentru celelalte tipuri
```

---

## 📝 Exemple Concrete de Teorie

### Exemplu 1: Echilibru Nash (extins)

```json
{
  "topic_id": "nash_equilibrium_extended",
  "topic_name": "Echilibru Nash - Teorie Completă",
  "difficulty": "medium",
  "theory": {
    "definition": "Echilibru Nash este o combinație de strategii unde fiecare jucător alege strategia care maximizează utilitatea sa, dată strategiile celorlalți jucători.",
    "key_concepts": [
      {
        "concept": "Best Response",
        "definition": "Strategia care maximizează utilitatea unui jucător dată strategiile celorlalți",
        "formula": "BR_i(s_{-i}) = argmax_{s_i} u_i(s_i, s_{-i})"
      },
      {
        "concept": "Echilibru Nash",
        "definition": "Profil de strategii s* = (s*_1, ..., s*_n) astfel încât pentru fiecare jucător i, s*_i este best response la s*_{-i}",
        "formula": "u_i(s*_i, s*_{-i}) ≥ u_i(s_i, s*_{-i}) pentru toate s_i"
      }
    ],
    "theorems": [
      {
        "name": "Teorema Nash",
        "statement": "Orice joc finit cu informație completă are cel puțin un echilibru Nash în strategii mixte.",
        "proof_hint": "Folosește teorema punctului fix a lui Brouwer"
      }
    ],
    "examples": [
      {
        "name": "Dilema Prizonierului",
        "description": "Joc clasic cu echilibru Nash suboptimal",
        "payoff_matrix": "[[-5,-5], [0,-10]], [[-10,0], [-1,-1]]",
        "nash_equilibrium": "(Confesă, Confesă)",
        "pareto_optimal": "(Nu confesa, Nu confesa)"
      }
    ]
  },
  "question_templates": [
    {
      "type": "multiple_choice",
      "template": "Conform teoremei Nash, orice joc finit cu informație completă:",
      "correct_answer": "Are cel puțin un echilibru Nash în strategii mixte",
      "distractors": [
        "Are întotdeauna echilibru Nash în strategii pure",
        "Nu are întotdeauna echilibru Nash",
        "Are exact un echilibru Nash"
      ],
      "explanation": "Teorema Nash garantează existența, dar nu unicitatea sau că e în strategii pure."
    }
  ]
}
```

### Exemplu 2: Alpha-Beta Pruning

```json
{
  "topic_id": "alpha_beta_pruning",
  "topic_name": "Alpha-Beta Pruning",
  "difficulty": "hard",
  "theory": {
    "definition": "Alpha-Beta pruning este o optimizare a algoritmului MinMax care elimină ramuri care nu pot influența decizia finală.",
    "key_concepts": [
      {
        "concept": "Alpha",
        "definition": "Valoarea cea mai bună pe care jucătorul MAX o poate garanta la nivelul curent",
        "initial_value": "-∞"
      },
      {
        "concept": "Beta",
        "definition": "Valoarea cea mai bună pe care jucătorul MIN o poate garanta la nivelul curent",
        "initial_value": "+∞"
      },
      {
        "concept": "Pruning",
        "definition": "Eliminarea unei ramuri când se știe că nu poate îmbunătăți valoarea curentă",
        "condition": "beta ≤ alpha"
      }
    ],
    "algorithms": [
      {
        "name": "Alpha-Beta Pruning",
        "pseudocode": "function alphabeta(node, depth, alpha, beta, maximizing):\n  if depth == 0 or terminal(node):\n    return evaluate(node)\n  if maximizing:\n    value = -∞\n    for child in children(node):\n      value = max(value, alphabeta(child, depth-1, alpha, beta, False))\n      alpha = max(alpha, value)\n      if beta <= alpha:\n        break  # Pruning\n    return value\n  else:\n    value = +∞\n    for child in children(node):\n      value = min(value, alphabeta(child, depth-1, alpha, beta, True))\n      beta = min(beta, value)\n      if beta <= alpha:\n        break  # Pruning\n    return value",
        "complexity_best": "O(b^(d/2))",
        "complexity_worst": "O(b^d)",
        "improvement": "În cel mai bun caz, reduce complexitatea la jumătate față de MinMax"
      }
    ]
  },
  "question_templates": [
    {
      "type": "multiple_choice",
      "template": "Când se face pruning în algoritmul Alpha-Beta?",
      "correct_answer": "Când beta ≤ alpha",
      "distractors": [
        "Când alpha ≥ beta",
        "Când valoarea nodului este 0",
        "Când adâncimea depășește limita"
      ],
      "explanation": "Pruning-ul se face când beta ≤ alpha, adică când jucătorul MIN știe că MAX nu va alege această ramură."
    },
    {
      "type": "true_false",
      "template": "Alpha-Beta pruning garantează întotdeauna reducerea numărului de noduri evaluate.",
      "correct_answer": false,
      "explanation": "În cel mai rău caz, Alpha-Beta evaluează același număr de noduri ca MinMax. Beneficiul apare în cel mai bun caz."
    }
  ]
}
```

---

## 🔄 Integrare cu Sistemul Existent

### 1. **Endpoint nou în `main.py`**

```python
@app.get("/theory/generate")
def generate_theory_question(topic_id: str, question_type: str | None = None, 
                            seed: int | None = None):
    """
    Generează o întrebare bazată pe teoria din cursuri.
    
    topic_id: ID-ul topicului (ex: "nash_equilibrium")
    question_type: Tipul întrebării (opțional)
    seed: Seed pentru reproducibilitate
    """
    generator = TheoryQuestionGenerator("ai_course_theory.json")
    return generator.generate_question(topic_id, question_type, seed)

@app.post("/theory/grade")
def grade_theory_question(ap: AnswerPayload):
    """
    Evaluează răspunsul la o întrebare teoretică.
    """
    return grade_theory_answer(ap.answer, ap.payload)
```

### 2. **Integrare în Quiz**

```javascript
// În quiz.js
async function generateTheoryQuestion(topicId, questionType) {
  const url = USE_PROXY
    ? `api/proxy_theory_generate.php?topic_id=${topicId}&question_type=${questionType}`
    : `${API}/theory/generate?topic_id=${topicId}&question_type=${questionType}`;
  
  const response = await fetch(url);
  return await response.json();
}
```

---

## 📚 Structură Recomandată pentru Fișiere

```
backend/
├── data/
│   └── theory/
│       ├── ai_course_theory.json      # Teoria principală
│       ├── game_theory.json           # Teoria jocurilor
│       ├── algorithms.json            # Algoritmi
│       └── csp_theory.json            # CSP theory
├── app/
│   ├── theory_questions.py            # Generator întrebări
│   ├── theory_grading.py              # Evaluare răspunsuri
│   └── main.py                        # API endpoints
```

---

## 🎯 Pași de Implementare Recomandați

1. **Creează structura de date** pentru teoria (JSON)
2. **Implementează generatorul** de întrebări (`theory_questions.py`)
3. **Implementează evaluarea** răspunsurilor (`theory_grading.py`)
4. **Adaugă endpoint-uri** în API
5. **Integrează în frontend** (quiz.php, etc.)
6. **Creează interfață** pentru adăugare/editare teorie (opțional, pentru profesori)

---

## 💡 Exemple de Întrebări Generate

### Din teoria Echilibru Nash:
- "Care este definiția corectă a echilibrului Nash?"
- "True/False: Echilibru Nash garantează optimul Pareto."
- "Completă: Best Response pentru jucătorul 1 este: BR₁(s₂) = _____"

### Din teoria MinMax:
- "Care este complexitatea algoritmului MinMax?"
- "Explică diferența între MinMax și Alpha-Beta pruning."
- "Ordonează pașii algoritmului Alpha-Beta."

---

**Notă:** Această structură permite adăugarea progresivă de teoria și întrebări, menținând flexibilitatea și extensibilitatea sistemului.

