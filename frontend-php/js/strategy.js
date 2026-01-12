const USE_PROXY = true;          
const API = "http://127.0.0.1:8000";

let currentPayload = null;

async function callGenerate(problemType, seed) {
  if (USE_PROXY) {
    const url = `api/proxy_strategy_generate.php?${problemType ? `problem_type=${problemType}&` : ''}${seed!==''?`seed=${seed}`:''}`;
    const r = await fetch(url);
    return await r.json();
  } else {
    const url = `${API}/problem1/generate?${problemType ? `problem_type=${problemType}&` : ''}${seed!==''?`seed=${seed}`:''}`;
    const r = await fetch(url);
    return await r.json();
  }
}

async function callGrade(payload, answer) {
  const body = JSON.stringify({ payload, answer });
  if (USE_PROXY) {
    const r = await fetch("api/proxy_strategy_grade.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body
    });
    return await r.json();
  } else {
    const r = await fetch(`${API}/problem1/grade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body
    });
    return await r.json();
  }
}

async function loadQuestion() {
  try {
    const problemTypeEl = document.getElementById("problemType");
    const seedEl = document.getElementById("seed");

    if (!problemTypeEl) {
      console.warn("Elements for generator not found, maybe in custom mode only.");
      return;
    }

    const problemType = problemTypeEl.value;
    const seed = seedEl.value;

    const q = await callGenerate(problemType, seed);
    currentPayload = q;
    
    const questionEl = document.getElementById("question");
    if (questionEl) {
      questionEl.textContent = q.question_text || "Eroare la generare";
      questionEl.style.background = "#1a202c";
      questionEl.style.color = "#e2e8f0";
    }
    
    const solutionEl = document.getElementById("solution");
    if (solutionEl) {
      solutionEl.textContent = q.solution?.explanation || "Soluția nu este disponibilă";
    }
    
    const answerEl = document.getElementById("answer");
    if (answerEl) {
      answerEl.value = "";
    }
    
    const resultEl = document.getElementById("result");
    if (resultEl) {
      resultEl.innerHTML = "";
    }
  } catch (error) {
    console.error("Error loading question:", error);
    alert("Eroare la generarea întrebării: " + error.message);
  }
}

async function gradeAnswer() {
  if (!currentPayload) {
    alert("Generează mai întâi o întrebare!");
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
  
  try {
    const result = await callGrade(currentPayload, answer);
    if (resultEl) {
      const score = result.score || 0;
      const feedback = result.feedback || "Fără feedback";
      const bgColor = score === 100 ? "#c6f6d5" : score > 0 ? "#feebc8" : "#fed7d7";
      resultEl.innerHTML = `
        <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: ${bgColor};">
          <strong>Scor: ${score}%</strong><br>
          ${feedback}
        </div>
      `;
    }
  } catch (error) {
    console.error("Error grading answer:", error);
    if (resultEl) {
      resultEl.innerHTML = `
        <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: #fed7d7; color: #742a2a;">
          <strong>Eroare:</strong> ${error.message}
        </div>
      `;
    }
    alert("Eroare la evaluarea răspunsului: " + error.message);
  }
}

function setMode(mode) {
  const solveSection = document.getElementById("solveSection");
  const customSection = document.getElementById("customSection");
  const modeBtns = document.querySelectorAll(".mode-btn");
  
  if (mode === "solve") {
    if (solveSection) solveSection.style.display = "block";
    if (customSection) customSection.style.display = "none";
    modeBtns.forEach(btn => {
      if (btn.dataset.mode === "solve") {
        btn.style.background = "#48bb78";
      } else {
        btn.style.background = "";
      }
    });
  } else {
    if (solveSection) solveSection.style.display = "none";
    if (customSection) customSection.style.display = "block";
    modeBtns.forEach(btn => {
      if (btn.dataset.mode === "custom") {
        btn.style.background = "#48bb78";
      } else {
        btn.style.background = "";
      }
    });
  }
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
async function loadCustomInstanceFromFile() {
  const fileInput = document.getElementById('customInstanceFile');
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
    const textarea = document.getElementById('customInstance');
    if (textarea) {
      textarea.value = content;
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

function initPage() {
  const genBtn = document.getElementById("genBtn");
  const gradeBtn = document.getElementById("gradeBtn");
  const modeBtns = document.querySelectorAll(".mode-btn");
  
  if (genBtn) {
    genBtn.addEventListener("click", loadQuestion);
  }
  
  if (gradeBtn) {
    gradeBtn.addEventListener("click", gradeAnswer);
  }
  
  modeBtns.forEach(btn => {
    btn.addEventListener("click", () => setMode(btn.dataset.mode));
  });
  
  // Set default mode
  setMode("solve");
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initPage);
} else {
  initPage();
}

