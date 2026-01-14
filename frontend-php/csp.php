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
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>SmarTest — Problema 3: CSP cu Backtracking</title>
  <link rel="stylesheet" href="css/style.css?v=8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
</head>
<body>
  <a href="index.php" class="back-home">⬅️ Înapoi la meniu</a>
  <div class="container">
    <h1>SmarTest — Problema 3: CSP cu Backtracking</h1>

    <!-- 🔁 Selector de mod -->
    <div class="card" style="margin-bottom: 24px;">
      <h3>Alege modul</h3>
      <div class="row" style="gap: 10px; flex-wrap: wrap;">
        <button class="mode-btn" data-mode="solve">Vreau să răspund la exerciții</button>
        <button class="mode-btn" data-mode="custom">Vreau să introduc eu exercițiile</button>
      </div>
      <small>
        Poți comuta oricând între moduri fără să pierzi datele introduse.
      </small>
    </div>

    <!-- 🟢 MODUL 1: răspunzi la exercițiile generate -->
    <div id="solveSection">
      <div class="card">
        <h3>Generator exercițiu</h3>
        <div class="grid">
          <div>
            <label>Tip problemă</label>
            <select id="problemType">
              <option value="simple">CSP Simplu</option>
              <option value="graph_coloring">Graph Coloring CSP</option>
              <option value="sudoku">Sudoku CSP</option>
            </select>
          </div>
          <div>
            <label>Optimizare (opțional)</label>
            <select id="optimization">
              <option value="FC">Forward Checking</option>
              <option value="MRV">MRV</option>
              <option value="AC-3">AC-3</option>
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
        <h3>Întrebare generată</h3>
        <pre id="question" style="white-space: pre-wrap; background: #1a202c; color: #e2e8f0; padding: 16px; border-radius: 8px; margin: 12px 0; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.6;">(nimic încă)</pre>
        <div class="row">
          <input id="answer" placeholder="ex: Forward Checking sau 1 (numărul opțiunii)">
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
          <pre id="solution" style="background: #1a202c; color: #e2e8f0; padding: 16px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.9rem; line-height: 1.6; overflow-x: auto;"></pre>
        </details>
      </div>
    </div>

    <!-- 🔵 MODUL 2: utilizatorul își dă propria problemă -->
    <div id="customSection" style="display:none;">
      <div class="card">
        <h3>Exercițiul tău</h3>
        <p>
          Poți introduce propria problemă CSP: alege tipul de problemă și descrie instanța.
        </p>

        <div class="grid">
          <div>
            <label>Tip problemă</label>
            <select id="customProblemType">
              <option value="simple">CSP Simplu</option>
              <option value="graph_coloring">Graph Coloring CSP</option>
              <option value="sudoku">Sudoku CSP</option>
            </select>
          </div>
          <div style="grid-column: 1 / -1;">
            <label>Descriere instanță</label>
            <textarea id="customInstance" rows="4" placeholder="Descrie instanța problemei CSP..."></textarea>
            
            <div style="margin-top: 12px; padding: 12px; background: #f7fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
              <label for="customInstanceFile" style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">
                📄 Sau încarcă un document cu descrierea instanței:
              </label>
              <div style="display: flex; gap: 8px; align-items: center;">
                <input type="file" id="customInstanceFile" accept=".txt,.pdf" style="flex: 1; padding: 8px; border: 1px solid #cbd5e0; border-radius: 6px;">
                <button onclick="loadCustomInstanceFromFile()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                  Încarcă document
                </button>
              </div>
              <small style="display: block; margin-top: 6px; color: #718096;">
                Acceptă fișiere .txt sau .pdf. Conținutul va fi încărcat în textarea.
              </small>
            </div>
          </div>
        </div>

        <button id="solveCustomBtn">Calculează optimizarea</button>

        <div id="customResult" style="margin-top: 10px;"></div>

        <details style="margin-top:12px">
          <summary>Detalii calcul</summary>
          <pre id="customSolution"></pre>
        </details>
      </div>
    </div>
  </div>

  <script src="js/csp.js?v=2"></script>
  <script>
    (function() {
      const params = new URLSearchParams(window.location.search);
      const replayId = params.get('replay');
      if (replayId) {
        window.addEventListener('load', function() {
          loadReplayCsp(replayId);
        });
      }
    })();
  </script>
</body>
</html>


