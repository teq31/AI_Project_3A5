# 📚 Cum Funcționează Proiectul SmarTest

## 🏗️ Arhitectura Generală

Proiectul este o **aplicație web educațională** cu arhitectură **client-server**:

```
┌─────────────────┐         ┌──────────────────┐
│   Frontend      │  HTTP   │    Backend       │
│   (PHP/JS)      │ ◄─────► │   (FastAPI)      │
│   localhost     │         │   :8000          │
└─────────────────┘         └──────────────────┘
```

---

## 🎯 Componente Principale

### 1. **Backend (FastAPI - Python)**
**Locație:** `backend/app/`

**Server:** Rulează pe `http://127.0.0.1:8000`

**Funcții principale:**
- Generează întrebări pentru diferite tipuri de probleme
- Evaluează răspunsurile utilizatorilor cu flexibilitate maximă
- Folosește NLP (Natural Language Processing) pentru înțelegere semantică

**Module principale:**
- `main.py` - Entry point, definește toate endpoint-urile API
- `smartest_nash.py` - Echilibru Nash (teoria jocurilor)
- `smartest_minmax.py` - Algoritm MinMax cu Alpha-Beta Pruning
- `smartest_problem1.py` - Identificare strategii (N-Queens, Hanoi, etc.)
- `smartest_csp.py` - Probleme de satisfacere a constrângerilor (CSP)
- `theory_questions.py` - Generare întrebări teoretice
- `theory_grading.py` - Evaluare răspunsuri teoretice cu NLP
- `nlp_utils.py` - Utilități NLP (similaritate semantică, embeddings)

---

### 2. **Frontend (PHP + JavaScript)**
**Locație:** `frontend-php/`

**Funcții principale:**
- Interfață utilizator pentru generare și rezolvare întrebări
- Comunică cu backend-ul prin proxy-uri PHP
- Gestionează quiz-uri mixte (multiple tipuri de întrebări)

**Pagini principale:**
- `index.php` - Meniu principal
- `quiz.php` - Generator de quiz-uri mixte
- `nash.php` - Pagină dedicată pentru Echilibru Nash
- `minmax.php` - Pagină dedicată pentru MinMax
- `strategy.php` - Pagină dedicată pentru Problema 1
- `csp.php` - Pagină dedicată pentru CSP
- `theory.php` - Pagină dedicată pentru întrebări teoretice

**JavaScript:**
- `quiz.js` - Logică pentru quiz-uri mixte
- `nash.js`, `minmax.js`, `strategy.js`, `csp.js`, `theory.js` - Logică specifică fiecărui tip

**API Proxy-uri (PHP):**
- `api/proxy_*.php` - Proxy-uri care fac legătura între frontend și backend

---

## 🔄 Fluxul de Funcționare

### **Scenariul 1: Generare și Rezolvare Întrebare Individuală**

```
1. Utilizator → Deschide pagină (ex: nash.php)
2. Frontend → Apel API: GET /nash/generate
3. Backend → Generează întrebare (matrice joc, parametri)
4. Backend → Returnează JSON cu întrebarea
5. Frontend → Afișează întrebarea în interfață
6. Utilizator → Introdu răspuns
7. Frontend → Apel API: POST /nash/grade
8. Backend → Evaluează răspuns (flexibil, acceptă multiple formate)
9. Backend → Returnează feedback (corect/greșit, explicații)
10. Frontend → Afișează rezultatul
```

### **Scenariul 2: Generare Quiz Mixt**

```
1. Utilizator → Deschide quiz.php
2. Utilizator → Configurează quiz-ul:
   - Alege tipuri de întrebări (Nash, MinMax, CSP, Strategy, Theory)
   - Poate adăuga/șterge întrebări
3. Utilizator → Apasă "Generează Quiz"
4. Frontend → Pentru fiecare întrebare configurată:
   - Apelează endpoint-ul corespunzător
   - Stochează întrebările generate
5. Frontend → Afișează quiz-ul (una câte una sau toate)
6. Utilizator → Completează răspunsurile
7. Utilizator → Apasă "Verifică Răspunsuri"
8. Frontend → Pentru fiecare răspuns:
   - Apelează endpoint-ul de grading corespunzător
   - Colectează rezultatele
9. Frontend → Afișează rezultatele finale
10. Utilizator → Poate exporta quiz-ul în PDF
```

---

## 🎓 Tipuri de Întrebări Suportate

### **1. Echilibru Nash** (`/nash/*`)
- **Generare:** Matrice joc aleatoare (configurabilă: 3x3, 4x4, etc.)
- **Răspuns:** Poziția echilibrului (ex: "R2 C1", "2 1", "none")
- **Grading:** Flexibil - acceptă multiple formate, ordine diferită

