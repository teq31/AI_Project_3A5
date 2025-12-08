<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <title>SmarTest — Echilibru Nash</title>
  <link rel="stylesheet" href="css/style.css?v=7">
</head>
<body>
  <div class="container">
    <h1>SmarTest — Echilibru Nash (strategii pure)</h1>

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
