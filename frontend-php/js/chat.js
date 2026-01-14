const USE_PROXY = true;
const API = "http://127.0.0.1:8000";

const chatBox = document.getElementById('chatBox');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const topicSelect = document.getElementById('topicSelect');
const matrixType = document.getElementById('matrixType');
const matrixRows = document.getElementById('matrixRows');
const matrixCols = document.getElementById('matrixCols');
const matrixBuildBtn = document.getElementById('matrixBuildBtn');
const matrixGrid = document.getElementById('matrixGrid');
const matrixInsertBtn = document.getElementById('matrixInsertBtn');
const matrixClearBtn = document.getElementById('matrixClearBtn');
const abDepth = document.getElementById('abDepth');
const abBranching = document.getElementById('abBranching');
const abBuildBtn = document.getElementById('abBuildBtn');
const abGrid = document.getElementById('abGrid');
const abInsertBtn = document.getElementById('abInsertBtn');
const abClearBtn = document.getElementById('abClearBtn');

function appendMessage(text, type, meta = null, sources = []) {
  const msg = document.createElement('div');
  msg.className = `message ${type}`;
  msg.textContent = text;

  if (meta) {
    const metaDiv = document.createElement('div');
    metaDiv.className = 'meta';
    metaDiv.textContent = meta;
    msg.appendChild(metaDiv);
  }

  if (sources.length > 0) {
    const srcDiv = document.createElement('div');
    srcDiv.className = 'sources';
    const list = sources.map((s) => `${s.topic_name || s.topic_id} • ${s.type}`).join(' | ');
    srcDiv.textContent = `Surse: ${list}`;
    msg.appendChild(srcDiv);
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function buildMatrixGrid() {
  if (!matrixGrid) return;
  const rows = Math.max(1, parseInt(matrixRows.value || '2', 10));
  const cols = Math.max(1, parseInt(matrixCols.value || '2', 10));
  matrixGrid.innerHTML = '';
  matrixGrid.style.gridTemplateColumns = `repeat(${cols}, 90px)`;

  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const input = document.createElement('input');
      input.className = 'matrix-cell';
      input.placeholder = matrixType.value === 'nash' ? 'a,b' : '0';
      input.dataset.row = r;
      input.dataset.col = c;
      matrixGrid.appendChild(input);
    }
  }
}

function clearMatrixGrid() {
  if (!matrixGrid) return;
  matrixGrid.innerHTML = '';
}

function readMatrixValues() {
  const rows = Math.max(1, parseInt(matrixRows.value || '2', 10));
  const cols = Math.max(1, parseInt(matrixCols.value || '2', 10));
  const values = [];
  for (let r = 0; r < rows; r += 1) {
    const rowVals = [];
    for (let c = 0; c < cols; c += 1) {
      const cell = matrixGrid.querySelector(`input[data-row="${r}"][data-col="${c}"]`);
      rowVals.push(cell ? cell.value.trim() : '');
    }
    values.push(rowVals);
  }
  return values;
}

function formatMatrixText() {
  const rows = Math.max(1, parseInt(matrixRows.value || '2', 10));
  const cols = Math.max(1, parseInt(matrixCols.value || '2', 10));
  const values = readMatrixValues();

  if (matrixType.value === 'nash') {
    const formatted = values.map((row) => {
      const rowFormatted = row.map((cell) => {
        const cleaned = cell || '0,0';
        const parts = cleaned.split(',').map((p) => p.trim());
        const a = parts[0] || '0';
        const b = parts[1] || '0';
        return `(${a},${b})`;
      });
      return `[${rowFormatted.join(', ')}]`;
    });
    return `Matricea payoff Nash (${rows}x${cols}): [${formatted.join(', ')}]`;
  }

  const formatted = values.map((row) => {
    const rowFormatted = row.map((cell) => (cell === '' ? '0' : cell));
    return `[${rowFormatted.join(', ')}]`;
  });
  return `Matrice numerică (${rows}x${cols}): [${formatted.join(', ')}]`;
}

