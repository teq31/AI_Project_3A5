<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <title>SmarTest — Echilibru Nash</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <div class="container">
    <a class="home-btn" href="index.php" title="Înapoi la meniu" aria-label="Înapoi la meniu">
      <!-- home icon (SVG) -->
      <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1V10.5z" fill="#667eea"/>
      </svg>
    </a>
    <h1>SmarTest — Echilibru Nash</h1>
  <h2 class="subtitle">(strategii pure)</h2>

    <div class="card">
      <h3>Generator</h3>
      <div class="grid">
        <div><label>Rows</label><input type="number" id="rows" value="3" min="2" max="6"></div>
        <div><label>Cols</label><input type="number" id="cols" value="3" min="2" max="6"></div>
        <div>
          <label>NE constraint</label>
          <select id="ensure">
            <option value="any">any</option>
            <option value="atleast_one" selected>atleast_one</option>
            <option value="unique">unique</option>
            <option value="none">none</option>
          </select>
        </div>
        <div><label>Seed (opțional)</label><input type="number" id="seed" placeholder=""></div>
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
      <div id="result"></div>
      <details style="margin-top:12px">
        <summary>Arată soluția oficială</summary>
        <pre id="solution"></pre>
      </details>
    </div>
  </div>

  <script src="js/smartest.js"></script>
</body>
</html>
