<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>SmarTest — Întrebări Teorie</title>
  <link rel="stylesheet" href="css/style.css?v=8">
</head>
<body>
  <a href="index.php" class="back-home">⬅️ Înapoi la meniu</a>
  <div class="container">
    <h1>SmarTest — Întrebări Teorie</h1>

    <!-- NLP Status Indicator -->
    <div id="nlpStatus" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; background: #f7fafc; border: 2px solid #e2e8f0;">
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span id="nlpStatusIcon">⏳</span>
          <span id="nlpStatusText">Verificare status NLP...</span>
        </div>
        <button id="refreshNLPStatus" onclick="checkNLPStatus()" style="padding: 4px 12px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem;">🔄 Reîncarcă</button>
      </div>
    </div>

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

