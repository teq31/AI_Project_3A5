# 🔍 Debugging NLP - Ghid Complet

## Probleme Identificate și Rezolvate

### 1. NLP nu se folosește efectiv
**Problema:** NLP era marcat ca "activ" dar nu era folosit în evaluare.

**Soluție:** 
- Verificare directă cu `semantic_similarity()` înainte de verificarea conceptelor
- Prag redus la 0.60 pentru flexibilitate
- Logging adăugat pentru debugging

### 2. Scoruri prea mici pentru răspunsuri corecte
**Problema:** Chiar dacă răspunsul era corect semantic, primea scor mic.

**Soluție:**
- Prioritate 1: Verificare răspuns complet cu NLP (dacă există `correct_answer`)
- Prioritate 2: Verificare concepte cu NLP
- Similaritate >= 0.80 = scor 100%
- Similaritate >= 0.60 = scor proporțional

### 3. Justificare cerută când nu e cazul
**Problema:** Sistemul cerea justificare pentru întrebări normale.

**Soluție:**
- Detecție mai strictă: doar pentru tipul "justification" sau când întrebarea conține explicit "justifică", "și explică", etc.
- Eliminat "explică" simplu din lista de indicatori

## Cum să Testezi NLP

### Test 1: Verifică Status NLP
```bash
# Accesează în browser:
http://127.0.0.1:8000/nlp/status
```

Ar trebui să vezi:
```json
{
  "semantic_similarity_available": true,
  "nlp_available": false,
  "model_loaded": true,
  "status": "enabled"
}
```

### Test 2: Verifică Log-urile Serverului
Când evaluezi un răspuns, ar trebui să vezi în consola serverului:
```
INFO:app.theory_grading:NLP similarity check: 0.85 for answer: '...' vs correct: '...'
INFO:app.theory_grading:NLP concept extraction: found 3/5 keywords: ['concept1', 'concept2', ...]
```

### Test 3: Testează cu Răspuns Corect
1. Generează o întrebare teoretică
2. Copiază răspunsul corect din "Arată soluția oficială"
3. Evaluează răspunsul
4. Ar trebui să primești scor >= 80% dacă NLP funcționează

### Test 4: Testează Similaritate Semantică
Răspunde cu sinonime sau parafrază:
- În loc de "backtracking", scrie "algoritm de backtracking"
- În loc de "echilibru Nash", scrie "soluție Nash"
- Ar trebui să fie acceptate dacă NLP funcționează

## Probleme Comune

### NLP nu se încarcă
**Sintom:** Indicatorul arată "Model: Neîncărcat"

**Soluție:**
- Modelul se încarcă la prima utilizare (lazy loading)
- Evaluează un răspuns - modelul se va încărca automat
- După prima evaluare, indicatorul ar trebui să arate "Model: Încărcat"

### Scoruri prea mici
**Sintom:** Chiar răspunsul corect primește scor mic

**Verificare:**
1. Verifică log-urile serverului pentru erori NLP
2. Verifică dacă `correct_answer` este definit în întrebare
3. Verifică dacă `correct_keywords` sunt definite

### "Metodă: Fallback"
**Sintom:** Indicatorul arată "Metodă: Fallback" în loc de "NLP Semantic Similarity"

**Cauze posibile:**
1. NLP nu este activat (`SEMANTIC_SIMILARITY_AVAILABLE = False`)
2. Modelul nu se încarcă (verifică log-urile)
3. Eroare în calcularea similarității (verifică log-urile)

**Soluție:**
- Verifică endpoint-ul `/nlp/status`
- Verifică log-urile serverului pentru erori
- Repornește serverul FastAPI

## Debugging Avansat

### Verifică dacă NLP este folosit
Adaugă în cod (temporar):
```python
logger.info(f"NLP_ENABLED: {NLP_ENABLED}")
logger.info(f"SEMANTIC_SIMILARITY_AVAILABLE: {SEMANTIC_SIMILARITY_AVAILABLE}")
logger.info(f"Using method: {method}")
```

### Testează funcția semantic_similarity direct
```python
from app.nlp_utils import semantic_similarity
result = semantic_similarity("backtracking", "algoritm de backtracking")
print(f"Similarity: {result}")  # Ar trebui să fie > 0.7
```

### Verifică modelul
```python
from app.nlp_utils import get_semantic_model
model = get_semantic_model()
print(f"Model loaded: {model is not None}")
```

## Rezolvare Rapidă

Dacă nimic nu funcționează:

1. **Repornește serverul FastAPI:**
   ```bash
   cd backend
   .venv\Scripts\activate
   py -m uvicorn app.main:app --reload --port 8000
   ```

2. **Verifică dependențele:**
   ```bash
   pip list | findstr sentence-transformers
   pip list | findstr scikit-learn
   ```

3. **Reinstalează NLP (dacă e necesar):**
   ```bash
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers scikit-learn
   ```

4. **Verifică log-urile:**
   - Urmărește consola serverului când evaluezi un răspuns
   - Caută erori sau warning-uri

## Contact

Dacă problemele persistă, verifică:
- Log-urile serverului FastAPI
- Endpoint-ul `/nlp/status`
- Consola browser-ului pentru erori JavaScript

