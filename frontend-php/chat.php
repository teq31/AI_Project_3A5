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
  <title>SmarTest — Chat AI</title>
  <link rel="stylesheet" href="css/style.css?v=8">
  <style>
    .chat-wrapper {
      max-width: 980px;
      margin: 120px auto 40px;
      background: rgba(255, 255, 255, 0.96);
      border-radius: 20px;
      padding: 24px 28px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    .chat-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
    }
    .chat-header h2 {
      margin: 0;
      color: #5a52d5;
      font-size: 1.6rem;
    }
    .matrix-helper {
      margin: 16px 0;
      padding: 14px;
      border-radius: 14px;
      background: #f3f2ff;
      border: 1px solid #e2e0ff;
    }
    .matrix-controls {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 10px;
    }
    .matrix-controls select,
    .matrix-controls input {
      padding: 6px 10px;
      border-radius: 8px;
      border: 1px solid #d9d9e3;
      font-size: 0.9rem;
      width: 120px;
    }
    .matrix-grid {
      display: grid;
      gap: 6px;
      margin: 8px 0 12px;
    }
    .matrix-cell {
      width: 90px;
      padding: 6px;
      border-radius: 6px;
      border: 1px solid #d9d9e3;
      font-size: 0.85rem;
    }
    .matrix-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .matrix-actions button {
      padding: 8px 12px;
      border-radius: 10px;
      border: none;
      background: #6c5ce7;
      color: white;
      font-weight: 600;
      cursor: pointer;
    }
    .matrix-actions button.secondary {
      background: #a29bfe;
    }
    .ab-helper {
      margin: 14px 0 8px;
      padding: 14px;
      border-radius: 14px;
      background: #f5fbff;
      border: 1px solid #d7eaff;
    }
    .ab-grid {
      display: grid;
      gap: 6px;
      margin: 8px 0 12px;
    }
    .chat-controls {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }
    .chat-controls select,
    .chat-controls input {
      padding: 8px 12px;
      border-radius: 10px;
      border: 1px solid #d9d9e3;
      font-size: 0.9rem;
    }
    .chat-box {
      height: 420px;
      overflow-y: auto;
      background: #f7f7fb;
      border-radius: 14px;
      padding: 16px;
      border: 1px solid #e5e5f3;
    }
    .message {
      margin: 10px 0;
      padding: 12px 14px;
      border-radius: 12px;
      max-width: 78%;
      line-height: 1.45;
      white-space: pre-wrap;
    }
    .message.user {
      margin-left: auto;
      background: #7767ff;
      color: white;
    }
    .message.ai {
      margin-right: auto;
      background: #e9e8ff;
      color: #2d2d3a;
    }
    .meta {
      margin-top: 6px;
      font-size: 0.85rem;
      color: #4b4b5c;
    }
    .sources {
      margin-top: 8px;
      font-size: 0.85rem;
      color: #4b4b5c;
    }
    .input-row {
      display: flex;
      gap: 10px;
      margin-top: 16px;
    }
    .input-row textarea {
      flex: 1;
      padding: 12px;
      border-radius: 12px;
      border: 1px solid #d9d9e3;
      resize: none;
      font-size: 1rem;
      min-height: 70px;
    }
    .input-row button {
      padding: 12px 18px;
      border-radius: 12px;
      border: none;
      background: #6c5ce7;
      color: white;
      font-weight: 600;
      cursor: pointer;
      min-width: 120px;
    }
    .input-row button:hover {
      background: #5848d6;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="chat-wrapper">
      <div class="chat-header">
        <h2>Chat AI — întrebări despre teorie</h2>
        <div class="chat-controls">
          <label for="topicSelect">Topic:</label>
          <select id="topicSelect">
            <option value="">Toate (aleatoriu)</option>
          </select>
        </div>
      </div>

      <div class="matrix-helper">
        <strong>Ajutor pentru matrici / date numerice</strong>
        <div class="matrix-controls">
          <label for="matrixType">Tip:</label>
          <select id="matrixType">
            <option value="nash">Matrice Nash (perechi a,b)</option>
            <option value="numeric">Matrice numerică</option>
          </select>
          <label for="matrixRows">Rânduri:</label>
          <input id="matrixRows" type="number" min="1" value="2">
          <label for="matrixCols">Coloane:</label>
          <input id="matrixCols" type="number" min="1" value="2">
          <button id="matrixBuildBtn">Generează grila</button>
        </div>
        <div id="matrixGrid" class="matrix-grid"></div>
        <div class="matrix-actions">
          <button id="matrixInsertBtn">Inserează în chat</button>
          <button id="matrixClearBtn" class="secondary">Șterge grila</button>
        </div>
      </div>

      <div class="ab-helper">
        <strong>Ajutor Alpha‑Beta / MinMax</strong>
        <div class="matrix-controls">
          <label for="abDepth">Adâncime:</label>
          <input id="abDepth" type="number" min="1" value="3">
          <label for="abBranching">Branching:</label>
          <input id="abBranching" type="number" min="2" value="2">
          <button id="abBuildBtn">Generează frunze</button>
        </div>
        <div id="abGrid" class="ab-grid"></div>
        <div class="matrix-actions">
          <button id="abInsertBtn">Inserează în chat</button>
          <button id="abClearBtn" class="secondary">Șterge frunze</button>
        </div>
      </div>

      <div id="chatBox" class="chat-box"></div>

      <div class="input-row">
        <textarea id="chatInput" placeholder="Scrie întrebarea ta..."></textarea>
        <button id="sendBtn">Trimite</button>
      </div>
    </div>
  </div>

  <script src="js/chat.js?v=1"></script>
</body>
</html>

