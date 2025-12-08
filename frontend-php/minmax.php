<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>SmarTest — MinMax cu Alpha-Beta</title>
  <link rel="stylesheet" href="css/style.css?v=7">
</head>
<body>
  <div class="container">
    <h1>SmarTest — MinMax cu optimizare Alpha-Beta</h1>

    <div class="card">
      <h3>Generator</h3>
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
      <h3>Întrebare</h3>
      <p><strong>Pentru arborele dat, care va fi valoarea din rădăcină și câte noduri frunze vor fi vizitate în cazul aplicării strategiei MinMax cu optimizarea Alpha-Beta?</strong></p>
      
      <div id="treeVisualization" style="margin: 20px 0; overflow-x: auto; padding: 20px; background: #f9f9f9; border-radius: 8px;"></div>
      
      <div class="row">
        <input id="answer" placeholder="ex: 5 4 sau valoare=5, frunze=4">
        <button id="gradeBtn">Evaluează</button>
      </div>
      <div id="result"></div>
      <details style="margin-top:12px">
        <summary>Arată soluția oficială</summary>
        <pre id="solution"></pre>
      </details>
    </div>
  </div>

  <script src="js/minmax.js?v=9"></script>
</body>
</html>

