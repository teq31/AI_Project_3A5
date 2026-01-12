const USE_PROXY = true;          
const API = "http://127.0.0.1:8000";

let currentPayload = null;

async function callGenerate(rows, cols, ensure, seed) {
  if (USE_PROXY) {
    const url = `api/proxy_nash_generate.php?rows=${rows}&cols=${cols}&ensure=${ensure}${seed!==''?`&seed=${seed}`:''}`;
    const r = await fetch(url);
    return await r.json();
  } else {
    const url = `${API}/nash/generate?rows=${rows}&cols=${cols}&ensure=${ensure}${seed!==''?`&seed=${seed}`:''}`;
    const r = await fetch(url);
    return await r.json();
  }
}

async function callGrade(payload, answer) {
  const body = JSON.stringify({ payload, answer });
  if (USE_PROXY) {
    const r = await fetch("api/proxy_nash_grade.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body
    });
    return await r.json();
  } else {
    const r = await fetch(`${API}/nash/grade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body
    });
    return await r.json();
  }
}

async function loadQuestion() {
  try {
    const rowsEl = document.getElementById("rows");
    const colsEl = document.getElementById("cols");
    const ensureEl = document.getElementById("ensure");
    const seedEl = document.getElementById("seed");

    if (!rowsEl || !colsEl || !ensureEl) {
      console.warn("Elements for generator not found, maybe in custom mode only.");
      return;
    }

    const rows = rowsEl.value;
    const cols = colsEl.value;
    const ensure = ensureEl.value;
    const seed = seedEl ? seedEl.value : "";

    const q = await callGenerate(rows, cols, ensure, seed);
    currentPayload = q;

    const questionEl = document.getElementById("question");
    const solutionEl = document.getElementById("solution");
    const resultEl = document.getElementById("result");
    const answerEl = document.getElementById("answer");

    if (questionEl) questionEl.textContent = q.question_text || "";
    if (solutionEl) solutionEl.textContent = q.solution?.explanation || "";
    if (resultEl) resultEl.innerHTML = "";
    if (answerEl) answerEl.value = "";
  } catch (err) {
    console.error("Error loading question:", err);
    alert("Eroare la generarea întrebării: " + (err.message || err));
  }
}

async function gradeAnswer() {
  try {
    if (!currentPayload) {
      alert("Te rog generează mai întâi o întrebare!");
      return;
    }
    const answerEl = document.getElementById("answer");
    if (!answerEl) return;

    const answer = answerEl.value.trim();
    if (!answer) {
      alert("Te rog introdu un răspuns!");
      return;
    }

    // Show loading state
    const resultEl = document.getElementById("result");
    if (resultEl) {
      resultEl.innerHTML = `
        <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: #edf2ff; color: #434190; text-align: center;">
          ⏳ Se evaluează răspunsul...
        </div>
      `;
    }

    const res = await callGrade(currentPayload, answer);
    if (resultEl) {
      const score = res.score || 0;
      const feedback = res.feedback || "Fără feedback";
      const bgColor = score === 100 ? "#c6f6d5" : score > 0 ? "#feebc8" : "#fed7d7";
      resultEl.innerHTML = `
        <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: ${bgColor};">
          <strong>Scor: ${score}%</strong><br>
          ${feedback}
        </div>
      `;
    }
  } catch (err) {
    console.error("Error grading answer:", err);
    const resultEl = document.getElementById("result");
    if (resultEl) {
      resultEl.innerHTML = `
        <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: #fed7d7; color: #742a2a;">
          <strong>Eroare:</strong> ${err.message || err}
        </div>
      `;
    }
    alert("Eroare la evaluarea răspunsului: " + (err.message || err));
  }
}

function parseCustomMatrix(rows, cols, text) {
  const lines = text
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(l => l.length > 0);

  if (lines.length !== rows) {
    throw new Error(`Ai introdus ${lines.length} linii, dar ai specificat rows=${rows}.`);
  }

  const payoff1 = Array.from({ length: rows }, () => Array(cols).fill(0));
  const payoff2 = Array.from({ length: rows }, () => Array(cols).fill(0));

  for (let i = 0; i < rows; i++) {
    const line = lines[i];
    const cells = line
      .split(/\s+/)
      .map(c => c.trim())
      .filter(c => c.length > 0);

    if (cells.length !== cols) {
      throw new Error(`Pe linia ${i + 1} ai ${cells.length} celule, dar ai specificat cols=${cols}.`);
    }

    for (let j = 0; j < cols; j++) {
      let cell = cells[j];

      cell = cell.replace(/[()]/g, "");

      const parts = cell.split(",");
      if (parts.length !== 2) {
        throw new Error(`Celula (${i + 1},${j + 1}) nu e de forma a,b (ex: 2,1).`);
      }

      const a = Number(parts[0]);
      const b = Number(parts[1]);

      if (Number.isNaN(a) || Number.isNaN(b)) {
        throw new Error(`Valorile din celula (${i + 1},${j + 1}) trebuie să fie numere: "${cell}"`);
      }

      payoff1[i][j] = a;
      payoff2[i][j] = b;
    }
  }

  return { payoff1, payoff2 };
}

function findPureNashEquilibria(payoff1, payoff2) {
  const rows = payoff1.length;
  const cols = payoff1[0].length;

  const bestRowsForCol = Array.from({ length: cols }, () => []);
  const maxForCol = Array(cols).fill(-Infinity);

  for (let j = 0; j < cols; j++) {
    for (let i = 0; i < rows; i++) {
      const val = payoff1[i][j];
      if (val > maxForCol[j]) {
        maxForCol[j] = val;
        bestRowsForCol[j] = [i];
      } else if (val === maxForCol[j]) {
        bestRowsForCol[j].push(i);
      }
    }
  }

  const bestColsForRow = Array.from({ length: rows }, () => []);
  const maxForRow = Array(rows).fill(-Infinity);

  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const val = payoff2[i][j];
      if (val > maxForRow[i]) {
        maxForRow[i] = val;
        bestColsForRow[i] = [j];
      } else if (val === maxForRow[i]) {
        bestColsForRow[i].push(j);
      }
    }
  }

  const equilibria = [];

  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const a = payoff1[i][j];
      const b = payoff2[i][j];
      const isBestForP1 = (a === maxForCol[j]);
      const isBestForP2 = (b === maxForRow[i]);
      if (isBestForP1 && isBestForP2) {
        equilibria.push({ row: i, col: j, a, b });
      }
    }
  }

  let log = "";

  log += "Best responses pentru jucătorul 1 (pe coloane):\n";
  for (let j = 0; j < cols; j++) {
    const rowsList = bestRowsForCol[j].map(r => `R${r + 1}`).join(", ");
    log += `  Col C${j + 1}: max=${maxForCol[j]} la ${rowsList}\n`;
  }

  log += "\nBest responses pentru jucătorul 2 (pe linii):\n";
  for (let i = 0; i < rows; i++) {
    const colsList = bestColsForRow[i].map(c => `C${c + 1}`).join(", ");
    log += `  Row R${i + 1}: max=${maxForRow[i]} la ${colsList}\n`;
  }

  log += "\nProfiluri care sunt Nash (best response pentru amândoi):\n";
  if (equilibria.length === 0) {
    log += "  Niciun echilibru Nash în strategii pure.\n";
  } else {
    equilibria.forEach(eq => {
      log += `  (R${eq.row + 1}, C${eq.col + 1}) cu payoff (${eq.a}, ${eq.b})\n`;
    });
  }

  return { equilibria, log };
}

let customRowsInput,
  customColsInput,
  customMatrixInput,
  customHintEl,
  solveCustomNashBtn,
  customResultEl,
  customSolutionEl;

function initCustomNashExercise() {
  customRowsInput = document.getElementById("customRows");
  customColsInput = document.getElementById("customCols");
  customMatrixInput = document.getElementById("customMatrix");
  customHintEl = document.getElementById("customHint");
  solveCustomNashBtn = document.getElementById("solveCustomNashBtn");
  customResultEl = document.getElementById("customResult");
  customSolutionEl = document.getElementById("customSolution");

  if (!customRowsInput || !customColsInput || !customMatrixInput || !solveCustomNashBtn) {
    return;
  }

  function updateCustomHint() {
    const r = parseInt(customRowsInput.value, 10);
    const c = parseInt(customColsInput.value, 10);
    if (!Number.isNaN(r) && !Number.isNaN(c) && r >= 2 && c >= 2) {
      if (customHintEl) {
        customHintEl.textContent =
          `Trebuie să introduci ${r} linii, fiecare cu ${c} celule de forma a,b (ex: 2,1 0,0 3,4).`;
      }
    } else if (customHintEl) {
      customHintEl.textContent = "";
    }
  }

  customRowsInput.addEventListener("input", updateCustomHint);
  customColsInput.addEventListener("input", updateCustomHint);
  updateCustomHint();

  solveCustomNashBtn.addEventListener("click", () => {
    try {
      const r = parseInt(customRowsInput.value, 10);
      const c = parseInt(customColsInput.value, 10);
      if (Number.isNaN(r) || Number.isNaN(c) || r < 2 || c < 2) {
        if (customResultEl) {
          customResultEl.textContent = "Te rog completează corect rows și cols (minim 2).";
          customResultEl.style.color = "red";
        }
        return;
      }

      const text = customMatrixInput.value.trim();
      if (!text) {
        if (customResultEl) {
          customResultEl.textContent = "Te rog introdu matricea payoff-urilor.";
          customResultEl.style.color = "red";
        }
        return;
      }

      const { payoff1, payoff2 } = parseCustomMatrix(r, c, text);
      const { equilibria, log } = findPureNashEquilibria(payoff1, payoff2);

      if (equilibria.length === 0) {
        if (customResultEl) {
          customResultEl.textContent =
            "Nu există niciun echilibru Nash în strategii pure pentru jocul introdus.";
          customResultEl.style.color = "orange";
        }
      } else {
        const eqText = equilibria
          .map(eq => `R${eq.row + 1} C${eq.col + 1} (payoff ${eq.a},${eq.b})`)
          .join(" ; ");
        if (customResultEl) {
          customResultEl.textContent =
            `Echilibre Nash (strategii pure) găsite: ${eqText}`;
          customResultEl.style.color = "green";
        }
      }

      if (customSolutionEl) {
        customSolutionEl.textContent = log;
      }
    } catch (e) {
      console.error(e);
      if (customResultEl) {
        customResultEl.textContent =
          "Eroare la interpretarea jocului: " + (e.message || e);
        customResultEl.style.color = "red";
      }
      if (customSolutionEl) {
        customSolutionEl.textContent = "";
      }
    }
  });
}

// Funcție pentru încărcarea răspunsului din document
async function loadAnswerFromFile() {
  const fileInput = document.getElementById('answerFile');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Te rog selectează un fișier!');
    return;
  }
  
  try {
    let answer = '';
    
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      const answers = await processTextFile(file);
      answer = answers.length > 0 ? answers[0] : '';
    } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      const answers = await processPDFFile(file);
      answer = answers.length > 0 ? answers[0] : '';
    } else {
      alert('Format de fișier nesuportat! Te rog folosește .txt sau .pdf');
      return;
    }
    
    if (!answer) {
      alert('Nu s-a găsit niciun răspuns în document!');
      return;
    }
    
    // Actualizează input-ul cu răspunsul
    const answerInput = document.getElementById('answer');
    if (answerInput) {
      answerInput.value = answer;
      alert('Răspunsul a fost încărcat cu succes!');
    }
    
    // Resetează input-ul de fișier
    fileInput.value = '';
    
  } catch (error) {
    console.error('Eroare la procesarea fișierului:', error);
    alert('Eroare la procesarea fișierului: ' + error.message);
  }
}

// Procesare fișier text
function processTextFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        // Împarte pe linii și filtrează liniile goale
        const answers = text.split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0);
        resolve(answers);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => reject(new Error('Eroare la citirea fișierului'));
    reader.readAsText(file);
  });
}

// Procesare fișier PDF
async function processPDFFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      try {
        const arrayBuffer = e.target.result;
        
        // Verifică dacă PDF.js este disponibil
        const pdfjs = window.pdfjsLib || window.pdfjs;
        if (!pdfjs) {
          reject(new Error('PDF.js nu este încărcat! Te rog reîncarcă pagina.'));
          return;
        }
        
        // Configurează PDF.js worker
        pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
        
        const loadingTask = pdfjs.getDocument({ data: arrayBuffer });
        const pdf = await loadingTask.promise;
        
        let fullText = '';
        
        // Citește toate paginile
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
          const page = await pdf.getPage(pageNum);
          const textContent = await page.getTextContent();
          const pageText = textContent.items.map(item => item.str).join('\n');
          fullText += pageText + '\n';
        }
        
        // Împarte pe linii și filtrează liniile goale
        const answers = fullText.split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0);
        
        resolve(answers);
      } catch (error) {
        reject(new Error('Eroare la procesarea PDF: ' + error.message));
      }
    };
    
    reader.onerror = () => reject(new Error('Eroare la citirea fișierului PDF'));
    reader.readAsArrayBuffer(file);
  });
}

// Funcție pentru încărcarea documentului în secțiunea custom
async function loadCustomMatrixFromFile() {
  const fileInput = document.getElementById('customMatrixFile');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Te rog selectează un fișier!');
    return;
  }
  
  try {
    let content = '';
    
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      content = await processTextFileForCustom(file);
    } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      content = await processPDFFileForCustom(file);
    } else {
      alert('Format de fișier nesuportat! Te rog folosește .txt sau .pdf');
      return;
    }
    
    if (!content) {
      alert('Fișierul este gol!');
      return;
    }
    
    // Actualizează textarea-ul cu conținutul
    const textarea = document.getElementById('customMatrix');
    if (textarea) {
      textarea.value = content.trim();
      alert('Documentul a fost încărcat cu succes!');
    }
    
    // Resetează input-ul de fișier
    fileInput.value = '';
    
  } catch (error) {
    console.error('Eroare la procesarea fișierului:', error);
    alert('Eroare la procesarea fișierului: ' + error.message);
  }
}

// Procesare fișier text pentru custom (returnează întregul conținut)
function processTextFileForCustom(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        resolve(text);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => reject(new Error('Eroare la citirea fișierului'));
    reader.readAsText(file);
  });
}

// Procesare fișier PDF pentru custom (returnează întregul conținut)
async function processPDFFileForCustom(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      try {
        const arrayBuffer = e.target.result;
        
        // Verifică dacă PDF.js este disponibil
        const pdfjs = window.pdfjsLib || window.pdfjs;
        if (!pdfjs) {
          reject(new Error('PDF.js nu este încărcat! Te rog reîncarcă pagina.'));
          return;
        }
        
        // Configurează PDF.js worker
        pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
        
        const loadingTask = pdfjs.getDocument({ data: arrayBuffer });
        const pdf = await loadingTask.promise;
        
        let fullText = '';
        
        // Citește toate paginile
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
          const page = await pdf.getPage(pageNum);
          const textContent = await page.getTextContent();
          const pageText = textContent.items.map(item => item.str).join('\n');
          fullText += pageText + '\n';
        }
        
        resolve(fullText);
      } catch (error) {
        reject(new Error('Eroare la procesarea PDF: ' + error.message));
      }
    };
    
    reader.onerror = () => reject(new Error('Eroare la citirea fișierului PDF'));
    reader.readAsArrayBuffer(file);
  });
}

function setMode(mode) {
  const solveSection = document.getElementById("solveSection");
  const customSection = document.getElementById("customSection");
  const buttons = document.querySelectorAll(".mode-btn");

  if (!solveSection || !customSection) {
    return;
  }

  if (mode === "solve") {
    solveSection.style.display = "";
    customSection.style.display = "none";
  } else if (mode === "custom") {
    solveSection.style.display = "none";
    customSection.style.display = "";
  }

  buttons.forEach(btn => {
    if (btn.dataset.mode === mode) {
      btn.classList.add("active-mode");
    } else {
      btn.classList.remove("active-mode");
    }
  });
}

function initPage() {
  const genBtn = document.getElementById("genBtn");
  const gradeBtn = document.getElementById("gradeBtn");
  if (genBtn) genBtn.addEventListener("click", loadQuestion);
  if (gradeBtn) gradeBtn.addEventListener("click", gradeAnswer);

  initCustomNashExercise();

  const modeButtons = document.querySelectorAll(".mode-btn");
  modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode;
      setMode(mode);
    });
  });

  setMode("solve");

  if (genBtn) {
    loadQuestion();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initPage);
} else {
  initPage();
}
