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
  
  try {
    const result = await callGrade(currentPayload, answer);
    const resultEl = document.getElementById("result");
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

