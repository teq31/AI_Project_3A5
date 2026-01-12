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
  <title>SmarTest — Întrebări Teorie</title>
  <link rel="stylesheet" href="css/style.css?v=8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
</head>
<body>
  <a href="index.php" class="back-home">⬅️ Înapoi la meniu</a>
  <div class="container">
    <h1>SmarTest — Întrebări Teorie</h1>

    <div class="card">
      <h3>Generator întrebare teorie</h3>
      <div class="grid">
        <div>
          <label>Topic (opțional - lasă gol pentru aleatoriu)</label>
          <select id="topicId">
            <option value="">Aleatoriu</option>
          </select>
        </div>
        <div>
          <label>Tip întrebare (opțional)</label>
          <select id="questionType">
            <option value="">Aleatoriu</option>
            <option value="multiple_choice">Multiple Choice</option>
            <option value="true_false">True/False</option>
            <option value="fill_blank">Fill in the Blank</option>
            <option value="short_answer">Short Answer</option>
            <option value="justification">Justificare</option>
            <option value="example">Exemplu</option>
            <option value="comparison">Comparare</option>
            <option value="definition">Definiție</option>
            <option value="calculation">Calcul</option>
            <option value="matrix_analysis">Analiză Matriceală</option>
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
      <div id="questionContainer" style="margin: 16px 0;">
        <p style="color: #718096;">(nimic încă - generează o întrebare)</p>
      </div>
      <div class="row">
        <input id="answer" placeholder="Introdu răspunsul tău">
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
        <div id="solution" style="background: #1a202c; color: #e2e8f0; padding: 16px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.9rem; line-height: 1.6; overflow-x: auto; margin-top: 8px;"></div>
      </details>
    </div>
  </div>

  <script src="js/theory.js"></script>
</body>
</html>

