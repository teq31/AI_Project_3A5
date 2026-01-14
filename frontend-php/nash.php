<?php
session_start();
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <title>SmarTest — Echilibru Nash</title>
  <link rel="stylesheet" href="css/style.css?v=7">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
</head>
<body>
  <a href="index.php" class="back-home">⬅️ Înapoi la meniu</a>
  <div class="container">
    <h1>SmarTest — Echilibru Nash (strategii pure)</h1>

    <!-- 🔁 Selector de mod -->
    <div class="card" style="margin-bottom: 24px;">
      <h3>Alege modul</h3>
      <div class="row" style="gap: 10px; flex-wrap: wrap;">
        <button class="mode-btn" data-mode="solve">Vreau să răspund la exerciții</button>
        <button class="mode-btn" data-mode="custom">Vreau să introduc eu exercițiile</button>
      </div>
      <small>
        Poți comuta oricând între moduri fără să pierzi ce ai scris.
      </small>
    </div>

    <!-- 🟢 MODUL 1: răspunzi la exercițiile generate (CE AVEAI DEJA) -->
    <div id="solveSection">
      <div class="card">
        <h3>Generator</h3>
        <div class="grid">
          <div>
            <label>Rows</label>
            <input type="number" id="rows" value="3" min="2" max="6">
          </div>
          <div>
            <label>Cols</label>
            <input type="number" id="cols" value="3" min="2" max="6">
          </div>
          <div>
            <label>NE constraint</label>
            <select id="ensure">
              <option value="any">any</option>
              <option value="atleast_one" selected>atleast_one</option>
              <option value="unique">unique</option>
              <option value="none">none</option>
            </select>
          </div>
          <div>
            <label>Seed (opțional)</label>
            <input type="number" id="seed" placeholder="">
          </div>
        </div>
        <button id="genBtn">Generează întrebare</button>
      </div>

      <div class="card">
        <h3>Întrebare</h3>
        <pre id="question">(nimic încă)</pre>
        <div class="row">
          <input id="answer" placeholder="ex: R2 C1 / 2 1 / none">
          <button id="gradeBtn">Evaluează</button>
        </div>
        
        <div style="margin-top: 12px; padding: 12px; background: #f7fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
          <label for="answerFile" style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">
            📄 Sau încarcă un document cu răspunsul:
          </label>
          <div style="display: flex; gap: 8px; align-items: center;">
            <input type="file" id="answerFile" accept=".txt,.pdf" style="flex: 1; padding: 8px; border: 1px solid #cbd5e0; border-radius: 6px;">
            <button onclick="loadAnswerFromFile()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
              Încarcă răspuns
            </button>
          </div>
          <small style="display: block; margin-top: 6px; color: #718096;">
            Acceptă fișiere .txt sau .pdf. Va fi încărcat primul răspuns din document.
          </small>
        </div>
        
        <div id="result"></div>
        <details style="margin-top:12px">
          <summary>Arată soluția oficială</summary>
          <pre id="solution"></pre>
        </details>
      </div>
    </div>

    <!-- 🔵 MODUL 2: utilizatorul își dă propria matrice de payoff -->
    <div id="customSection" style="display:none;">
      <div class="card">
        <h3>Exercițiul tău — Echilibru Nash</h3>
        <p>
          Introdu jocul în formă normală: alegi numărul de linii și coloane, apoi scrii
          <strong>matricea cu pay-off-uri</strong> pentru cei doi jucători.
        </p>

        <div class="grid">
          <div>
            <label>Rows (strategiile jucătorului 1)</label>
            <input type="number" id="customRows" value="2" min="2" max="6">
          </div>
          <div>
            <label>Cols (strategiile jucătorului 2)</label>
            <input type="number" id="customCols" value="2" min="2" max="6">
          </div>
          <div style="grid-column: 1 / -1;">
            <label>Matricea payoff-urilor</label>
            <textarea id="customMatrix" rows="5"
              placeholder="Format: fiecare linie = o strategie a jucătorului 1&#10;fiecare celulă = a,b (payoff jucător1, jucător2)&#10;Exemplu pentru 2x3:&#10;2,1 0,0 1,2&#10;3,0 1,1 0,3"></textarea>
            <small id="customHint"></small>
            
            <div style="margin-top: 12px; padding: 12px; background: #f7fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
              <label for="customMatrixFile" style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">
                📄 Sau încarcă un document cu matricea payoff-urilor:
              </label>
              <div style="display: flex; gap: 8px; align-items: center;">
                <input type="file" id="customMatrixFile" accept=".txt,.pdf" style="flex: 1; padding: 8px; border: 1px solid #cbd5e0; border-radius: 6px;">
                <button onclick="loadCustomMatrixFromFile()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                  Încarcă document
                </button>
              </div>
              <small style="display: block; margin-top: 6px; color: #718096;">
                Acceptă fișiere .txt sau .pdf. Conținutul va fi încărcat în textarea.
              </small>
            </div>
          </div>
        </div>

        <button id="solveCustomNashBtn">Calculează Echilibrul Nash</button>

        <div id="customResult" style="margin-top: 10px;"></div>

        <details style="margin-top:12px">
          <summary>Detalii calcul</summary>
          <pre id="customSolution"></pre>
        </details>
      </div>
    </div>
  </div>

  <script src="js/smartest.js?v=2"></script>
  <script>
    // dacă venim din profil cu parametrul ?replay=ID, încărcăm direct testul salvat
    (function() {
      const params = new URLSearchParams(window.location.search);
      const replayId = params.get('replay');
      if (replayId) {
        // amânăm puțin pentru a fi sigur că DOM-ul este gata
        window.addEventListener('load', function() {
          loadReplayNash(replayId);
        });
      }
    })();
  </script>
</body>
</html>
