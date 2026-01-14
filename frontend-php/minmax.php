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
  <title>SmarTest — Problema 4: MinMax cu Alpha-Beta</title>
  <link rel="stylesheet" href="css/style.css?v=7">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
</head>
<body>
  <script>
    (function() {
      const params = new URLSearchParams(window.location.search);
      const replayId = params.get('replay');
      if (replayId) {
        window.addEventListener('load', function() {
          loadReplayMinmax(replayId);
        });
      }
    })();
  </script>
  <a href="index.php" class="back-home">⬅️ Înapoi la meniu</a>
  <div class="container">
    <h1>SmarTest — Problema 4: MinMax cu optimizare Alpha-Beta</h1>

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

    <!-- 🟢 MODUL 1: răspunzi la exercițiile generate (CE AVEAI DEJA) -->
    <div id="solveSection">
      <div class="card">
        <h3>Generator exercițiu</h3>
        <div class="grid">
          <div><label>Adâncime</label><input type="number" id="depth" value="3" min="2" max="5"></div>
          <div><label>Factor ramificare</label><input type="number" id="branching" value="2" min="2" max="4"></div>
          <div><label>Valoare minimă</label><input type="number" id="valueMin" value="-10" min="-20" max="0"></div>
          <div><label>Valoare maximă</label><input type="number" id="valueMax" value="10" min="0" max="20"></div>
          <div><label>Seed (opțional)</label><input type="number" id="seed" placeholder=""></div>
        </div>
        <button id="genBtn">Generează întrebare</button>
      </div>

      <div class="card">
        <h3>Întrebare generată</h3>
        <p><strong>Pentru arborele dat, care va fi valoarea din rădăcină și câte noduri frunze vor fi vizitate în cazul aplicării strategiei MinMax cu optimizarea Alpha-Beta?</strong></p>
        
        <div id="treeVisualization"
            style="margin: 20px 0; overflow-x: auto; padding: 20px; background: #f9f9f9; border-radius: 8px;"></div>
        
        <div class="row">
          <input id="answer" placeholder="ex: 5 4 sau valoare=5, frunze=4">
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

    <!-- 🔵 MODUL 2: utilizatorul își dă propriile exerciții -->
    <div id="customSection" style="display:none;">
      <div class="card">
        <h3>Exercițiul tău</h3>
        <p>
          Poți introduce propriul arbore MinMax: alegi adâncimea și factorul de ramificare, apoi scrii 
          <strong>valorile frunzelor de la stânga la dreapta</strong>, separate prin spațiu.
        </p>

        <div class="grid">
          <div>
            <label>Adâncime</label>
            <input type="number" id="customDepth" value="3" min="2" max="5">
          </div>
          <div>
            <label>Factor ramificare</label>
            <input type="number" id="customBranching" value="2" min="2" max="4">
          </div>
          <div style="grid-column: 1 / -1;">
            <label>Valorile frunzelor (stânga → dreapta)</label>
            <textarea id="customLeaves" rows="3"
                      placeholder="ex: 3 5 -2 7 4 1 0 9"></textarea>
            <small id="customHint"></small>
            
            <div style="margin-top: 12px; padding: 12px; background: #f7fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
              <label for="customLeavesFile" style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">
                📄 Sau încarcă un document cu valorile frunzelor:
              </label>
              <div style="display: flex; gap: 8px; align-items: center;">
                <input type="file" id="customLeavesFile" accept=".txt,.pdf" style="flex: 1; padding: 8px; border: 1px solid #cbd5e0; border-radius: 6px;">
                <button onclick="loadCustomLeavesFromFile()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                  Încarcă document
                </button>
              </div>
              <small style="display: block; margin-top: 6px; color: #718096;">
                Acceptă fișiere .txt sau .pdf. Conținutul va fi încărcat în textarea.
              </small>
            </div>
          </div>
        </div>

        <button id="solveCustomBtn">Calculează pentru exercițiul meu</button>

        <div id="customResult" style="margin-top: 10px;"></div>

        <details style="margin-top:12px">
          <summary>Detalii calcul</summary>
          <pre id="customSolution"></pre>
        </details>
      </div>
    </div>
  </div>

  <script src="js/minmax.js?v=11"></script>
</body>
</html>
