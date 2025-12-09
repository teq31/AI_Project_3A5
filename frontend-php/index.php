<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>SmarTest — Meniu</title>
  <link rel="stylesheet" href="css/style.css?v=8">
  <style>
    .quiz-button {
      margin-top: 24px;
    }
    .quiz-button a {
      background: linear-gradient(135deg, #7767ff 0%, #9d6bff 55%, #c06bd8 100%);
      border: 1.8px solid rgba(255, 255, 255, 0.75);
      box-shadow: 0 10px 28px rgba(144, 102, 220, 0.24);
      font-weight: 600;
      letter-spacing: 0.3px;
      padding: 16px 26px;
      border-radius: 14px;
      backdrop-filter: blur(4px);
    }
    .quiz-button a:hover {
      background: linear-gradient(135deg, #8575ff 0%, #aa76ff 55%, #cc74de 100%);
      box-shadow: 0 14px 32px rgba(144, 102, 220, 0.30);
      transform: translateY(-2px);
      filter: brightness(1.02);
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>SmarTest</h1>
    <p>Alege tipul de întrebare:</p>
    <ul class="menu">
      <li><a href="nash.php">Echilibru Nash (strategii pure)</a></li>
      <li><a href="minmax.php">MinMax cu optimizare Alpha-Beta</a></li>
      <li class="quiz-button"><a href="quiz.php">Generare quiz-uri</a></li>
    </ul>
  </div>
</body>
</html>