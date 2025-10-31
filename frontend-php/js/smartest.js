const USE_PROXY = true;          // true = chem PHP proxy (fără CORS); false = chem direct FastAPI
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
  const rows = document.getElementById("rows").value;
  const cols = document.getElementById("cols").value;
  const ensure = document.getElementById("ensure").value;
  const seed = document.getElementById("seed").value;
  const q = await callGenerate(rows, cols, ensure, seed);
  currentPayload = q;
  document.getElementById("question").textContent = q.question_text;
  document.getElementById("solution").textContent = q.solution.explanation;
  document.getElementById("result").innerHTML = "";
  document.getElementById("answer").value = "";
}

async function gradeAnswer() {
  if (!currentPayload) return;
  const answer = document.getElementById("answer").value.trim();
  const res = await callGrade(currentPayload, answer);
  document.getElementById("result").innerHTML = `<strong>Scor: ${res.score}%</strong><br>${res.feedback}`;
}

document.getElementById("genBtn").addEventListener("click", loadQuestion);
document.getElementById("gradeBtn").addEventListener("click", gradeAnswer);
window.addEventListener("DOMContentLoaded", loadQuestion);
