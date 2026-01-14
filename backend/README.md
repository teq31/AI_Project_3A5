# 🧠 SmarTest — Backend (FastAPI)

Acesta este backend-ul aplicației **SmarTest**, care se ocupă de generarea întrebărilor și evaluarea răspunsurilor (în prezent implementat pentru tipul **„Echilibru Nash în strategii pure”**).

Frontend-ul este scris în **PHP + JavaScript** și comunică cu acest backend prin API (direct sau prin proxy PHP).

---

## 🚀 1. Cerințe

- **Python 3.10+**
- **pip** (manager de pachete)
- Recomandat: **VS Code** sau rulare prin terminal / Command Prompt
- Backend-ul trebuie rulat în paralel cu **Apache (XAMPP)** pentru frontend-ul PHP

---

## ⚙️ 2. Instalare, configurare și rulare

Deschide un terminal în folderul `backend/` și execută pașii de mai jos:

```bash
# 1️⃣ Creează un mediu virtual Python
python -m venv .venv

# 2️⃣ Activează mediul virtual:
# --- pe Windows (Command Prompt)
.venv\Scripts\activate.bat
# --- pe PowerShell (dacă este permis)
.venv\Scripts\activate
# --- pe macOS / Linux
# source .venv/bin/activate

# 3️⃣ Instalează toate dependențele necesare
pip install -r requirements.txt

# 4️⃣ Pornește serverul FastAPI
uvicorn app.main:app --reload --port 8000

---