### **2. MinMax cu Alpha-Beta** (`/minmax/*`)
- **Generare:** Arbore de decizie (configurabil: adâncime, factor ramificare)
- **Răspuns:** Valoarea minimax și numărul de frunze evaluate
- **Grading:** Acceptă formate naturale ("valoare=5, frunze=4")

### **3. Identificare Strategie** (`/problem1/*`)
- **Generare:** Probleme clasice (N-Queens, Hanoi, Graph Coloring, Knight Tour)
- **Răspuns:** Numele strategiei (Backtracking, Hillclimbing, etc.)
- **Grading:** Acceptă sinonime, abrevieri, formate diferite

### **4. CSP (Constraint Satisfaction Problems)** (`/csp/*`)
- **Generare:** Probleme CSP (simple, graph coloring, sudoku)
- **Răspuns:** Tipul de optimizare (Forward Checking, MRV, AC-3)
- **Grading:** Flexibil, acceptă multiple denumiri

### **5. Întrebări Teoretice** (`/theory/*`)
- **Generare:** Din fișier JSON (`backend/data/theory/example_theory.json`)
- **Tipuri de întrebări:**
  - Multiple Choice
  - True/False
  - Fill in the Blank
  - Short Answer
  - Justification (cu analiză separată pentru răspuns și justificare)
  - Example (cere exemple concrete)
  - Comparison (compară concepte)
  - Definition (definire concepte)
  - Calculation (calcule matematice)
  - Matrix Analysis (analiză matrice)
- **Topic-uri disponibile:**
  - Echilibru Nash
  - Alpha-Beta Pruning
  - Tipuri de Inteligență Artificială
  - Strategii de Căutare
  - Euristici
  - Probleme de Satisfacere a Constrângerilor (CSP)
  - Ontologii
- **Grading:** 
  - **Cu NLP:** Similaritate semantică, înțelegere intenție, detecție incertitudine
  - **Fără NLP:** Fallback la regex și substring matching

---

## 🧠 Sistemul de Grading Flexibil

### **Principii:**
1. **Acceptă multiple formate:** "R2 C1", "2 1", "rândul 2 coloana 1"
2. **Ordine flexibilă:** "C1 R2" = "R2 C1"
3. **Sinonime:** "Backtracking" = "Backtrack" = "BT"
4. **Toleranță la erori:** Spații extra, diacritice, majuscule/minuscule
5. **Înțelegere semantică:** Pentru întrebări teoretice, înțelege intenția

### **NLP Integration (pentru întrebări teoretice):**
- **Sentence Transformers:** Similaritate semantică între răspunsuri
- **Fuzzy Matching:** Potrivire aproximativă pentru texte
- **Concept Extraction:** Identifică concepte cheie în răspunsuri
- **Intent Detection:** Detectează "nu știu", "nu sunt sigur", "știu parțial"

### **Exemplu de grading flexibil:**

**Răspuns corect:** "R2 C1"

**Răspunsuri acceptate:**
- ✅ "R2 C1"
- ✅ "2 1"
- ✅ "rândul 2, coloana 1"
- ✅ "C1 R2" (ordine inversă)
- ✅ "Rând 2 Coloană 1"
- ✅ "2,1"

---

## 📊 Structura Datelor

### **Format Întrebare (JSON):**
```json
{
  "question": "Text întrebare",
  "type": "nash|minmax|csp|strategy|theory",
  "data": { /* date specifice tipului */ },
  "solution": "Răspuns corect",
  "explanation": "Explicație detaliată"
}
```

### **Format Răspuns Utilizator:**
```json
{
  "payload": { /* întrebarea originală */ },
  "answer": "Răspuns utilizator"
}
```

### **Format Feedback:**
```json
{
  "correct": true|false,
  "score": 0.0-1.0,
  "feedback": "Mesaj feedback",
  "solution": "Răspuns corect",
  "explanation": "Explicație"
}
```

---

## 🚀 Pornirea Proiectului

### **1. Backend:**
```bash
cd backend
# Opțiunea 1: Script automat
start_server.bat  # Windows
# sau
.\start_server.ps1  # PowerShell

# Opțiunea 2: Manual
.venv\Scripts\activate
py -m uvicorn app.main:app --reload --port 8000
```

**Verificare:** `http://127.0.0.1:8000/health` → `{"status":"ok"}`

### **2. Frontend:**
```bash
# Opțiunea 1: XAMPP
# Copiază frontend-php în htdocs
# Pornește Apache
# Accesează: http://localhost/smartest/index.php

# Opțiunea 2: PHP Built-in Server
cd frontend-php
php -S localhost:8080
# Accesează: http://localhost:8080/index.php
```

---

## 🔧 Configurare NLP (Opțional)

