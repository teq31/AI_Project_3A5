# 🚀 Ghid de Pornire - SmarTest

## 📋 Ce face proiectul?

**SmarTest** este o aplicație educațională pentru **Echilibru Nash în strategii pure** (teoria jocurilor).

- **Backend (FastAPI)**: Generează întrebări despre jocuri matriceale și evaluează răspunsurile
- **Frontend (PHP)**: Interfață web pentru a genera întrebări și a verifica răspunsurile

---

## ⚙️ Pornire Backend (FastAPI)

### Pasul 1: Deschide terminal în folderul `backend/`

```powershell
cd C:\Users\otilia\Desktop\AI-proj\AI_Project_3A5\backend
```

### Pasul 2: Activează mediul virtual (dacă nu este deja activat)

```powershell
.venv\Scripts\Activate.ps1
```

### Pasul 3: Pornește serverul FastAPI

```powershell
py -m uvicorn app.main:app --reload --port 8000
```

**Serverul va rula pe:** `http://127.0.0.1:8000`

**Testează:** Deschide în browser `http://127.0.0.1:8000/health` - ar trebui să vezi `{"status":"ok"}`

---

## 🌐 Pornire Frontend (PHP)

### Opțiunea 1: Cu XAMPP (Recomandat)

1. **Instalează XAMPP** (dacă nu este deja instalat)
   - Descarcă de la: https://www.apachefriends.org/

2. **Copiază folderul `frontend-php` în `htdocs`**
   ```powershell
   # Exemplu: copiază în C:\xampp\htdocs\smartest\
   ```

3. **Pornește Apache din XAMPP Control Panel**

4. **Deschide în browser:**
   ```
   http://localhost/smartest/index.php
   ```

### Opțiunea 2: Cu PHP Built-in Server

1. **Deschide terminal în folderul `frontend-php/`**
   ```powershell
   cd C:\Users\otilia\Desktop\AI-proj\AI_Project_3A5\frontend-php
   ```

2. **Pornește serverul PHP**
   ```powershell
   php -S localhost:8080
   ```

3. **Deschide în browser:**
   ```
   http://localhost:8080/index.php
   ```

---

## ✅ Verificare

1. **Backend rulează?** → `http://127.0.0.1:8000/health`
2. **Frontend rulează?** → `http://localhost/smartest/index.php` (sau portul tău)
3. **Testează generarea unei întrebări** din interfața web

---

## 🔧 Dacă întâmpini probleme

### Backend nu pornește:
- Verifică că Python 3.10+ este instalat: `py --version`
- Verifică că toate dependențele sunt instalate: `py -m pip list`
- Verifică că portul 8000 nu este ocupat de alt proces

### Frontend nu se conectează la backend:
- Verifică că backend-ul rulează pe `http://127.0.0.1:8000`
- Verifică fișierul `frontend-php/js/smartest.js` - variabila `USE_PROXY` trebuie să fie `true` dacă folosești PHP proxy
- Verifică fișierele proxy PHP în `frontend-php/api/`

---

## 📝 Note

- Backend-ul trebuie să ruleze **înainte** de a folosi frontend-ul
- Dacă folosești XAMPP, asigură-te că Apache este pornit
- Serverul FastAPI se reîncarcă automat când modifici codul (datorită flag-ului `--reload`)

