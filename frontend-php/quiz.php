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
  <title>SmarTest — Generator Quiz</title>
  <link rel="stylesheet" href="css/style.css?v=9">
  <style>
    .quiz-question-config {
      background: #f7fafc;
      border: 2px solid #e2e8f0;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .quiz-question-config label {
      font-weight: 600;
      min-width: 120px;
    }
    .quiz-question-config select {
      flex: 1;
    }
    .quiz-question-config button {
      padding: 8px 16px;
      background: #e53e3e;
      font-size: 0.9rem;
    }
    .quiz-container {
      display: none;
    }
    .quiz-container.active {
      display: block;
    }
    .quiz-question-card {
      background: white;
      border: 2px solid #e2e8f0;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }
    .quiz-question-card.current {
      border-color: #667eea;
      box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    .quiz-navigation {
      display: flex;
      gap: 12px;
      margin-top: 20px;
      flex-wrap: wrap;
    }
    .quiz-navigation button {
      flex: 1;
      min-width: 150px;
    }
    .quiz-results {
      background: #f0fff4;
      border: 2px solid #9ae6b4;
      border-radius: 12px;
      padding: 20px;
      margin-top: 20px;
    }
    .quiz-results h3 {
      color: #22543d;
      margin-top: 0;
    }
    .question-result {
      padding: 12px;
      margin: 8px 0;
      border-radius: 8px;
      background: white;
    }
    .question-result.correct {
      border-left: 4px solid #48bb78;
    }
    .question-result.partial {
      border-left: 4px solid #ed8936;
    }
    .question-result.wrong {
      border-left: 4px solid #e53e3e;
    }
    .pdf-format-selector {
      background: #f7fafc;
      border: 2px solid #e2e8f0;
      border-radius: 10px;
      padding: 16px;
      margin: 16px 0;
    }
    .pdf-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .pdf-actions button {
      width: auto;
      padding: 6px 14px;
      font-size: 0.9rem;
      font-weight: 650;
      border: none;
      color: #fff;
      border-radius: 10px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      box-shadow: 0 6px 16px rgba(102, 126, 234, 0.25);
      transition: all 0.25s ease;
    }
    .pdf-actions button.btn-pdf-summary {
      background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
      box-shadow: 0 6px 16px rgba(229, 62, 62, 0.25);
    }
    .pdf-actions button.btn-pdf-detailed {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      box-shadow: 0 6px 16px rgba(102, 126, 234, 0.25);
    }
    .pdf-actions button:hover {
      transform: translateY(-1px) scale(0.995);
      box-shadow: 0 4px 12px rgba(0,0,0,0.12);
      filter: brightness(1.02);
    }
    .pdf-format-selector label {
      display: block;
      margin: 8px 0;
      padding: 12px;
      background: white;
      border: 2px solid #e2e8f0;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    .pdf-format-selector input[type="radio"] {
      margin-right: 10px;
    }
    .pdf-format-selector label:hover {
      border-color: #667eea;
      background: #f7fafc;
    }
    .pdf-format-selector input[type="radio"]:checked + span {
      font-weight: 600;
      color: #667eea;
    }
  </style>
</head>
<body>
  <a href="index.php" class="back-home">⬅️ Înapoi la meniu</a>
  
  <div class="container">
    <h1>Generator Quiz — SmarTest</h1>
    
    <!-- Setup Quiz -->
    <div id="setupSection" class="quiz-container active">
      <div class="card">
        <h3>Configurează Quiz-ul</h3>
        <p>Alege câte întrebări vrei și de ce tip:</p>
        
        <div id="questionsConfig"></div>
        
        <button onclick="addQuestion()" style="background: #48bb78; margin-bottom: 16px;">
          ➕ Adaugă întrebare
        </button>
        
        <button onclick="startQuiz()" style="width: 100%;">
          🚀 Începe Quiz-ul
        </button>
      </div>
    </div>
    
    <!-- Quiz Section -->
    <div id="quizSection" class="quiz-container">
      <div class="card">
        <h3 id="quizProgress">Întrebarea 1 din 5</h3>
        
        <div id="currentQuestion"></div>
        
        <div class="row">
          <input id="quizAnswer" placeholder="Răspunsul tău">
          <button onclick="submitAnswer()">Trimite răspuns</button>
        </div>
        
        <div style="margin-top: 12px; padding: 12px; background: #f7fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
          <label for="answerFile" style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">
            📄 Sau încarcă un document cu răspunsurile:
          </label>
          <div style="display: flex; gap: 8px; align-items: center;">
            <input type="file" id="answerFile" accept=".txt,.pdf" style="flex: 1; padding: 8px; border: 1px solid #cbd5e0; border-radius: 6px;">
            <button onclick="loadAnswersFromFile()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
              Încarcă răspunsuri
            </button>
          </div>
          <small style="display: block; margin-top: 6px; color: #718096;">
            Acceptă fișiere .txt sau .pdf. Răspunsurile trebuie să fie separate pe linii (fiecare linie = un răspuns).
          </small>
        </div>
        
        <div id="questionFeedback"></div>
        
        <div class="quiz-navigation">
          <button onclick="prevQuestion()" id="prevBtn" style="background: #718096;">
            ⬅️ Înapoi
          </button>
          <button onclick="nextQuestion()" id="nextBtn">
            Următoarea ➡️
          </button>
          <button onclick="finishQuiz()" id="finishBtn" style="display: none; background: #48bb78;">
            ✅ Finalizează Quiz
          </button>
        </div>
      </div>
    </div>
    
    <!-- Results Section -->
    <div id="resultsSection" class="quiz-container">
      <div class="card">
        <div class="quiz-results">
          <h3>📊 Rezultate Quiz</h3>
          <div id="quizScore"></div>
          <div id="quizDetails"></div>
          
          <div class="pdf-format-selector">
            <h4 style="margin-top: 0;">Exportă PDF</h4>
            <div class="pdf-actions">
              <button class="btn-pdf-summary" onclick="exportToPDF('summary')">
                📄 Rezumat
              </button>
              <button class="btn-pdf-detailed" onclick="exportToPDF('detailed')">
                📋 Detaliat
              </button>
            </div>
          </div>
          
          <button onclick="location.reload()" style="background: #718096; margin-top: 20px;">
            🔄 Quiz nou
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
  <script src="js/quiz.js?v=3"></script>
</body>
</html>