Pentru funcționalități NLP avansate (similaritate semantică):

```bash
cd backend
# Script automat
install_nlp.bat  # Windows
# sau
.\install_nlp.ps1  # PowerShell
```

**Dependențe NLP:**
- `sentence-transformers` - Embeddings și similaritate semantică
- `scikit-learn` - Cosine similarity
- `fuzzywuzzy` - Fuzzy string matching
- `python-Levenshtein` - Distanță Levenshtein

**Notă:** Dacă NLP nu este instalat, sistemul folosește metode fallback (regex, substring matching).

---

## 📁 Structura Fișierelor

```
AI_Project_3A5/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── smartest_nash.py     # Nash Equilibrium
│   │   ├── smartest_minmax.py   # MinMax
│   │   ├── smartest_problem1.py # Strategy problems
│   │   ├── smartest_csp.py      # CSP problems
│   │   ├── theory_questions.py  # Theory question generation
│   │   ├── theory_grading.py    # Theory grading with NLP
│   │   └── nlp_utils.py         # NLP utilities
│   ├── data/
│   │   └── theory/
│   │       └── example_theory.json  # Theory questions database
│   ├── requirements.txt
│   ├── start_server.bat
│   └── install_nlp.bat
│
├── frontend-php/
│   ├── index.php                # Main menu
│   ├── quiz.php                 # Quiz generator
│   ├── nash.php                 # Nash page
│   ├── minmax.php               # MinMax page
│   ├── strategy.php             # Strategy page
│   ├── csp.php                  # CSP page
│   ├── theory.php               # Theory page
│   ├── js/
│   │   ├── quiz.js              # Quiz logic
│   │   ├── nash.js
│   │   ├── minmax.js
│   │   ├── strategy.js
│   │   ├── csp.js
│   │   └── theory.js
│   └── api/
│       └── proxy_*.php          # API proxies
│
└── Documentation files...
```

---

## 🎨 Caracteristici Speciale

### **1. Quiz-uri Mixte**
- Poți combina orice tipuri de întrebări într-un singur quiz
- Export în PDF cu toate întrebările și răspunsurile

### **2. Grading Inteligent**
- Acceptă răspunsuri în limba română naturală
- Detectează incertitudine ("nu știu")
- Evaluează justificări separat de răspunsuri principale

### **3. Reproducibilitate**
- Toate endpoint-urile acceptă parametrul `seed`
- Același seed = aceeași întrebare

### **4. Feedback Detaliat**
- Explicații pentru răspunsuri corecte și greșite
- Soluții oficiale
- Scoruri parțiale pentru răspunsuri parțial corecte

---

## 🔍 Endpoint-uri API Disponibile

### **Health Check:**
- `GET /health` - Verifică dacă serverul rulează

### **Nash:**
- `GET /nash/generate` - Generează întrebare Nash
- `POST /nash/grade` - Evaluează răspuns Nash

### **MinMax:**
- `GET /minmax/generate` - Generează întrebare MinMax
- `POST /minmax/grade` - Evaluează răspuns MinMax

### **Strategy (Problem1):**
- `GET /problem1/generate` - Generează întrebare strategie
- `POST /problem1/grade` - Evaluează răspuns strategie

### **CSP:**
- `GET /csp/generate` - Generează întrebare CSP
- `POST /csp/grade` - Evaluează răspuns CSP

### **Theory:**
- `GET /theory/topics` - Listă topic-uri disponibile
- `GET /theory/generate` - Generează întrebare teoretică
- `POST /theory/grade` - Evaluează răspuns teoretic

---

## 📝 Note Importante

1. **Backend-ul trebuie să ruleze înainte de frontend**
2. **CORS este configurat** pentru a permite apeluri din browser
3. **Proxy-urile PHP** gestionează comunicarea între frontend și backend
4. **NLP este opțional** - sistemul funcționează și fără el (cu metode fallback)
5. **Toate răspunsurile sunt evaluate flexibil** - acceptă multiple formate

---

## 🐛 Troubleshooting

### **Backend nu pornește:**
- Verifică Python 3.10+: `py --version`
- Verifică dependențe: `pip list`
- Verifică portul 8000: `netstat -ano | findstr :8000`

### **Frontend nu se conectează:**
- Verifică că backend-ul rulează: `http://127.0.0.1:8000/health`
- Verifică proxy-urile PHP în `frontend-php/api/`
- Verifică consola browser-ului pentru erori JavaScript

### **NLP nu funcționează:**
- Instalează dependențele: `install_nlp.bat`
- Sistemul va folosi fallback automat dacă NLP nu este disponibil

---

**Ultima actualizare:** Proiectul suportă 5 tipuri de probleme practice + întrebări teoretice cu NLP pentru grading avansat.

