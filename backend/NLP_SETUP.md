# 🧠 Configurare NLP (Procesare de Limbaj Natural)

Acest proiect folosește procesare de limbaj natural (NLP) pentru a înțelege mai bine răspunsurile utilizatorilor și a oferi evaluare mai precisă și naturală.

## 📦 Dependențe

Bibliotecile NLP sunt opționale - sistemul funcționează și fără ele, dar cu funcționalități reduse.

### Instalare completă (recomandat)

```bash
# Activează mediul virtual
.venv\Scripts\activate  # Windows
# sau
source .venv/bin/activate  # Linux/Mac

# Instalează toate dependențele (inclusiv NLP)
# Dacă ai erori SSL, folosește:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# SAU instalează manual fiecare bibliotecă:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org scikit-learn
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org fuzzywuzzy
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org python-Levenshtein
```

### Biblioteci NLP folosite

1. **sentence-transformers** - Similaritate semantică între texte
   - Model: `paraphrase-multilingual-MiniLM-L12-v2`
   - Suport pentru română și engleză
   - Se descarcă automat la prima utilizare (~420MB)

2. **scikit-learn** - Pentru calcularea similarității cosinus

3. **fuzzywuzzy** + **python-Levenshtein** - Fallback pentru matching fuzzy
   - Folosit dacă sentence-transformers nu este disponibil

## 🚀 Funcționalități NLP

### 1. Similaritate Semantică
Sistemul poate înțelege că următoarele răspunsuri sunt similare semantic:
- "Backtracking" ≈ "algoritm de backtracking" ≈ "folosește backtracking"
- "Echilibru Nash" ≈ "Nash equilibrium" ≈ "echilibru de tip Nash"

### 2. Extragere Concepte
Detectează concepte cheie chiar dacă sunt exprimate diferit:
- "ordine de explorare" ≈ "ordinea în care explorează"
- "pruning" ≈ "eliminare ramuri" ≈ "tăiere noduri"

### 3. Înțelegere Intenție
Detectează automat:
- Incertitudine: "nu sunt sigur", "poate"
- Afirmație: "da", "adevărat", "corect"
- Negare: "nu", "fals", "incorect"
- Justificare: "deoarece", "pentru că"

### 4. Comparare Naturală
Compară răspunsuri folosind înțelegere semantică, nu doar matching exact:
- "O(b^(d/2))" ≈ "complexitate O de b la puterea d pe 2"
- "minus infinit" ≈ "-∞" ≈ "negative infinity"

## ⚙️ Instalare rapidă

### Opțiunea 1: Script automat (recomandat)
```bash
# Windows (Command Prompt)
install_nlp.bat

# Windows (PowerShell)
.\install_nlp.ps1
```

### Opțiunea 2: Manual
```bash
# Activează mediul virtual
.venv\Scripts\activate  # Windows

# Instalează dependențele NLP
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers scikit-learn fuzzywuzzy python-Levenshtein
```

## ⚙️ Configurare

Sistemul detectează automat dacă bibliotecile NLP sunt disponibile:
- ✅ **Cu NLP**: Funcționalități complete, evaluare semantică precisă
- ⚠️ **Fără NLP**: Fallback la metode tradiționale (regex, substring matching)

**Notă**: Dacă întâmpini erori SSL (ca `Could not find a suitable TLS CA certificate bundle`), folosește scripturile de mai sus care includ `--trusted-host`.

## 📊 Exemple de Utilizare

### Răspunsuri recunoscute ca similare:

```
Utilizator: "Algoritmul folosește backtracking pentru a rezolva problema"
Sistem: ✅ Recunoaște "backtracking" chiar dacă nu este exact "Backtracking"

Utilizator: "Complexitatea este O de b la d pe 2"
Sistem: ✅ Recunoaște că este echivalent cu "O(b^(d/2))"

Utilizator: "Da, deoarece algoritmul verifică sistematic toate stările"
Sistem: ✅ Separă răspunsul ("Da") de justificare ("deoarece...")
```

## 🔧 Troubleshooting

### Eroare: "Sentence Transformers not available"
- Instalează: `pip install sentence-transformers scikit-learn`
- Modelul se descarcă automat la prima utilizare

### Eroare: "FuzzyWuzzy not available"
- Instalează: `pip install fuzzywuzzy python-Levenshtein`
- Este folosit ca fallback

### Performanță lentă
- Prima utilizare: Modelul NLP se descarcă (~420MB)
- Utilizări ulterioare: Modelul se încarcă în memorie (rapid)
- Pentru producție: Consideră cache pentru embeddings

## 📝 Note

- Modelul NLP este multilingv și funcționează bine pentru română și engleză
- Similaritatea semantică este calculată folosind embeddings (vectori de dimensiune 384)
- Pragul implicit pentru "corect" este 0.75 (75% similaritate)
- Sistemul funcționează și fără NLP, dar cu precizie redusă

