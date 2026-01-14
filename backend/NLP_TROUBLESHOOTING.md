# 🔧 Troubleshooting NLP

## Verificare Status NLP

### 1. Verifică endpoint-ul de status

După ce serverul FastAPI rulează, accesează:
```
http://127.0.0.1:8000/nlp/status
```

Ar trebui să vezi un JSON cu:
```json
{
  "semantic_similarity_available": true,
  "nlp_available": true,
  "model_loaded": true,
  "test_similarity": 1.0,
  "status": "enabled"
}
```

### 2. Verifică dependențele instalate

În terminal, în directorul `backend/`:
```powershell
.venv\Scripts\python.exe -c "import sentence_transformers; print('sentence-transformers: OK')"
.venv\Scripts\python.exe -c "from sklearn.metrics.pairwise import cosine_similarity; print('scikit-learn: OK')"
.venv\Scripts\python.exe -c "from fuzzywuzzy import fuzz; print('fuzzywuzzy: OK')"
```

### 3. Verifică log-urile serverului

Când pornești serverul FastAPI, ar trebui să vezi în consolă:
```
INFO: Sentence Transformers loaded successfully
INFO: Semantic model loaded: paraphrase-multilingual-MiniLM-L12-v2
```

Dacă vezi:
```
WARNING: Sentence Transformers not available...
```

Înseamnă că dependențele nu sunt instalate corect.

## Probleme Comune

### Problema 1: `SEMANTIC_SIMILARITY_AVAILABLE = False`

**Cauză:** `sentence-transformers` sau `scikit-learn` nu sunt instalate sau importul eșuează.

**Soluție:**
```powershell
cd backend
.venv\Scripts\activate
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers scikit-learn
```

### Problema 2: Modelul nu se încarcă

**Cauză:** Modelul `paraphrase-multilingual-MiniLM-L12-v2` nu poate fi descărcat sau încărcat.

**Soluție:**
- Verifică conexiunea la internet (prima dată când se folosește, modelul trebuie descărcat)
- Verifică spațiul pe disc (modelul ocupă ~400MB)
- Verifică log-urile pentru erori specifice

### Problema 3: NLP funcționează dar nu pare să fie folosit

**Cauză:** Funcțiile fallback sunt folosite în loc de NLP.

**Verificare:**
- Verifică log-urile serverului când evaluezi un răspuns
- Verifică dacă `NLP_ENABLED = True` în `theory_grading.py`
- Testează cu un răspuns care ar trebui să beneficieze de NLP (ex: sinonime, răspunsuri parafrazate)

### Problema 4: Eroare la import

**Cauză:** Probleme cu calea sau structura proiectului.

**Soluție:**
- Asigură-te că rulezi serverul din directorul `backend/`
- Verifică că `app/nlp_utils.py` există
- Verifică că toate dependențele sunt în `.venv`

## Testare NLP

### Test 1: Similaritate semantică

Testează dacă NLP-ul înțelege sinonime:
```python
from app.nlp_utils import semantic_similarity
score = semantic_similarity("backtracking", "algoritm de backtracking")
print(f"Similarity: {score}")  # Ar trebui să fie > 0.7
```

### Test 2: Find best match

Testează dacă găsește cel mai bun match:
```python
from app.nlp_utils import find_best_match
match, score = find_best_match("BT", ["Backtracking", "Hillclimbing", "A*"])
print(f"Match: {match}, Score: {score}")  # Ar trebui să fie "Backtracking"
```

### Test 3: Extract key concepts

Testează dacă extrage concepte cheie:
```python
from app.nlp_utils import extract_key_concepts
result = extract_key_concepts(
    "Algoritmul folosește backtracking pentru a rezolva problema",
    ["backtracking", "recursivitate", "optimizare"]
)
print(f"Found: {result['found_keywords']}")  # Ar trebui să conțină "backtracking"
```

## Fallback Behavior

Dacă NLP nu este disponibil, sistemul folosește metode fallback:
- **Fără NLP:** Matching simplu (substring, lowercase)
- **Cu FuzzyWuzzy:** Fuzzy string matching (dacă este instalat)
- **Cu Sentence Transformers:** Similaritate semantică completă (dacă este instalat)

Sistemul va funcționa în orice caz, dar cu NLP va fi mult mai precis și flexibil.

## Reinstalare Completă

Dacă nimic nu funcționează:

```powershell
cd backend
.venv\Scripts\activate

# Dezinstalează
pip uninstall sentence-transformers scikit-learn fuzzywuzzy python-Levenshtein -y

# Reinstalează
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers scikit-learn fuzzywuzzy python-Levenshtein

# Repornește serverul
py -m uvicorn app.main:app --reload --port 8000
```

## Verificare Finală

După instalare, verifică:
1. ✅ Endpoint `/nlp/status` returnează `"status": "enabled"`
2. ✅ Log-urile serverului arată "Sentence Transformers loaded successfully"
3. ✅ Testează o întrebare teoretică și verifică dacă răspunsurile parafrazate sunt acceptate