function buildAlphaBetaGrid() {
  if (!abGrid) return;
  const depth = Math.max(1, parseInt(abDepth.value || '3', 10));
  const branching = Math.max(2, parseInt(abBranching.value || '2', 10));
  const leafCount = branching ** depth;
  abGrid.innerHTML = '';
  abGrid.style.gridTemplateColumns = 'repeat(8, 90px)';

  for (let i = 0; i < leafCount; i += 1) {
    const input = document.createElement('input');
    input.className = 'matrix-cell';
    input.placeholder = `L${i + 1}`;
    input.dataset.leaf = i;
    abGrid.appendChild(input);
  }
}

function clearAlphaBetaGrid() {
  if (!abGrid) return;
  abGrid.innerHTML = '';
}

function formatAlphaBetaText() {
  const depth = Math.max(1, parseInt(abDepth.value || '3', 10));
  const branching = Math.max(2, parseInt(abBranching.value || '2', 10));
  const leafCount = branching ** depth;
  const leaves = [];
  for (let i = 0; i < leafCount; i += 1) {
    const cell = abGrid.querySelector(`input[data-leaf="${i}"]`);
    const val = cell ? cell.value.trim() : '';
    leaves.push(val === '' ? '0' : val);
  }
  return `Alpha-Beta: depth=${depth}, branching=${branching}, leaves=[${leaves.join(', ')}]`;
}

async function loadTopics() {
  try {
    const url = USE_PROXY ? 'api/proxy_theory_topics.php' : `${API}/theory/topics`;
    const resp = await fetch(url);
    const data = await resp.json();
    if (data.topics && Array.isArray(data.topics)) {
      data.topics.forEach((topic) => {
        const option = document.createElement('option');
        option.value = topic.topic_id;
        option.textContent = topic.topic_name;
        topicSelect.appendChild(option);
      });
    }
  } catch (err) {
    console.error('Error loading topics:', err);
  }
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) {
    return;
  }

  appendMessage(text, 'user');
  chatInput.value = '';

  const payload = {
    question: text,
    topic_id: topicSelect.value || null,
    max_sources: 3
  };

  try {
    const url = USE_PROXY ? 'api/proxy_chat_ask.php' : `${API}/chat/ask`;
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (data.error) {
      appendMessage(`Eroare: ${data.error}`, 'ai');
      return;
    }

    const confidence = data.confidence !== undefined
      ? `Confidență: ${Math.round(data.confidence * 100)}% • Metodă: ${data.method || 'N/A'}`
      : null;

    appendMessage(data.answer || 'Nu am un răspuns clar.', 'ai', confidence, data.sources || []);
  } catch (err) {
    appendMessage(`Eroare: ${err.message}`, 'ai');
  }
}

matrixBuildBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  buildMatrixGrid();
});
matrixInsertBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  if (!matrixGrid || matrixGrid.children.length === 0) {
    buildMatrixGrid();
  }
  const text = formatMatrixText();
  chatInput.value = chatInput.value ? `${chatInput.value}\n${text}` : text;
});
matrixClearBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  clearMatrixGrid();
});
matrixType?.addEventListener('change', () => {
  if (matrixGrid && matrixGrid.children.length > 0) {
    buildMatrixGrid();
  }
});

abBuildBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  buildAlphaBetaGrid();
});
abInsertBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  if (!abGrid || abGrid.children.length === 0) {
    buildAlphaBetaGrid();
  }
  const text = formatAlphaBetaText();
  chatInput.value = chatInput.value ? `${chatInput.value}\n${text}` : text;
});
abClearBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  clearAlphaBetaGrid();
});
abDepth?.addEventListener('change', () => {
  if (abGrid && abGrid.children.length > 0) {
    buildAlphaBetaGrid();
  }
});
abBranching?.addEventListener('change', () => {
  if (abGrid && abGrid.children.length > 0) {
    buildAlphaBetaGrid();
  }
});

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

loadTopics();
buildMatrixGrid();
buildAlphaBetaGrid();

