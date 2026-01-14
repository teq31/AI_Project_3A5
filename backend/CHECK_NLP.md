# 🔍 Verificare NLP Status

## Problema
NLP apare ca "Dezactivat" în frontend, deși ar trebui să fie activ.

## Pași de verificare

### 1. Verifică dacă backend-ul rulează

Deschide în browser sau folosește curl:
```
http://127.0.0.1:8000/nlp/status
```

Ar trebui să vezi un JSON cu:
```json
{
  "semantic_similarity_available": true,
  "nlp_available": true,
  "model_loaded": true,
  "status": "enabled"
}
```

### 2. Verifică dacă bibliotecile sunt instalate

În terminal, în folderul `backend/`, activează virtual environment și verifică:

```powershell
cd backend
.venv\Scripts\Activate.ps1
pip list | findstr "sentence-transformers scikit-learn"
```

Ar trebui să vezi:
- `sentence-transformers`
- `scikit-learn`

### 3. Dacă bibliotecile NU sunt instalate

Instalează-le:

```powershell
cd backend
.venv\Scripts\Activate.ps1
pip install sentence-transformers scikit-learn certifi
```

### 4. Testează NLP-ul direct

Rulează scriptul de test:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python test_nlp.py
```

### 5. Verifică log-urile backend-ului

Când pornești backend-ul, ar trebui să vezi în consolă:
```
INFO: Sentence Transformers loaded successfully
INFO: Semantic model loaded: paraphrase-multilingual-MiniLM-L12-v2
```

Dacă vezi erori, verifică:
- Conectivitate la internet (modelul se descarcă prima dată)
- Certificat SSL (ar trebui să fie rezolvat cu `certifi`)

### 6. Reîncarcă statusul în frontend

După ce ai verificat că backend-ul returnează status corect, apasă butonul **"REÎNCARCĂ"** în frontend pentru a actualiza statusul.

## Dacă tot nu funcționează

1. **Oprește backend-ul** (Ctrl+C)
2. **Șterge cache-ul modelului** (opțional):
   ```powershell
   # Modelul este salvat în cache-ul Python, de obicei în:
   # C:\Users\<user>\.cache\huggingface\transformers\
   ```
3. **Repornește backend-ul**:
   ```powershell
   cd backend
   .venv\Scripts\Activate.ps1
   py -m uvicorn app.main:app --reload --port 8000
   ```
4. **Verifică din nou** `/nlp/status` în browser

## Note importante

- Modelul se descarcă **prima dată** când este folosit (poate dura câteva minute)
- După descărcare, modelul este salvat în cache și se va încărca mai rapid
- Dacă vezi "model_loaded: false" dar "semantic_similarity_available: true", modelul se va încărca la prima utilizare efectivă

